import asyncio
from collections import defaultdict
from pathlib import Path
import sys

import pytest
import pytest_asyncio

PROJECT_ROOT = Path(__file__).resolve().parents[3]
MOFOX_SRC_PATH = PROJECT_ROOT / "src"
if str(MOFOX_SRC_PATH) not in sys.path:
    sys.path.insert(0, str(MOFOX_SRC_PATH))

from kernel.concurrency.watchdog import Watchdog, TaskStatus, watch_task


@pytest_asyncio.fixture
async def watchdog():
    wd = Watchdog.get_instance()

    if wd._running:
        await wd.stop()

    for info in list(wd._tasks.values()):
        if not info.task.done():
            info.task.cancel()
            try:
                await info.task
            except asyncio.CancelledError:
                pass
            except Exception:
                pass
    wd._tasks.clear()
    wd._task_counter = 0
    wd._stats = defaultdict(int)
    wd._on_timeout_callbacks.clear()
    wd._on_error_callbacks.clear()
    wd._on_complete_callbacks.clear()
    wd.check_interval = 0.01
    wd.default_timeout = 0.05

    yield wd

    for info in list(wd._tasks.values()):
        if not info.task.done():
            info.task.cancel()
            try:
                await info.task
            except asyncio.CancelledError:
                pass
            except Exception:
                pass
    wd._tasks.clear()

    if wd._running:
        await wd.stop()


def test_get_instance_returns_singleton(watchdog):
    other = Watchdog.get_instance()
    assert other is watchdog


@pytest.mark.asyncio
async def test_register_task_success(watchdog):
    async def sample():
        await asyncio.sleep(0.01)
        return "done"

    task = asyncio.create_task(sample())
    task_id = watchdog.register_task(task, name="test_task", timeout=0.1, metadata={"foo": "bar"})

    await task
    task_info = watchdog.get_task_info(task_id)
    assert task_info is not None
    assert task_info.name == "test_task"
    assert task_info.status is TaskStatus.COMPLETED
    assert task_info.metadata["foo"] == "bar"


@pytest.mark.asyncio
async def test_timeout_handling_marks_and_cancels_task(watchdog):
    async def slow_job():
        await asyncio.sleep(0.2)

    watchdog.enable_timeout_check = True
    watchdog.check_interval = 0.01

    task = asyncio.create_task(slow_job())
    task_id = watchdog.register_task(task, name="slow_job", timeout=0.05)

    await watchdog.start()
    await asyncio.sleep(0.12)

    task_info = watchdog.get_task_info(task_id)
    assert task_info is not None
    assert watchdog._stats["total_timeout"] == 1
    assert task_info.status is TaskStatus.CANCELLED
    assert task.cancelled()

    await watchdog.stop()


@pytest.mark.asyncio
async def test_error_callback_triggered_on_failure(watchdog):
    received = []

    def on_error(task_id, info):
        received.append((task_id, info.status))

    watchdog.add_error_callback(on_error)

    async def failing_task():
        raise RuntimeError("boom")

    task = asyncio.create_task(failing_task())
    task_id = watchdog.register_task(task, name="failing_task")

    with pytest.raises(RuntimeError):
        await task

    task_info = watchdog.get_task_info(task_id)
    assert task_info is not None
    assert task_info.status is TaskStatus.FAILED
    assert received == [(task_id, TaskStatus.FAILED)]


@pytest.mark.asyncio
async def test_watch_task_helper_starts_monitor(watchdog):
    async def quick_job():
        await asyncio.sleep(0.01)
        return 42

    task, task_id = await watch_task(quick_job(), name="quick_job", timeout=0.1, auto_start=True)

    result = await task
    task_info = watchdog.get_task_info(task_id)

    assert result == 42
    assert task_info is not None
    assert task_info.status is TaskStatus.COMPLETED
    assert watchdog._running is True

    await watchdog.stop()
