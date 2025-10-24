from django.contrib import admin
from MyLib.models.author import Author
from MyLib.models.book import Book
from MyLib.models.borrower import Borrower
# Register your models here.
admin.site.register(Book)
admin.site.register(Author)
admin.site.register(Borrower)
