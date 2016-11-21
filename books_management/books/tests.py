from django.test import TestCase

from .models import Author, Book, BorrowingRequest, User


class BookMethodTests(TestCase):

    def setUp(self):
        author = Author.objects.create(first_name='George', last_name='Orwell')
        owner = User.objects.create(username='user', password='test')
        book = Book.objects.create(title='1984', author=author, owner=owner)

    def test_borrow_with_already_borrowed_book(self):
        """
        If book is already borrowed borrow should return False.
        """
        book = Book.objects.get(title='1984')
        borrower = User.objects.create(username='borrower', password='test')
        new_borrower = User.objects.create(
            username='new borrower', password='test')
        BorrowingRequest.objects.create(
            book=book, borrower=borrower, status=BorrowingRequest.APPROVED)

        self.assertIs(book.borrow(new_borrower), False)

    def test_borrow_already_requested_book(self):
        """
        If book was already requested by user borrow should return False.
        """
        book = Book.objects.get(title='1984')
        borrower = User.objects.create(username='borrower', password='test')
        book.borrow(borrower)
        self.assertIs(book.borrow(borrower), False)


class BorrowingRequestMethodTests(TestCase):

    def setUp(self):
        author = Author.objects.create(first_name='George', last_name='Orwell')
        owner = User.objects.create(username='user', password='test')
        book = Book.objects.create(title='1984', author=author, owner=owner)

    def test_approve_with_multiple_pending_requests(self):
        """
        If multiple requests exists, if one is approved all the others get declined.
        """
        book = Book.objects.select_related('author').get(title='1984')
        borrower_1 = User.objects.create(username='borrower1', password='test')
        borrower_2 = User.objects.create(username='borrower2', password='test')
        borrower_3 = User.objects.create(username='borrower3', password='test')

        book.borrow(borrower_1)
        book.borrow(borrower_2)
        book.borrow(borrower_3)

        request = BorrowingRequest.objects.get(borrower=borrower_1, book=book)
        request.approve(book.owner)

        self.assertIs(
            BorrowingRequest.objects.filter(
                book=book, status=BorrowingRequest.PENDING).exists(),
            False
        )
