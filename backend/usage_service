from azure.cosmos import CosmosClient
import os
from dotenv import load_dotenv
from datetime import datetime, timezone

load_dotenv()


class UsageService:
    def __init__(self):
        conn_str = os.getenv("COSMOS_CONNECTION_STRING")
        db_name = os.getenv("COSMOS_DATABASE")
        container_name = os.getenv("COSMOS_CONTAINER")  # reuse "conversations"

        self.client = CosmosClient.from_connection_string(conn_str)
        self.database = self.client.get_database_client(db_name)
        self.container = self.database.get_container_client(container_name)

    def log_usage(self, session_id: str, user_id: str, tokens_used: int):
        item = {
            "id": f"usage-{session_id}-{datetime.now(timezone.utc).timestamp()}",
            "session_id": session_id,   # matches the partition key, so no extra RU cost
            "type": "usage",
            "user_id": user_id,
            "tokens_used": tokens_used,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        self.container.create_item(body=item)

    def get_session_total(self, session_id: str) -> int:
        query = "SELECT VALUE SUM(c.tokens_used) FROM c WHERE c.session_id = @session_id AND c.type = 'usage'"
        params = [{"name": "@session_id", "value": session_id}]
        result = list(self.container.query_items(query=query, parameters=params, partition_key=session_id))
        return result[0] if result and result[0] else 0


usage_service = UsageService()