from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pymongo import MongoClient
from dotenv import load_dotenv
import os
from bson.objectid import ObjectId

load_dotenv()
URI = os.getenv("MONGODB_URI")
if not URI:
    raise ValueError("MONGODB_URI environment variable is not set")



client = MongoClient(URI)
db = client["vocabulary"]
collection = db["words"]

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

latest_word = ""
@app.get("/add", response_class=HTMLResponse)
async def add_page(request: Request):
    return templates.TemplateResponse("add.html", {"request": request, "latest_word": latest_word})

@app.post("/add")
async def add_word(word_english: str = Form(...), word_class: str = Form(...), word_turkish: str = Form(...)):
    word_data = {
        "word_english": word_english,
        "word_class": word_class,
        "word_turkish": word_turkish
    }
    
    global latest_word
    latest_word = word_data
    collection.insert_one(word_data)
    return RedirectResponse(url="/add", status_code=303)

@app.get("/words", response_class=HTMLResponse)
async def words_page(request: Request):
    words = list(collection.find())
    return templates.TemplateResponse("words.html", {"request": request, "words": words})

@app.get("/edit/{word_id}", response_class=HTMLResponse)
async def edit_page(request: Request, word_id: str):
    word = collection.find_one({"_id": ObjectId(word_id)})
    return templates.TemplateResponse("edit.html", {"request": request, "word": word})

@app.post("/update/{word_id}", response_class=HTMLResponse)
async def update_word(word_id: str, word_english: str = Form(...), word_class: str = Form(...), word_turkish: str = Form(...)):
    updated_word_data = {
        "word_english": word_english,
        "word_class": word_class,
        "word_turkish": word_turkish
    }
    collection.update_one({"_id": ObjectId(word_id)}, {"$set": updated_word_data})
    return RedirectResponse(url="/words", status_code=303)

@app.get("/delete/{word_id}", response_class=HTMLResponse)
async def delete_word(word_id: str):
    collection.delete_one({"_id": ObjectId(word_id)})
    return RedirectResponse(url="/words", status_code=303)