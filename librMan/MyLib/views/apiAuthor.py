from ninja import Router,Schema
from django.shortcuts import get_object_or_404
from django.http import HttpRequest
from typing import List
from ..models.author import Author, AuthorInSchema, AuthorOutSchema

authorRouter = Router()

class ErrorSchema(Schema):
    error: str

@authorRouter.post("/add", response=AuthorOutSchema)
def add_author(request: HttpRequest, payload: AuthorInSchema):
    new_author = Author.objects.create(**payload.dict())
    return new_author

@authorRouter.get("/list", response=List[AuthorOutSchema])
def list_authors(request: HttpRequest):
    return Author.objects.prefetch_related('books').all()

@authorRouter.get("single/{author_id}", response=AuthorOutSchema)
def single_author(request: HttpRequest, author_id: int):
    return get_object_or_404(Author.objects.prefetch_related('books'), id=author_id)

@authorRouter.delete("/{author_id}", response={204: None, 400: ErrorSchema})
def delete_author(request: HttpRequest, author_id: int):
    author = get_object_or_404(Author, id=author_id)

    if author.books.exists():
        return 400, {"error": "Cannot delete author with associated books"}
    author.delete()
    return 204, None