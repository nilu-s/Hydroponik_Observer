import asyncio

from app import realtime_updates


def test_readings_capture_uses_value_interval_minutes(monkeypatch) -> None:
    inserted = []

    async def fake_run_periodic(name, interval_provider, work, min_sleep_sec=0.2):
        await work()
        await work()

    async def fake_fetch_live_reading(setup_id, node_id):
        return {"ts": None, "ph": 6.5, "ec": 1.2, "temp": 22.0, "status": ["ok"]}

    def fake_insert_reading(**kwargs):
        inserted.append(kwargs)

    times = iter([0, 61])

    monkeypatch.setattr(realtime_updates, "run_periodic", fake_run_periodic)
    monkeypatch.setattr(
        realtime_updates,
        "list_setups",
        lambda: [{"setup_id": "S1", "node_id": "N1", "value_interval_minutes": 1}],
    )
    monkeypatch.setattr(realtime_updates, "_fetch_live_reading", fake_fetch_live_reading)
    monkeypatch.setattr(realtime_updates, "insert_reading", fake_insert_reading)
    monkeypatch.setattr(realtime_updates.time, "time", lambda: next(times))

    asyncio.run(realtime_updates.readings_capture_loop())

    assert len(inserted) == 1
