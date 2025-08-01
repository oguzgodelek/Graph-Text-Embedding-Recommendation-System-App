import numpy as np
from sentence_transformers import SentenceTransformer
import networkx as nx
from node2vec import Node2Vec


########## Get text embeddings ############

def get_sentence_embeddings(data: list[str], config: dict) -> np.ndarray:
    model = SentenceTransformer(config['model'])
    embeddings = model.encode(data)
    return embeddings


########### Generate node embeddings ##########
def create_user_item_graph_nx(interaction_data: list[list[str | int]]) -> nx.Graph:
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


def create_embeddings_node2vec(graph: nx.Graph, 
                               conf_dict: dict) -> dict:
    node2vec = Node2Vec(graph=graph, **conf_dict['constructor'])
    model = node2vec.fit(**conf_dict['fit'])
    item_embeddings = {}
    for node, data in graph.nodes(data=True):
        if data.get('type') == 'item':
            try:
                item_embeddings[node] = model.wv[node].tolist()
            except KeyError:
                item_embeddings[node] = [0 for _ in range(conf_dict['constructor']['dimensions'])]
    return item_embeddings
