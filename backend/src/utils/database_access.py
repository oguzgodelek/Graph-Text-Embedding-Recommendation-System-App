from qdrant_client import AsyncQdrantClient, models
from qdrant_client.models import VectorParams, Distance
import json



def create_client_connection() -> AsyncQdrantClient:
    client = AsyncQdrantClient("http://qdrant:6333")
    return client


async def get_collection_names(client: AsyncQdrantClient) -> list:
    collections = await client.get_collections()
    return [collection.name for collection in collections.collections]