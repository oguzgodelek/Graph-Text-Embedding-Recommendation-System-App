import re 
import numpy as np
from sentence_transformers import SentenceTransformer
import networkx as nx
from node2vec import Node2Vec


########## Get text embeddings ############
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
    return list(map(lambda x: clean_title(x[0]) + ' | ' + clean_description(x[1]), item_data))


def get_sentence_embeddings(data: list[str], config: dict):
    model = SentenceTransformer(config['text_embedding']['model_name'], device=config['device'])
    embeddings = model.encode(data)
    return embeddings


########### Generate node embeddings ##########
def create_user_item_graph_nx(interaction_data: list[list[str]]) -> nx.Graph:
    # This graph is a weighted bipartite graph that users and jobs are its nodes
    # If there is an interaction between a user and an item there is an edge between these two nodes
    # The weight of the edge is given in the data unless it is 1
    graph = nx.Graph()
    unique_user_ids = list(set(map(lambda x: x[0], interaction_data)))
    unique_item_ids = list(set(map(lambda x: x[1], interaction_data)))
    graph.add_nodes_from(unique_user_ids, type='user')
    graph.add_nodes_from(unique_item_ids, type='item')
    graph.add_weighted_edges_from(interaction_data)
    return graph


def create_embeddings_node2vec(graph: nx.Graph, conf_dict: dict) -> dict:
    node2vec = Node2Vec(graph=graph, **conf_dict['constructor'])
    model = node2vec.fit(**conf_dict['fit'])
    job_embeddings = {}
    for node, data in graph.nodes(data=True):
        if data.get('type') == 'item':
            job_embeddings[node] = model.wv[node].tolist()
    return job_embeddings
