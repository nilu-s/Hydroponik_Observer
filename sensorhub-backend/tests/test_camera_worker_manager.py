import asyncio

from app.camera_worker_manager import CameraWorkerManager


class DummyProcess:
    def __init__(self) -> None:
        self._terminated = False

    def poll(self):
        return None if not self._terminated else 0

    def terminate(self):
        self._terminated = True

    def wait(self, timeout=None):
        return 0

    def kill(self):
        self._terminated = True


def test_camera_worker_manager_reuses_worker(monkeypatch) -> None:
    manager = CameraWorkerManager()
    opened = {"count": 0}

    def open_worker(device_id: str):
        opened["count"] += 1
        return DummyProcess()

    async def pump_frames(device_id: str, process: DummyProcess) -> None:
        return None

    monkeypatch.setattr(manager, "_open_worker_process", open_worker)
    monkeypatch.setattr(manager, "_pump_frames", pump_frames)

    async def run() -> None:
        queue1 = await manager.subscribe("dev-1")
        queue2 = await manager.subscribe("dev-1")
        assert opened["count"] == 1
        health = manager.get_health()
        assert health["workerCount"] == 1
        await manager.unsubscribe("dev-1", queue1)
        await manager.unsubscribe("dev-1", queue2)

    asyncio.run(run())
