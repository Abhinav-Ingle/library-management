from django.db import models
from .author import Author
from ninja import Schema
from typing import List, Optional
from datetime import date

class Book(models.Model):
    title = models.TextField()
    published_date = models.DateField()
    authors = models.ManyToManyField(Author, related_name="books")
    quantity = models.IntegerField(default=1)
    available_quantity = models.IntegerField(default=1)

    def __str__(self):
        return self.title
    
    
#Schema

class AuthorBriefSchema(Schema):
    id: int
    name: str

class BookInSchema(Schema):
    title: str
    published_date: Optional[date] = None
    quantity: int
    authors: List[int]

class BookOutSchema(Schema):
    id: int
    title: str
    published_date: Optional[date] = None
    quantity: int
    available_quantity: int
    authors: List[AuthorBriefSchema]
    
class BorrowerBriefSchema(Schema):
    id: int
    name: str
    email: str

class BookBorrowingHistorySchema(Schema):
    borrower: BorrowerBriefSchema
    borrow_date: date
    due_date: date
    return_date: Optional[date]
    is_returned: bool

class BookWithHistorySchema(BookOutSchema):
    current_borrower: Optional[BorrowerBriefSchema]
    borrowing_history: List[BookBorrowingHistorySchema]