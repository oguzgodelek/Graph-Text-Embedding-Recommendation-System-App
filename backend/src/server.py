from contextlib import asynccontextmanager
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import sys
import json
from pydantic import BaseModel

from .utils import database_access
from .utils import utils


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        print("🌱 Lifespan starting...")
        app.state.client = database_access.create_client_connection()
        import os
        with open('config.json', 'r') as config_file:
            app.state.config = json.load(config_file)
        print("✅ Client initialized:", app.state.client)
        yield
        app.state.client.close()
    except BaseException as ex:
        print("Error during lifespan:", ex)
        sys.exit(-1)

app = FastAPI(lifespan=lifespan)

origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get('/')
async def read_root():
    return {"message": "Alive"}


@app.get('/status')
async def read_status():
    return {"status": "entrypoint"}


@app.post('/initialize_only_graph')
async def initialize_only_graph(graphFileInput: UploadFile = File(...)):
    graph_embeddings, collection_name = await utils.get_graph_embeddings(graphFileInput, app.state.config['node_embedding'])
    await database_access.store_vectors(config=app.state.config,
                                            client=app.state.client,
                                            collection_name=collection_name,
                                            graph_embeddings=graph_embeddings)
    try: 
        print("Graph file received:", graphFileInput.filename)
        
        return {"collection_name": collection_name}
    except Exception as e:
        print("Error during graph initialization:", e)
        return {"status": "error", "message": str(e)}


@app.post('/initialize_only_text')
async def initialize_only_text(textFileInput: UploadFile = File(...)):
    try: 

        text_embeddings, collection_name, item_info = await utils.get_text_embeddings(textFileInput, app.state.config['text_embedding'])
        await database_access.store_vectors(config=app.state.config,
                                            client=app.state.client,
                                            collection_name=collection_name,
                                            item_embeddings=text_embeddings,
                                            item_infos=item_info)
        return {"collection_name": collection_name}
    except Exception as e:
        print("Error during text initialization:", e)
        return {"status": "error", "message": str(e)}


@app.post('/initialize_both')
async def initialize_both(textFileInput: UploadFile = File(...),
                          graphFileInput: UploadFile = File(...)):
    graph_embeddings, collection_name = await utils.get_graph_embeddings(graphFileInput,
                                                                         app.state.config['node_embedding'])
    text_embeddings, _, item_info = await utils.get_text_embeddings(textFileInput, app.state.config['text_embedding'])
    await database_access.store_vectors(config=app.state.config,
                                        client=app.state.client,
                                        collection_name=collection_name,
                                        graph_embeddings=graph_embeddings,
                                        item_embeddings=text_embeddings,
                                        item_infos=item_info)
    try:
        return {"collection_name": collection_name}
    except Exception as e:
        print("Error during both initialization:", e)
        return {"status": "error", "message": str(e)}


class CollectionResponse(BaseModel):
    count: int
    collectionList: list[str]
    message: str


@app.get('/available_collections')
async def available_collections() -> CollectionResponse:
    try:
        # Get databases from the client stored in app state
        collections = await database_access.get_collection_names(app.state.client)
        return CollectionResponse(count=len(collections),
                                  collectionList=collections,
                                  message="OK" if len(collections) > 0 else "No collection found")
    except Exception as ex:
        print("Error retrieving collections:", ex)
        return CollectionResponse(count=0, collectionList=[], message=str(ex))


class Item(BaseModel):
    id: str
    name: str
    description: str


class ItemResponse(BaseModel):
    count: int
    itemList: list[Item]
    message: str


@app.get('/retrieve_similar/{k}/{collection}/{id}')
async def retrieve_similar(k: int, collection: str, id: str) -> ItemResponse:
    try:
        # Get databases from the client stored in app state
        items: list[dict[str, str]] = await database_access.retrieve_k_similar_items(app.state.client,
                                                                                     collection,
                                                                                     id, k)
        return ItemResponse(count=len(items),
                            itemList=list(map(lambda item: Item(**item), items)),
                            message="OK" if len(items) > 0 else "No item found")
    except Exception as ex:
        print("Error retrieving similar collections:", ex)
        return ItemResponse(count=0, itemList=[], message=str(ex))


@app.get('/retrieve_random/{k}/{collection}')
async def retrieve_random(k: int, collection: str) -> ItemResponse:
    try:
        # Get databases from the client stored in app state
        items: list[dict[str, str]] = await database_access.retrieve_random_k_items(app.state.client,
                                                                                    collection, k)
        return ItemResponse(count=len(items),
                            itemList=list(map(lambda item: Item(**item), items)),
                            message="OK" if len(items) > 0 else "No item found")
    except Exception as ex:
        print("Error retrieving random collections:", ex)
        return ItemResponse(count=0, itemList=[], message=str(ex))
