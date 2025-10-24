from django.db import models
from ninja import Schema
from typing import List, Optional
from datetime import date

class Author(models.Model):
    name = models.TextField()
    biography = models.TextField()
    date_of_birth = models.DateField(null=True)

    def __str__(self):
        return self.name
    
    
    
# Schema

class BookBriefSchema(Schema):
    id: int
    title: str
  

class AuthorInSchema(Schema):
    name: str
    biography: str
    date_of_birth: Optional[date] = None

class AuthorOutSchema(Schema):
    id: int
    name: str
    biography: str
    date_of_birth: Optional[date]
    books: List[BookBriefSchema]