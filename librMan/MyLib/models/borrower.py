from django.db import models
from .book import Book
from ninja import Schema
from typing import List, Optional
from datetime import datetime, date


class Borrower(models.Model):
    name = models.TextField()
    email = models.EmailField()
    phone = models.TextField()
    membership_date = models.DateField(auto_now_add=True)
    borrowed_books = models.ManyToManyField(Book, through='BookBorrowing')

    def __str__(self):
        return self.name

class BookBorrowing(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    borrower = models.ForeignKey(Borrower, on_delete=models.CASCADE)
    borrow_date = models.DateField(auto_now_add=True)
    due_date = models.DateField()
    return_date = models.DateField(null=True)
    is_returned = models.BooleanField(default=False)
    
#Schema

class BookBriefForBorrowerSchema(Schema):
    id: int
    title: str
 

class BorrowerInSchema(Schema):
    name: str
    email: str
    phone: str

class BorrowerOutSchema(Schema):
    id: int
    name: str
    email: str
    phone: str
    membership_date: Optional[date] = None

class BookBorrowingInSchema(Schema):
    book_id: int
    due_date: Optional[date] = None

class BookBorrowingOutSchema(Schema):
    id: int
    book: BookBriefForBorrowerSchema
    borrow_date: Optional[date] = None
    due_date: Optional[date] = None
    return_date: Optional[date] = None
    is_returned: bool

class BorrowerDetailSchema(BorrowerOutSchema):
    current_borrowings: List[BookBorrowingOutSchema]                                                               