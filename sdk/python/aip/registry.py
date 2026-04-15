"""
AIP Network Registries.

Decentralized physical or memory mappings charting exact capability boundaries across nodes.
"""

from typing import Any
import sqlite3
import json
import os

class AgentRegistry:
    """
    An in-memory town square. 
    Where local process agents announce their presence natively.
    """
    def __init__(self):
        self.agents: dict[str, Any] = {}

    def register(self, agent: Any) -> None:
        self.agents[agent.id] = agent

    def find(self, capability: str) -> list[Any]:
        return [a for a in self.agents.values() if capability in a.capabilities]

    def get(self, agent_id: str) -> Any | None:
        return self.agents.get(agent_id)


class SQLiteAgentRegistry:
    """
    A persistent mapping boundary letting dynamically distributed python systems smoothly 
    discover interacting physical nodes scaling across SQLite architectures perfectly locally!
    """
    def __init__(self, db_path: str = "aip_network.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS network (
                    agent_id TEXT PRIMARY KEY,
                    capabilities TEXT,
                    public_key TEXT,
                    endpoint_url TEXT
                )
            ''')
            
    def register(self, agent: Any, endpoint_url: str = "") -> None:
        caps = json.dumps(agent.capabilities)
        pub = getattr(agent, "public_key", "")
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO network (agent_id, capabilities, public_key, endpoint_url) VALUES (?, ?, ?, ?)",
                (agent.id, caps, pub, endpoint_url)
            )
            
    def find(self, capability: str) -> list[dict]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT agent_id, capabilities, public_key, endpoint_url FROM network")
            results = []
            for row in cursor:
                caps = json.loads(row[1])
                if capability in caps:
                    results.append({"id": row[0], "capabilities": caps, "public_key": row[2], "url": row[3]})
            return results

    def get_url(self, agent_id: str) -> str | None:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT endpoint_url FROM network WHERE agent_id = ?", (agent_id,))
            row = cursor.fetchone()
            return row[0] if row else None
