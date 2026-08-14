from rag.indexing import get_index_client, INDEX_NAME

client = get_index_client()
client.delete_index(INDEX_NAME)
print(f"Deleted index '{INDEX_NAME}'")