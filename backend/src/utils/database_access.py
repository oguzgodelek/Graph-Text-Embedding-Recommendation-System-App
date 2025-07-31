from qdrant_client import AsyncQdrantClient, models
from qdrant_client.models import VectorParams, Distance

from .utils import create_payload


def create_client_connection() -> AsyncQdrantClient:
    client = AsyncQdrantClient("http://qdrant:6333")
    return client


async def get_collection_names(client: AsyncQdrantClient) -> list:
    collections = await client.get_collections()
    return [collection.name for collection in collections.collections]


async def store_vectors(client: AsyncQdrantClient, 
                        collection_name: str,
                        config: dict,
                        graph_embeddings: dict = {}, 
                        item_embeddings: dict = {}, 
                        item_infos: list[list[str]] | None = None,
                        ) -> None:
    # Final vectors are direct concatenation of graph and item embeddings
    # If one is missing, then it is replaced with zero vector
    final_embeddings = {}
    for id in list(item_embeddings.keys()) + list(graph_embeddings.keys()):
        final_embeddings[id] = (
            item_embeddings.get(id, [0 for _ in range(config['text_embedding']['vector_dim'])]) +
            graph_embeddings.get(id, [0 for _ in range(config['graph_embedding']['constructor']['dimensions'])])
        )

    ids = sorted(list(map(int, final_embeddings.keys())))
    vectors = list(map(lambda x: final_embeddings[str(x)], ids))
    payloads = list(map(lambda id: create_payload(str(id), item_infos), ids)) if item_infos is not None else [{"id": id for id in ids}]
    await client.upload_collection(
        collection_name=collection_name,
        vectors=vectors,
        payload=payloads,
        ids=ids,
    )


async def retrieve_k_similar_items(client: AsyncQdrantClient, collection_name:str, item_id: str, k: int):
    try:
        retrieve_result = await client.retrieve(
            collection_name='jobs',
            ids=[item_id],
            with_vectors=True,
            with_payload=True
        )
        query_vector = retrieve_result[0].vector
        search_result = await client.query_points(
            collection_name=collection_name,
            query=query_vector,
            limit=k,
            with_payload=True
        )
        similar_jobs = []
        for result in search_result.points:
            similar_jobs.append({
                "job_id": result.id,
                "job_title": result.payload["title"],
                "job_description": result.payload["description"],
                "similarity score": result.score,
            })
        return similar_jobs
    except Exception as ex:
        print(f'Exception during retrieve_k_similar_items: {ex}')
        return {}
