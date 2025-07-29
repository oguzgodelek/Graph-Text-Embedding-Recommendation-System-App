from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

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
    try: 
        print("File received for graph initialization", graphFileInput)
        return {"status": "processing"}
    except Exception as e:
        print("Error during graph initialization:", e)
        return {"status": "error", "message": str(e)}

@app.post('/initialize_only_text')
async def initialize_only_text(textFileInput: UploadFile = File(...)):
    try: 
        print("File received for text initialization", textFileInput)
        return {"status": "processing"}
    except Exception as e:
        print("Error during text initialization:", e)
        return {"status": "error", "message": str(e)}

@app.post('/initialize_both')
async def initialize_both(
    textFileInput: UploadFile = File(...),
    graphFileInput: UploadFile = File(...)
):
    try: 
        print("File received for both initialization", textFileInput, graphFileInput)
        return {"status": "processing"}
    except Exception as e:
        print("Error during both initialization:", e)
        return {"status": "error", "message": str(e)}
