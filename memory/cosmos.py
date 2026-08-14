import os
import uuid
from datetime import datetime, timezone
from dotenv import load_dotenv
from azure.cosmos import CosmosClient, PartitionKey

load_dotenv()


class ConversationMemory:
    def __init__(self):
        conn_str = os.getenv("COSMOS_CONNECTION_STRING")
        print(f"DEBUG COSMOS conn_str: {repr(conn_str)}", flush=True)
        db_name = os.getenv("COSMOS_DATABASE")
        container_name = os.getenv("COSMOS_CONTAINER")

        self.client = CosmosClient.from_connection_string(conn_str)
        self.database = self.client.create_database_if_not_exists(id=db_name)
        self.container = self.database.create_container_if_not_exists(
            id=container_name,
            partition_key=PartitionKey(path="/session_id"),
            offer_throughput=400
        )

    def add_message(self, session_id: str, role: str, content: str, sources: list[str] = None, user_id: str = None):
        """
        Stores a single message turn (user or assistant) tied to a session and user.
        """
        item = {
            "id": str(uuid.uuid4()),
            "session_id": session_id,
            "user_id": user_id,
            "role": role,
            "content": content,
            "sources": sources or [],
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        self.container.create_item(body=item)
        return item

    def get_history(self, session_id: str, user_id: str, limit: int = 50) -> list[dict]:
        """
        Returns all messages for a session, scoped to the requesting user, ordered oldest to newest.
        A user can only ever retrieve their own messages for a session, even if they
        somehow guess or reuse someone else's session_id.
        """
        query = "SELECT * FROM c WHERE c.session_id = @session_id AND c.user_id = @user_id ORDER BY c.timestamp ASC"
        params = [
            {"name": "@session_id", "value": session_id},
            {"name": "@user_id", "value": user_id}
        ]

        items = list(self.container.query_items(
            query=query,
            parameters=params,
            partition_key=session_id
        ))
        return items[-limit:]

    def get_recent_context(self, session_id: str, user_id: str, turns: int = 6) -> list[dict]:
        """
        Returns the last N messages (scoped to the user) formatted for feeding
        back into the LLM as chat history.
        """
        history = self.get_history(session_id, user_id)
        recent = history[-turns:]
        return [{"role": m["role"], "content": m["content"]} for m in recent]
