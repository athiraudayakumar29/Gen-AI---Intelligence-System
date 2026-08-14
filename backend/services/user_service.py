import uuid
import os
from azure.cosmos import CosmosClient, PartitionKey
from dotenv import load_dotenv
from backend.services.auth_service import hash_password, verify_password

load_dotenv()


class UserService:
    def __init__(self):
        endpoint = os.getenv("COSMOS_ENDPOINT")
        key = os.getenv("COSMOS_KEY")
        db_name = os.getenv("COSMOS_DATABASE", "assistant_db")

        self.client = CosmosClient(endpoint, credential=key)
        self.database = self.client.create_database_if_not_exists(id=db_name)
        self.container = self.database.create_container_if_not_exists(
            id="users",
            partition_key=PartitionKey(path="/user_id"),
        )

    def create_user(self, email: str, password: str) -> dict:
        user_id = str(uuid.uuid4())
        item = {
            "id": user_id,
            "user_id": user_id,
            "email": email,
            "password_hash": hash_password(password)
        }
        self.container.create_item(body=item)
        return {"user_id": user_id, "email": email}

    def get_user_by_email(self, email: str) -> dict | None:
        query = "SELECT * FROM c WHERE c.email = @email"
        params = [{"name": "@email", "value": email}]
        results = list(self.container.query_items(
            query=query,
            parameters=params,
            enable_cross_partition_query=True
        ))
        return results[0] if results else None

    def authenticate(self, email: str, password: str) -> dict | None:
        user = self.get_user_by_email(email)
        if user and verify_password(password, user["password_hash"]):
            return {"user_id": user["user_id"], "email": user["email"]}
        return None


user_service = UserService()