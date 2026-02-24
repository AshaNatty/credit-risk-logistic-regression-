"""Long-term memory backed by SQLite."""
from __future__ import annotations

import json
import logging
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class SQLiteMemory:
    """Long-term persistent memory using SQLite."""

    def __init__(self, db_path: str = "data/audit.db"):
        self._db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _get_conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._get_conn() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS assessments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    request_id TEXT UNIQUE NOT NULL,
                    customer_id TEXT NOT NULL,
                    decision TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS audit_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    request_id TEXT NOT NULL,
                    agent TEXT NOT NULL,
                    action TEXT NOT NULL,
                    reasoning TEXT,
                    created_at TEXT NOT NULL
                )
                """
            )
            conn.commit()
        logger.info("SQLite database initialised at %s", self._db_path)

    def save_assessment(self, request_id: str, customer_id: str, decision: str, payload: Dict[str, Any]) -> None:
        with self._get_conn() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO assessments (request_id, customer_id, decision, payload, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (request_id, customer_id, decision, json.dumps(payload), datetime.now(timezone.utc).isoformat()),
            )
            conn.commit()

    def get_assessment(self, request_id: str) -> Optional[Dict[str, Any]]:
        with self._get_conn() as conn:
            row = conn.execute(
                "SELECT * FROM assessments WHERE request_id = ?", (request_id,)
            ).fetchone()
        if row:
            return dict(row)
        return None

    def log_audit(self, request_id: str, agent: str, action: str, reasoning: str) -> None:
        with self._get_conn() as conn:
            conn.execute(
                """
                INSERT INTO audit_logs (request_id, agent, action, reasoning, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (request_id, agent, action, reasoning, datetime.now(timezone.utc).isoformat()),
            )
            conn.commit()

    def get_audit_logs(self, request_id: str) -> List[Dict[str, Any]]:
        with self._get_conn() as conn:
            rows = conn.execute(
                "SELECT * FROM audit_logs WHERE request_id = ? ORDER BY created_at ASC",
                (request_id,),
            ).fetchall()
        return [dict(r) for r in rows]
