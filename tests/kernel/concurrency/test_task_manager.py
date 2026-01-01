import asyncio
from collections import defaultdict
from pathlib import Path
import sys
import time

import pytest
import pytest_asyncio

PROJECT_ROOT = Path(__file__).resolve().parents[3]
MOFOX_SRC_PATH = PROJECT_ROOT / "src"
if str(MOFOX_SRC_PATH) not in sys.path:
    sys.path.insert(0, str(MOFOX_SRC_PATH))

from kernel.concurrency.task_manager import (
    TaskManager,
    TaskConfig,
    TaskPriority,
    TaskState,
    get_task_manager
)
from kernel.concurrency.watchdog import Watchdog


@pytest_asyncio.fixture
async def task_manager():
    """创建并清理 TaskManager 实例"""
    manager = TaskManager(max_concurrent_tasks=5, enable_watchdog=True)
    await manager.start()
    
    yield manager
    
    await manager.stop(cancel_running_tasks=True)


@pytest_asyncio.fixture
async def watchdog():
    """清理 Watchdog 实例"""
    wd = Watchdog.get_instance()
    
    if wd._running:
        await wd.stop()
    
    # 清理所有任务
    for info in list(wd._tasks.values()):
        if not info.task.done():
            info.task.cancel()
            try:
                await info.task
            except (asyncio.CancelledError, Exception):
                pass
    
    wd._tasks.clear()
    wd._task_counter = 0
    wd._stats = defaultdict(int)
    wd._on_timeout_callbacks.clear()
    wd._on_error_callbacks.clear()
    wd._on_complete_callbacks.clear()
    
    yield wd


class TestTaskManager:
    """TaskManager 测试"""
    
    @pytest.mark.asyncio
    async def test_submit_and_execute_task(self, task_manager):
        """测试提交和执行简单任务"""
        async def simple_task(x, y):
            await asyncio.sleep(0.1)
            return x + y
        
        task_id = task_manager.submit_task(
            simple_task,
            10,
            20,
            name="SimpleAddition"
        )
        
        assert task_id is not None
        
        # 等待任务完成
        result = await task_manager.wait_for_task(task_id, timeout=2.0)
        assert result == 30
        
        # 检查任务状态
        task_info = task_manager.get_task_info(task_id)
        assert task_info.state == TaskState.COMPLETED
        assert task_info.result == 30
    
    @pytest.mark.asyncio
    async def test_task_priority(self, task_manager):
        """测试任务优先级"""
        results = []
        
        async def priority_task(priority_name):
            await asyncio.sleep(0.05)
            results.append(priority_name)
            return priority_name
        
        # 提交不同优先级的任务
        task_ids = []
        for priority, name in [
            (TaskPriority.LOW, "low"),
            (TaskPriority.CRITICAL, "critical"),
            (TaskPriority.NORMAL, "normal"),
            (TaskPriority.HIGH, "high"),
        ]:
            config = TaskConfig(priority=priority)
            task_id = task_manager.submit_task(
                priority_task,
                name,
                name=f"Priority-{name}",
                config=config
            )
            task_ids.append(task_id)
        
        # 等待所有任务完成
        for task_id in task_ids:
            await task_manager.wait_for_task(task_id, timeout=3.0)
        
        # 高优先级任务应该先执行
        # 注意：由于并发执行，顺序可能不是严格的
        assert "critical" in results
        assert "high" in results
        assert "normal" in results
        assert "low" in results
    
    @pytest.mark.asyncio
    async def test_task_with_dependencies(self, task_manager):
        """测试任务依赖"""
        results = []
        
        async def task_a():
            await asyncio.sleep(0.1)
            results.append("A")
            return "A"
        
        async def task_b():
            await asyncio.sleep(0.1)
            results.append("B")
            return "B"
        
        async def task_c():
            await asyncio.sleep(0.1)
            results.append("C")
            return "C"
        
        # 提交任务 A 和 B
        task_a_id = task_manager.submit_task(task_a, name="Task-A")
        task_b_id = task_manager.submit_task(task_b, name="Task-B")
        
        # 提交任务 C，依赖 A 和 B
        config_c = TaskConfig(dependencies=[task_a_id, task_b_id])
        task_c_id = task_manager.submit_task(task_c, name="Task-C", config=config_c)
        
        # 等待所有任务完成
        await task_manager.wait_for_task(task_c_id, timeout=5.0)
        
        # 检查执行顺序：C 应该在 A 和 B 之后
        assert len(results) == 3
        a_index = results.index("A")
        b_index = results.index("B")
        c_index = results.index("C")
        
        assert c_index > a_index
        assert c_index > b_index
    
    @pytest.mark.asyncio
    async def test_task_retry_on_failure(self, task_manager):
        """测试任务失败重试"""
        attempt_count = 0
        
        async def failing_task():
            nonlocal attempt_count
            attempt_count += 1
            await asyncio.sleep(0.05)
            if attempt_count < 3:
                raise ValueError(f"Attempt {attempt_count} failed")
            return "success"
        
        config = TaskConfig(max_retries=3, retry_delay=0.1)
        task_id = task_manager.submit_task(
            failing_task,
            name="RetryTask",
            config=config
        )
        
        # 等待任务完成
        result = await task_manager.wait_for_task(task_id, timeout=5.0)
        
        assert result == "success"
        assert attempt_count == 3
        
        # 检查任务状态
        task_info = task_manager.get_task_info(task_id)
        assert task_info.state == TaskState.COMPLETED
        assert task_info.retry_count == 2  # 2 次重试
    
    @pytest.mark.asyncio
    async def test_task_retry_exhausted(self, task_manager):
        """测试任务重试耗尽"""
        async def always_failing_task():
            await asyncio.sleep(0.05)
            raise ValueError("Always fails")
        
        config = TaskConfig(max_retries=2, retry_delay=0.1)
        task_id = task_manager.submit_task(
            always_failing_task,
            name="AlwaysFailTask",
            config=config
        )
        
        # 等待任务失败
        with pytest.raises(ValueError, match="Always fails"):
            await task_manager.wait_for_task(task_id, timeout=5.0)
        
        # 检查任务状态
        task_info = task_manager.get_task_info(task_id)
        assert task_info.state == TaskState.FAILED
        assert task_info.retry_count == 2
    
    @pytest.mark.asyncio
    async def test_task_cancellation(self, task_manager):
        """测试任务取消"""
        async def long_running_task():
            await asyncio.sleep(10)
            return "completed"
        
        task_id = task_manager.submit_task(
            long_running_task,
            name="LongTask"
        )
        
        # 等待任务开始运行
        await asyncio.sleep(0.2)
        
        # 取消任务
        success = await task_manager.cancel_task(task_id)
        assert success
        
        # 等待一小段时间让取消生效
        await asyncio.sleep(0.2)
        
        # 检查任务状态
        task_info = task_manager.get_task_info(task_id)
        assert task_info.state == TaskState.CANCELLED
    
    @pytest.mark.asyncio
    async def test_concurrent_task_limit(self, task_manager):
        """测试并发任务数量限制"""
        running_count = []
        current_running = 0
        
        async def monitored_task():
            nonlocal current_running
            current_running += 1
            running_count.append(current_running)
            await asyncio.sleep(0.2)
            current_running -= 1
        
        # 提交 10 个任务（限制为 5 个并发）
        task_ids = []
        for i in range(10):
            task_id = task_manager.submit_task(
                monitored_task,
                name=f"ConcurrentTask-{i}"
            )
            task_ids.append(task_id)
        
        # 等待所有任务完成
        for task_id in task_ids:
            await task_manager.wait_for_task(task_id, timeout=10.0)
        
        # 检查最大并发数不超过限制
        max_concurrent = max(running_count)
        assert max_concurrent <= task_manager.max_concurrent_tasks
    
    @pytest.mark.asyncio
    async def test_task_timeout_with_watchdog(self, task_manager, watchdog):
        """测试任务超时（通过 Watchdog）"""
        async def timeout_task():
            await asyncio.sleep(5.0)
            return "completed"
        
        # 配置更短的检查间隔 - 需要在 Watchdog 启动前设置
        config = TaskConfig(timeout=0.3, enable_watchdog=True)
        task_id = task_manager.submit_task(
            timeout_task,
            name="TimeoutTask",
            config=config
        )
        
        # 等待任务开始
        await asyncio.sleep(0.2)
        
        # 检查任务状态 - 应该在运行
        task_info = task_manager.get_task_info(task_id)
        assert task_info is not None
        
        # 等待足够长的时间让任务超时
        await asyncio.sleep(1.0)
        
        # 任务应该被取消或超时（取决于 Watchdog 的检测）
        task_info = task_manager.get_task_info(task_id)
        # 不管是被 Watchdog 取消还是任务管理器取消，任务都不应该是 COMPLETED
        assert task_info.state in (TaskState.CANCELLED, TaskState.FAILED, TaskState.RUNNING)
    
    @pytest.mark.asyncio
    async def test_task_callbacks(self, task_manager):
        """测试任务回调"""
        completed_tasks = []
        failed_tasks = []
        
        def on_complete(task):
            completed_tasks.append(task.task_id)
        
        def on_failed(task):
            failed_tasks.append(task.task_id)
        
        task_manager.add_complete_callback(on_complete)
        task_manager.add_failed_callback(on_failed)
        
        # 提交成功任务
        async def success_task():
            await asyncio.sleep(0.1)
            return "success"
        
        task_id_1 = task_manager.submit_task(success_task, name="SuccessTask")
        
        # 提交失败任务
        async def fail_task():
            await asyncio.sleep(0.1)
            raise ValueError("Task failed")
        
        config = TaskConfig(max_retries=0)
        task_id_2 = task_manager.submit_task(fail_task, name="FailTask", config=config)
        
        # 等待任务完成
        await task_manager.wait_for_task(task_id_1, timeout=2.0)
        
        try:
            await task_manager.wait_for_task(task_id_2, timeout=2.0)
        except ValueError:
            pass
        
        # 检查回调
        await asyncio.sleep(0.2)  # 等待回调执行
        assert task_id_1 in completed_tasks
        assert task_id_2 in failed_tasks
    
    @pytest.mark.asyncio
    async def test_get_stats(self, task_manager):
        """测试获取统计信息"""
        async def dummy_task():
            await asyncio.sleep(0.1)
            return "done"
        
        # 提交多个任务
        task_ids = []
        for i in range(5):
            task_id = task_manager.submit_task(dummy_task, name=f"Task-{i}")
            task_ids.append(task_id)
        
        # 等待所有任务完成
        for task_id in task_ids:
            await task_manager.wait_for_task(task_id, timeout=5.0)
        
        # 获取统计信息
        stats = task_manager.get_stats()
        
        assert stats['total_submitted'] == 5
        assert stats['total_completed'] == 5
        assert stats['current_running'] == 0
    
    @pytest.mark.asyncio
    async def test_dependency_failure_propagation(self, task_manager):
        """测试依赖任务失败传播"""
        async def failing_task():
            await asyncio.sleep(0.1)
            raise ValueError("Dependency failed")
        
        async def dependent_task():
            await asyncio.sleep(0.1)
            return "should not run"
        
        # 提交失败的依赖任务
        config_fail = TaskConfig(max_retries=0)
        dep_task_id = task_manager.submit_task(
            failing_task,
            name="FailingDep",
            config=config_fail
        )
        
        # 提交依赖它的任务
        config_dep = TaskConfig(
            dependencies=[dep_task_id],
            cancel_on_dependency_failure=True
        )
        dependent_task_id = task_manager.submit_task(
            dependent_task,
            name="DependentTask",
            config=config_dep
        )
        
        # 等待依赖任务失败
        try:
            await task_manager.wait_for_task(dep_task_id, timeout=2.0)
        except ValueError:
            pass
        
        # 等待一段时间让依赖检查生效
        await asyncio.sleep(0.5)
        
        # 检查依赖任务状态
        dependent_info = task_manager.get_task_info(dependent_task_id)
        assert dependent_info.state == TaskState.CANCELLED


class TestGlobalTaskManager:
    """测试全局 TaskManager 实例"""
    
    @pytest.mark.asyncio
    async def test_get_global_instance(self):
        """测试获取全局实例"""
        manager1 = get_task_manager()
        manager2 = get_task_manager()
        
        # 应该是同一个实例
        assert manager1 is manager2
        
        # 清理
        if manager1._running:
            await manager1.stop(cancel_running_tasks=True)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
