from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

class Book(BaseModel):
    title: str

app = FastAPI()

books = [
    {
        "id":1,
        "title":"ananas",
    },
    {
        "id":2,
        "title":"skuf"
    },
]

@app.get("/books", tags=["books"])
def readbooks():
    return books

@app.get("/books/{book_id}", tags=["books"])
def get_book(book_id: int):
    for book in books:
        if book["id"] == book_id:
            return book
    raise HTTPException(status_code=404)

@app.post("/books", tags=["books"])
def create_book(book: Book):
    new_book = {
        "id": len(books) + 1,
        "title": book.title
    }
    books.append(new_book)
    return new_book
