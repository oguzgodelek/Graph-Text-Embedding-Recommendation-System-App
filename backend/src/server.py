from contextlib import asynccontextmanager
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import sys
import io
import json

from .utils import database_access
from .utils import utils


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        print("🌱 Lifespan starting...")
        app.state.client = database_access.create_client_connection()
        app.state.config = json.load(open('../config.json'))
        print("✅ Client initialized:", app.state.client) ## Initialization problem
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
async def initialize_only_graph(graph_file_input: UploadFile = File(...)):
    try: 
        graph_embeddings, collection_name = await utils.get_graph_embeddings(graph_file_input, app.state.config)
        return {"status": "processing"}
    except Exception as e:
        print("Error during graph initialization:", e)
        return {"status": "error", "message": str(e)}


@app.post('/initialize_only_text')
async def initialize_only_text(text_file_input: UploadFile = File(...)):
    try: 
        
        text_embeddings, collection_name = await utils.get_text_embeddings(text_file_input, app.state.config)
        return {"status": "processing"}
    except Exception as e:
        print("Error during text initialization:", e)
        return {"status": "error", "message": str(e)}


@app.post('/initialize_both')
async def initialize_both(text_file_input: UploadFile = File(...),
                          graph_file_input: UploadFile = File(...)):
    try: 
        graph_embeddings, collection_name = await utils.get_graph_embeddings(graph_file_input, app.state.config['node_embedding'])
        text_embeddings, _ = await utils.get_text_embeddings(text_file_input, app.state.config)
        return {"status": "processing"}
    except Exception as e:
        print("Error during both initialization:", e)
        return {"status": "error", "message": str(e)}


@app.get('/available_databases')
async def available_databases():
    try:
        # Get databases from the client stored in app state
        databases = await database_access.get_collection_names(app.state.client)
        return {"databases": databases}
    except Exception as e:
        print("Error retrieving databases:", e)
        return {"status": "error", "message": str(e)}
    