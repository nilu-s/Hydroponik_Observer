from app import db


def _init_temp_db(monkeypatch, tmp_path) -> None:
    db.close_connections()
    test_db = tmp_path / "sensorhub.db"
    monkeypatch.setattr(db, "DB_PATH", test_db)
    db.init_db(reset=True)


def test_migrate_node_id_updates_references(monkeypatch, tmp_path) -> None:
    _init_temp_db(monkeypatch, tmp_path)
    with db._get_conn() as conn:
        conn.execute(
            """
            INSERT INTO nodes (node_id, name, kind, status, last_error)
            VALUES (?, ?, ?, ?, ?)
            """,
            ("COM3", "Legacy", "real", "offline", None),
        )
        conn.execute(
            """
            INSERT INTO calibration (node_id, calib_version, calib_hash, payload_json, updated_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            ("COM3", 1, "hash", "{}", 123),
        )
        conn.execute(
            """
            INSERT INTO setups (
                setup_id, name, node_id, camera_id,
                value_interval_minutes, photo_interval_minutes,
                created_at
            ) VALUES (?, ?, ?, NULL, ?, ?, ?)
            """,
            ("S1", "Setup 1", "COM3", 10, 20, 111),
        )
        conn.execute(
            """
            INSERT INTO readings (setup_id, node_id, ts, ph, ec, temp, status_json)
            VALUES (?, ?, ?, NULL, NULL, NULL, ?)
            """,
            ("S1", "COM3", 999, "[]"),
        )

    db.migrate_node_id("COM3", "uid1234")

    assert db.get_setup("S1")["node_id"] == "uid1234"
    assert db.get_calibration("uid1234") is not None
    assert db.get_calibration("COM3") is None

    with db._get_conn() as conn:
        readings = conn.execute(
            "SELECT node_id FROM readings WHERE setup_id = ?",
            ("S1",),
        ).fetchall()
    assert readings[0][0] == "uid1234"


def test_migrate_node_id_merges_existing_uid(monkeypatch, tmp_path) -> None:
    _init_temp_db(monkeypatch, tmp_path)
    with db._get_conn() as conn:
        conn.execute(
            "INSERT INTO nodes (node_id, name, kind, status, last_error) VALUES (?, ?, ?, ?, ?)",
            ("uid1234", "New", "real", "online", None),
        )
        conn.execute(
            "INSERT INTO nodes (node_id, name, kind, status, last_error) VALUES (?, ?, ?, ?, ?)",
            ("COM3", "Old", "real", "offline", None),
        )
        conn.execute(
            """
            INSERT INTO setups (
                setup_id, name, node_id, camera_id,
                value_interval_minutes, photo_interval_minutes,
                created_at
            ) VALUES (?, ?, ?, NULL, ?, ?, ?)
            """,
            ("S1", "Setup 1", "COM3", 10, 20, 111),
        )

    db.migrate_node_id("COM3", "uid1234")

    assert db.get_setup("S1")["node_id"] == "uid1234"
    assert db.get_node("uid1234") is not None
    assert db.get_node("COM3") is None
