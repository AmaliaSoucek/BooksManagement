from django.contrib.auth.models import User
from django.db import models


class Author(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)


class Book(models.Model):
    author = models.ForeignKey(Author)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)


class BorrowingRequest(models.Model):

    PENDING = 0
    APPROVED = 1
    DECLINED = 2

    CHOICES = ((PENDING, u'pending'),
               (APPROVED, u'approved'),
               (DECLINED, u'declined'))

    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    borrower = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.PositiveSmallIntegerField(choices=CHOICES)

