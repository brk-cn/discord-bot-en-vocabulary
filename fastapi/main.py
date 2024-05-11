from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()
mongodb_uri = os.getenv("MONGODB_URI")
client = MongoClient(mongodb_uri)
db = client["vocabulary"]
collection = db["words"]

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/submit")
async def submit(request: Request, word_english: str = Form(...), word_class: str = Form(...), word_turkish: str = Form(...)):
    word_data = {
        "word_english": word_english,
        "word_class": word_class,
        "word_turkish": word_turkish
    }
    collection.insert_one(word_data)
    return RedirectResponse(url="/", status_code=303)