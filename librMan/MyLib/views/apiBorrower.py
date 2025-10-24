from datetime import datetime,date
from urllib.error import HTTPError
from ninja import Router,Schema
from django.shortcuts import get_object_or_404
from django.http import HttpRequest
from typing import List
from ..models.borrower import Borrower, BookBorrowing
from ..models.book import Book
from ..models.borrower import (
    BorrowerInSchema, 
    BorrowerOutSchema, 
    BorrowerDetailSchema,
    BookBorrowingInSchema, 
    BookBorrowingOutSchema,
    BookBriefForBorrowerSchema
)

borrowerRouter = Router()

class ErrorSchema(Schema):
    error: str

@borrowerRouter.post("/add", response=BorrowerOutSchema)
def add_borrower(request: HttpRequest, payload: BorrowerInSchema):
    new_borrower = Borrower.objects.create(**payload.dict())
    return new_borrower

@borrowerRouter.get("/list", response=List[BorrowerOutSchema])
def list_borrowers(request: HttpRequest):
    return Borrower.objects.all()


@borrowerRouter.get("/single/{borrower_id}", response=BorrowerDetailSchema)
def single_borrower(request: HttpRequest, borrower_id: int):
    borrower = get_object_or_404(Borrower.objects.prefetch_related('bookborrowing_set__book'), id=borrower_id)

    active_borrowings = BookBorrowing.objects.filter(
        borrower=borrower, is_returned=False
    ).select_related("book")

    return BorrowerDetailSchema(
        id=borrower.id,
        name=borrower.name,
        email=borrower.email,
        phone=borrower.phone,
        membership_date=borrower.membership_date,
        current_borrowings=[
            BookBorrowingOutSchema(
                id=b.id,
                book=BookBriefForBorrowerSchema(id=b.book.id, title=b.book.title),
                borrow_date=b.borrow_date,
                due_date=b.due_date,
                return_date=b.return_date,
                is_returned=b.is_returned
            )
            for b in active_borrowings
        ]
    )
    

@borrowerRouter.post("/{borrower_id}/borrow", response=BookBorrowingOutSchema)
def borrow_book(request: HttpRequest, borrower_id: int, payload: BookBorrowingInSchema):
    borrower = get_object_or_404(Borrower, id=borrower_id)
    book = get_object_or_404(Book, id=payload.book_id)
    
    
    if book.available_quantity <= 0:
        raise HTTPError(404, "Book is not available for borrowing")
    
    
    borrowing = BookBorrowing.objects.create(
        book=book,
        borrower=borrower,
        due_date=payload.due_date
    )
    
    
    book.available_quantity -= 1
    book.save()
    
    return borrowing

@borrowerRouter.post("/return/{borrowing_id}", response=BookBorrowingOutSchema)
def return_book(request: HttpRequest, borrowing_id: int):
    borrowing = get_object_or_404(BookBorrowing, id=borrowing_id)
    
    if borrowing.is_returned:
        raise HTTPError(400, "Book already returned")
    
    
    borrowing.is_returned = True
    borrowing.return_date = date.today()
    borrowing.save()
    
    
    book = borrowing.book
    book.available_quantity += 1
    book.save()
    
    return borrowing

@borrowerRouter.get("/{borrower_id}/history", response=List[BookBorrowingOutSchema])
def borrowing_history(request: HttpRequest, borrower_id: int):
    return BookBorrowing.objects.filter(borrower_id=borrower_id).select_related('book')

@borrowerRouter.get("/{borrower_id}/current", response=List[BookBorrowingOutSchema])
def current_borrowings(request: HttpRequest, borrower_id: int):
    return BookBorrowing.objects.filter(
        borrower_id=borrower_id,
        is_returned=False
    ).select_related('book')

@borrowerRouter.get("/overdue", response=List[BookBorrowingOutSchema])
def overdue_borrowings(request: HttpRequest):
    return BookBorrowing.objects.filter(
        is_returned=False,
        due_date__lt=date.today()
    ).select_related('book', 'borrower')
    
    
    
@borrowerRouter.delete("/{borrower_id}", response={204: None, 400: ErrorSchema})
def delete_borrower(request: HttpRequest, borrower_id: int):
    borrower = get_object_or_404(Borrower, id=borrower_id)
    
    if BookBorrowing.objects.filter(borrower=borrower, is_returned=False).exists():
        return 400, {"error": "Cannot delete borrower with active borrowings"}
    borrower.delete()
    return 204, None

# @borrowerRouter.delete("/borrowing/{borrowing_id}", response={204: None})
# def delete_borrowing(request: HttpRequest, borrowing_id: int):
#     borrowing = get_object_or_404(BookBorrowing, id=borrowing_id)
#     if not borrowing.is_returned:
#         return 400, {"error": "Cannot delete active borrowing record"}
#     borrowing.delete()
#     return 204, None