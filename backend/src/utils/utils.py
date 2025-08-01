from .generate_embeddings import create_user_item_graph_nx, create_embeddings_node2vec, get_sentence_embeddings
from fastapi import UploadFile
import io
import re

def clean_title(text: str) -> str:
    text = text.rstrip().lstrip()
    text = re.sub('^\w\s', '', text)  # Remove special characters
    return text


def clean_description(text: str) -> str:
    text = re.sub('<.*?>', '', text)  # Delete html tags if there is any
    text = re.sub('^\w\s', '', text)  # Delete special characters except spaces
    text = text.replace('&nbsp;', '')  # Delete &nbsp; pattern
    return text


def get_and_clean_data(item_data: list[list[str]]) -> list[str]:
    return list(map(lambda x: clean_title(x[1]) + ' | ' + clean_description(x[2]), item_data))


def create_payload(id: str, item_data: list[list[str]]) -> dict:
    entry = list(filter(lambda x: x[0] == id, item_data))[0]
    payload = {
        "title": clean_title(entry[1]),
        "description": clean_description(entry[2])
    }
    return payload


async def read_file(file: UploadFile, isInteraction: bool) -> tuple[list[list[int | str]], str]:
    raw_data = await file.read()
    data = io.StringIO(raw_data.decode('utf-8'))
    if isInteraction:
        data = list(map(lambda x: [int(x[0]), int(x[1]), int(x[2])], map(lambda x: x.split(','), data.read().split('\n')[1:-1])))
    else:
        data = list(map(lambda x: x.split(','), data.read().split('\n')[1:-1]))
    return data, file.filename


async def get_graph_embeddings(graph_file: UploadFile, config: dict) -> tuple[dict, str]:
    graph_data, collection_name = await read_file(graph_file, True)
    interaction_graph = create_user_item_graph_nx(graph_data)
    graph_embeddings = create_embeddings_node2vec(interaction_graph, config)
    return graph_embeddings, ".".join((collection_name.split('.')[:-1]))


async def get_text_embeddings(text_file: UploadFile, config: dict) -> tuple[dict, str, list[list[str]]]:
    text_data, collection_name = await read_file(text_file, False)
    cleaned_data = get_and_clean_data(text_data)
    text_embeddings = get_sentence_embeddings(cleaned_data, config)
    embedding_dict = {}
    for item_id, embedding in zip(map(lambda x: x[0], text_data), text_embeddings.tolist()):
        embedding_dict[item_id] = embedding
    return embedding_dict, ".".join((collection_name.split('.')[:-1])), text_data

