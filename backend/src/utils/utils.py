import generate_embeddings
from fastapi import UploadFile
import io


async def read_file(file: UploadFile) -> tuple[list[list[str]], str]:
    raw_data = await file.read()
    data = io.StringIO(raw_data.decode('utf-8'))
    data = list(map(lambda x: x.split(','), data.read().split('\n')[1:-1]))
    return data, file.filename


async def get_graph_embeddings(graph_file: UploadFile, config: dict) -> tuple[dict, str]:
    graph_data, collection_name = await read_file(graph_file)
    interaction_graph = generate_embeddings.create_user_item_graph_nx(graph_data)
    graph_embeddings = generate_embeddings.create_embeddings_node2vec(interaction_graph, config)
    return graph_embeddings, ".".join((collection_name.split('.')[:-1]))


async def get_text_embeddings(text_file: UploadFile, config: dict) -> tuple[dict, str]:
    text_data, collection_name = await read_file(text_file)
    cleaned_data = generate_embeddings.get_and_clean_data(text_data)
    text_embeddings = generate_embeddings.get_sentence_embeddings(cleaned_data, config)
    embedding_dict = {}
    for job_id, embedding in zip(map(lambda x: x[0], text_data), text_embeddings.tolist()):
        embedding_dict[job_id] = embedding
    return text_embeddings, ".".join((collection_name.split('.')[:-1]))