from ninja import Router,Schema
from django.shortcuts import get_object_or_404
from django.http import HttpRequest
from typing import List
from ..models.book import Book, BookInSchema, BookOutSchema,BookWithHistorySchema,BookBorrowingHistorySchema,BorrowerBriefSchema
from ..models.borrower import BookBorrowing

bookRouter = Router()

class ErrorSchema(Schema):
    error: str

@bookRouter.post("/add", response=BookOutSchema)
def add_book(request: HttpRequest, payload: BookInSchema):
    book_data = payload.dict()
    authors = book_data.pop('authors')
    new_book = Book.objects.create(**book_data)
    new_book.authors.set(authors)
    return new_book

@bookRouter.get("/list", response=List[BookOutSchema])
def list_books(request: HttpRequest):
    return Book.objects.prefetch_related('authors').all()

@bookRouter.get("single/{book_id}", response=BookOutSchema)
def single_book(request: HttpRequest, book_id: int):
    return get_object_or_404(Book.objects.prefetch_related('authors'), id=book_id)


@bookRouter.delete("/{book_id}", response={204: None, 400: ErrorSchema})
def delete_book(request: HttpRequest, book_id: int):
    book = get_object_or_404(Book, id=book_id)

    if book.available_quantity != book.quantity:
        return 400, {"error": "Cannot delete book with active borrowings"}
    book.delete()
    return 204, None

@bookRouter.get("/history/{book_id}", response=BookWithHistorySchema)
def book_borrowing_history(request: HttpRequest, book_id: int):
    book = get_object_or_404(Book.objects.prefetch_related('authors'), id=book_id)
    
    # Get all borrowing records for this book
    borrowing_history = BookBorrowing.objects.filter(
        book=book
    ).select_related('borrower').order_by('-borrow_date')
    
    # Get current borrower (if any)
    current_borrowing = borrowing_history.filter(is_returned=False).first()
    current_borrower = None
    if current_borrowing:
        current_borrower = BorrowerBriefSchema(
            id=current_borrowing.borrower.id,
            name=current_borrowing.borrower.name,
            email=current_borrowing.borrower.email
        )
    
    # Format borrowing history
    history = [
        BookBorrowingHistorySchema(
            borrower=BorrowerBriefSchema(
                id=record.borrower.id,
                name=record.borrower.name,
                email=record.borrower.email
            ),
            borrow_date=record.borrow_date,
            due_date=record.due_date,
            return_date=record.return_date,
            is_returned=record.is_returned
        ) for record in borrowing_history
    ]
    
    return BookWithHistorySchema(
        id=book.id,
        title=book.title,
        published_date=book.published_date,
        quantity=book.quantity,
        available_quantity=book.available_quantity,
        authors=[{
            'id': author.id, 
            'name': author.name
        } for author in book.authors.all()],
        current_borrower=current_borrower,
        borrowing_history=history
    )