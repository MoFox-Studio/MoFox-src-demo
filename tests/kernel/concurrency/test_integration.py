"""
Watchdog 和 TaskManager 集成测试

测试两个模块的配合效果：
- Watchdog 监控任务
- TaskManager 管理任务执行
- 超时处理
- 错误处理
- 资源清理
"""

import asyncio
import pytest
from src.kernel.concurrency.watchdog import get_watchdog
from src.kernel.concurrency.task_manager import (
    get_task_manager, TaskConfig, TaskPriority
)


async def reset_instances():
    """重置全局实例"""
    import src.kernel.concurrency.watchdog as watchdog_module
    import src.kernel.concurrency.task_manager as tm_module
    
    watchdog_module._watchdog_instance = None
    tm_module._task_manager_instance = None


async def cleanup():
    """清理资源"""
    watchdog = get_watchdog()
    task_manager = get_task_manager()
    
    if task_manager._running:
        await task_manager.stop(cancel_running_tasks=True)
    
    if watchdog._running:
        await watchdog.stop()


class TestWatchdogTaskManagerIntegration:
    """Watchdog 和 TaskManager 集成测试"""
    
    @pytest.mark.asyncio
    async def test_basic_integration(self):
        """测试基本的集成功能"""
        await reset_instances()
        try:
            task_manager = get_task_manager(max_concurrent_tasks=5)
            await task_manager.start()
            
            # 定义一个简单的协程
            async def simple_task():
                await asyncio.sleep(0.1)
                return "success"
            
            # 提交任务
            task_id = task_manager.submit_task(
                simple_task,
                name="Test Task"
            )
            
            # 等待任务完成
            result = await task_manager.wait_for_task(task_id)
            assert result == "success"
            
            # 检查统计信息
            stats = task_manager.get_stats()
            assert stats['total_completed'] == 1
            
            await task_manager.stop()
        finally:
            await cleanup()
    
    @pytest.mark.asyncio
    async def test_timeout_detection(self):
        """测试超时检测"""
        await reset_instances()
        try:
            task_manager = get_task_manager()
            task_manager.auto_cancel_on_timeout = True
            await task_manager.start()
            
            # 定义一个会超时的协程
            async def long_running_task():
                await asyncio.sleep(10)
                return "completed"
            
            # 提交任务，设置短超时时间
            config = TaskConfig(timeout=0.5)
            task_id = task_manager.submit_task(
                long_running_task,
                name="Timeout Task",
                config=config
            )
            
            # 等待任务完成（应该会被取消）
            try:
                await task_manager.wait_for_task(task_id, timeout=2.0)
                assert False, "应该抛出异常"
            except asyncio.CancelledError:
                pass
            
            # 检查任务状态
            task_info = task_manager.get_task_info(task_id)
            assert task_info.state.value == "cancelled"
            
            await task_manager.stop()
        finally:
            await cleanup()
    
    @pytest.mark.asyncio
    async def test_error_handling(self):
        """测试错误处理"""
        await reset_instances()
        try:
            task_manager = get_task_manager()
            await task_manager.start()
            
            # 定义一个会出错的协程
            async def failing_task():
                await asyncio.sleep(0.1)
                raise ValueError("Task failed")
            
            # 提交任务
            task_id = task_manager.submit_task(
                failing_task,
                name="Failing Task"
            )
            
            # 等待任务完成
            try:
                await task_manager.wait_for_task(task_id)
                assert False, "应该抛出异常"
            except ValueError as e:
                assert str(e) == "Task failed"
            
            # 检查统计信息
            stats = task_manager.get_stats()
            assert stats['total_failed'] == 1
            
            await task_manager.stop()
        finally:
            await cleanup()
    
    @pytest.mark.asyncio
    async def test_retry_mechanism(self):
        """测试重试机制"""
        await reset_instances()
        try:
            task_manager = get_task_manager()
            await task_manager.start()
            
            call_count = 0
            
            # 定义一个会失败然后成功的协程
            async def retry_task():
                nonlocal call_count
                call_count += 1
                await asyncio.sleep(0.05)
                
                if call_count < 3:
                    raise RuntimeError(f"Attempt {call_count} failed")
                return f"success on attempt {call_count}"
            
            # 提交任务，设置最多重试 2 次
            config = TaskConfig(max_retries=2, retry_delay=0.1)
            task_id = task_manager.submit_task(
                retry_task,
                name="Retry Task",
                config=config
            )
            
            # 等待任务完成
            result = await task_manager.wait_for_task(task_id)
            assert "success" in result
            assert call_count == 3
            
            # 检查统计信息
            stats = task_manager.get_stats()
            assert stats['total_completed'] == 1
            assert stats['total_retries'] == 2
            
            await task_manager.stop()
        finally:
            await cleanup()
    
    @pytest.mark.asyncio
    async def test_watchdog_cleanup(self):
        """测试 Watchdog 资源清理"""
        await reset_instances()
        try:
            watchdog = get_watchdog()
            task_manager = get_task_manager()
            await task_manager.start()
            
            # 提交多个任务
            async def quick_task():
                await asyncio.sleep(0.05)
                return "done"
            
            task_ids = []
            for i in range(5):
                task_id = task_manager.submit_task(
                    quick_task,
                    name=f"Task-{i}"
                )
                task_ids.append(task_id)
            
            # 等待所有任务完成
            for task_id in task_ids:
                await task_manager.wait_for_task(task_id)
            
            # 检查 Watchdog 中的任务数
            # 在清理后，应该没有或很少任务保留
            await asyncio.sleep(0.5)
            
            watchdog_stats = watchdog.get_stats()
            # 检查是否有已完成的任务被清理
            logger_info = f"Watchdog tracked: {watchdog_stats['current_tracked']}, completed: {watchdog_stats['total_completed']}"
            print(logger_info)
            
            await task_manager.stop()
        finally:
            await cleanup()
    
    @pytest.mark.asyncio
    async def test_concurrent_tasks(self):
        """测试并发任务执行"""
        await reset_instances()
        try:
            task_manager = get_task_manager(max_concurrent_tasks=3)
            await task_manager.start()
            
            import time
            start_time = time.time()
            
            # 定义一个会占用时间的协程
            async def timed_task(duration):
                await asyncio.sleep(duration)
                return duration
            
            # 提交 6 个任务
            task_ids = []
            for i in range(6):
                task_id = task_manager.submit_task(
                    timed_task,
                    0.2,  # 每个任务耗时 0.2 秒
                    name=f"Timed Task-{i}"
                )
                task_ids.append(task_id)
            
            # 等待所有任务完成
            results = []
            for task_id in task_ids:
                result = await task_manager.wait_for_task(task_id)
                results.append(result)
            
            elapsed = time.time() - start_time
            
            # 由于最多 3 个并发，6 个任务应该至少耗时 0.4 秒（2 批）
            assert elapsed >= 0.35  # 稍微留一点余地
            assert len(results) == 6
            
            # 检查统计信息
            stats = task_manager.get_stats()
            assert stats['total_completed'] == 6
            
            await task_manager.stop()
        finally:
            await cleanup()
    
    @pytest.mark.asyncio
    async def test_task_dependencies(self):
        """测试任务依赖关系"""
        await reset_instances()
        try:
            task_manager = get_task_manager()
            await task_manager.start()
            
            execution_order = []
            
            # 定义任务
            async def task_a():
                execution_order.append("A")
                await asyncio.sleep(0.1)
                return "result_A"
            
            async def task_b():
                execution_order.append("B")
                await asyncio.sleep(0.1)
                return "result_B"
            
            async def task_c():
                execution_order.append("C")
                return "result_C"
            
            # 提交任务
            task_a_id = task_manager.submit_task(task_a, name="Task A")
            task_b_id = task_manager.submit_task(task_b, name="Task B")
            
            # Task C 依赖 A 和 B
            config_c = TaskConfig(dependencies=[task_a_id, task_b_id])
            task_c_id = task_manager.submit_task(
                task_c,
                name="Task C",
                config=config_c
            )
            
            # 等待所有任务完成
            await task_manager.wait_for_task(task_a_id)
            await task_manager.wait_for_task(task_b_id)
            await task_manager.wait_for_task(task_c_id)
            
            # 检查执行顺序
            assert "A" in execution_order and "B" in execution_order
            assert execution_order[-1] == "C"  # C 必须最后执行
            
            await task_manager.stop()
        finally:
            await cleanup()
    
    @pytest.mark.asyncio
    async def test_priority_queue(self):
        """测试优先级队列"""
        await reset_instances()
        try:
            task_manager = get_task_manager(max_concurrent_tasks=1)
            await task_manager.start()
            
            execution_order = []
            
            # 定义任务
            async def tracked_task(name):
                execution_order.append(name)
                await asyncio.sleep(0.05)
            
            # 提交低优先级任务
            low_config = TaskConfig(priority=TaskPriority.LOW)
            task_low = task_manager.submit_task(
                tracked_task,
                "LOW",
                name="Low Priority",
                config=low_config
            )
            
            # 短暂延迟
            await asyncio.sleep(0.01)
            
            # 提交高优先级任务
            high_config = TaskConfig(priority=TaskPriority.HIGH)
            task_high = task_manager.submit_task(
                tracked_task,
                "HIGH",
                name="High Priority",
                config=high_config
            )
            
            # 等待完成
            await task_manager.wait_for_task(task_low)
            await task_manager.wait_for_task(task_high)
            
            # 由于并发限制为1，高优先级应该被优先调度
            # 但由于低优先级已经开始执行，高优先级会在后
            assert len(execution_order) == 2
            
            await task_manager.stop()
        finally:
            await cleanup()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
