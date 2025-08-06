from qdrant_client import AsyncQdrantClient, models
from qdrant_client.models import VectorParams, Distance, PointStruct
import random

from .utils import create_payload



def create_client_connection() -> AsyncQdrantClient:
    client = AsyncQdrantClient("http://qdrant:6333")
    return client


async def get_collection_names(client: AsyncQdrantClient) -> list[str]:
    collections = await client.get_collections()
    return [str(collection.name) for collection in collections.collections]


async def store_vectors(client: AsyncQdrantClient, 
                        collection_name: str,
                        config: dict,
                        graph_embeddings: dict = {}, 
                        item_embeddings: dict = {}, 
                        item_infos: list[list[str]] | None = None,
                        ) -> None:
    # Final vectors are direct concatenation of graph and item embeddings
    # If one is missing, then it is replaced with zero vector
    if not await client.collection_exists(collection_name):
        await client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=config['node_embedding']['constructor']['dimensions'] + config['text_embedding']['vector_dim'], distance=Distance.COSINE),
        )

    final_embeddings = {}
    for id in list(item_embeddings.keys()) + list(graph_embeddings.keys()):
        final_embeddings[str(id)] = (
            item_embeddings.get(id, [0 for _ in range(config['text_embedding']['vector_dim'])]) +
            graph_embeddings.get(id, [0 for _ in range(config['node_embedding']['constructor']['dimensions'])])
        )

    ids = sorted(list(map(int, final_embeddings.keys())))
    await client.upsert(
        collection_name=collection_name,
        points=[PointStruct(id=idx,
                            vector=final_embeddings[str(idx)],
                            payload=create_payload(str(idx), item_infos) if item_infos is not None else {"title": "", "description": ""}) for idx in ids]
        )


async def retrieve_k_similar_items(client: AsyncQdrantClient, collection_name:str, item_id: str, k: int) -> list[dict]:
    try:
        retrieve_result = await client.retrieve(
            collection_name=collection_name,
            ids=[int(item_id)],
            with_vectors=True,
            with_payload=False
        )

        query_vector = retrieve_result[0].vector
        search_result = await client.query_points(
            collection_name=collection_name,
            query=query_vector,
            limit=k,
            with_payload=True
        )
        similar_items = []
        for result in search_result.points:
            try:
                similar_items.append({
                    "id": str(result.id),
                    "name": result.payload["title"],
                    "description": result.payload["description"],
                })
            except AttributeError as ex:
                continue
        return similar_items
    except Exception as ex:
        print(f'Exception during retrieve_k_similar_items: {ex}')
        return []


async def retrieve_random_k_items(client: AsyncQdrantClient, collection_name:str, k: int) -> list[dict]:
    try:
        info = await client.get_collection(collection_name)
        total_points = info.points_count

        if total_points < k:
            k = total_points

        # Random offset
        offset = random.randint(0, total_points - k)

        search_result = await client.scroll(collection_name=collection_name,
                                            limit=k,
                                            offset=offset)
        items = []
        for result in search_result[0]:
            items.append({
                "id": str(result.id),
                "name": result.payload["title"],
                "description": result.payload["description"],
            })
        return items
    except Exception as ex:
        print(f'Exception during retrieve_random_k_items: {ex}')
        return []
