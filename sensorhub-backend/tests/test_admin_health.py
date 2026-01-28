import asyncio

from app.api import admin


def test_admin_health_shape(monkeypatch) -> None:
    class DummyManager:
        def get_health(self):
            return {"workerCount": 0, "subscriberCount": 0, "workers": []}

    async def run() -> None:
        monkeypatch.setattr(admin, "get_camera_worker_manager", lambda: DummyManager())
        monkeypatch.setattr(admin, "list_setups", lambda: [])
        monkeypatch.setattr(admin, "list_camera_devices", lambda: [])
        payload = await admin.get_health()
        assert payload["ok"] is True
        assert payload["workers"]["workerCount"] == 0
        assert payload["setups"]["count"] == 0
        assert payload["cameras"]["count"] == 0

    asyncio.run(run())
