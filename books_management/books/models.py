from django.contrib.auth.models import User
from django.db import models


class Author(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)

    def __str__(self):
        return "%s %s" % (self.first_name, self.last_name)


class Book(models.Model):
    author = models.ForeignKey(Author)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)

    @property
    def is_borrowed(self):
        return self.borrowingrequest_set.filter(
            status=BorrowingRequest.APPROVED
        ).exists()

    def borrow(self, user):
        if self.is_borrowed:
            return False

        BorrowingRequest.objects.create(
            borrower=user, book=self, status=BorrowingRequest.PENDING)
        return True


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

    def approve(self, user):
        if self.status != self.PENDING:
            return False

        self.status = self.APPROVED
        BorrowingRequest.objects.filter(
            book=self.book).update(status=self.DECLINED)
        self.save()
        return True

    def decline(self, user):
        if not self.is_pending:
            return False

        self.status = self.DECLINED
        self.save()
        return True

    @property
    def is_pending(self):
        return self.status == self.PENDING
