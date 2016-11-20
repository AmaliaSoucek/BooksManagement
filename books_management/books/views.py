from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import models
from django.http import (
    Http404, HttpResponse, HttpResponseBadRequest, HttpResponseForbidden,
    HttpResponseRedirect)
from django.shortcuts import redirect
from django.views import View
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from .models import Author, Book, BorrowingRequest


class UserRegisterLogin(CreateView):
    template_name = 'registration/register.html'
    form_class = UserCreationForm
    success_url = '/'

    def form_valid(self, form):
        self.object = form.save()
        login(self.request, self.object)
        return HttpResponseRedirect(self.get_success_url())


class AuthorListView(LoginRequiredMixin, ListView):
    model = Author


class AuthorCreateView(LoginRequiredMixin, CreateView):
    model = Author
    fields = ('first_name', 'last_name',)
    success_url = '/authors'

    def get_context_data(self, **kwargs):
        context = super(AuthorCreateView, self).get_context_data(**kwargs)
        context['title'] = 'Add new author'
        return context


class AuthorUpdateView(LoginRequiredMixin, UpdateView):
    model = Author
    fields = ('first_name', 'last_name',)
    success_url = '/authors'

    def get_context_data(self, **kwargs):
        context = super(AuthorUpdateView, self).get_context_data(**kwargs)
        context['title'] = 'Edit Author'
        return context


class BookListView(LoginRequiredMixin, ListView):
    model = Book

    def get_queryset(self):

        q = BorrowingRequest.objects.filter(
            status=BorrowingRequest.APPROVED)

        return Book.objects.annotate(
            is_already_borrowed=models.Sum(models.Case(
                models.When(
                    borrowingrequest__status=BorrowingRequest.APPROVED,
                    then=1
                ), default=0, output_field=models.BooleanField()))
        ).annotate(
            requested=models.Sum(models.Case(
                models.When(
                    borrowingrequest__status=BorrowingRequest.PENDING,
                    borrowingrequest__borrower=self.request.user,
                    then=1
                ), default=0, output_field=models.BooleanField()))
        ).annotate(
            borrowed=models.Sum(models.Case(
                models.When(
                    borrowingrequest__status=BorrowingRequest.APPROVED,
                    borrowingrequest__borrower=self.request.user,
                    then=1
                ), default=0, output_field=models.BooleanField()))
        )

    def get_context_data(self, **kwargs):
        context = super(BookListView, self).get_context_data(**kwargs)
        context['title'] = 'All books'
        context['show_add_book'] = False
        return context


class OwnedBookListView(LoginRequiredMixin, ListView):
    model = Book

    def get_queryset(self):
        return Book.objects.filter(owner=self.request.user)

    def get_context_data(self, **kwargs):
        context = super(OwnedBookListView, self).get_context_data(**kwargs)
        context['title'] = 'My books'
        context['show_add_book'] = True 
        return context


class BookCreateView(LoginRequiredMixin, CreateView):
    model = Book
    fields = ('title', 'author')
    success_url = '/books/owned'

    def form_valid(self, form):
        book = form.save(commit=False)
        book.owner = self.request.user
        return super(BookCreateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(BookCreateView, self).get_context_data(**kwargs)
        context['title'] = 'Add new book'
        return context


class BookDeleteView(LoginRequiredMixin, DeleteView):
    model = Book
    success_url = '/books/owned'

    def get_object(self, queryset=None):
        obj = super(BookDeleteView, self).get_object()
        if not obj.owner == self.request.user:
            raise Http404
        return obj


class BookDetailOrUpdateView(LoginRequiredMixin, View):

    def get(self, request, pk):
        obj = Book.objects.get(id=pk)
        if obj.owner == request.user:
            return redirect('book-update', pk=pk)
        return redirect('book-detail', pk=pk)


class BookDetailView(LoginRequiredMixin, DeleteView):
    model = Book


class BookUpdateView(LoginRequiredMixin, UpdateView):
    model = Book
    fields = ('title', 'author')
    success_url = '/books/owned'

    def get_object(self, queryset=None):
        obj = super(BookUpdateView, self).get_object()
        if not obj.owner == self.request.user:
            raise Http404
        return obj

    def get_context_data(self, **kwargs):
        context = super(BookUpdateView, self).get_context_data(**kwargs)
        context['title'] = 'Edit book'
        return context


class BorrowBook(LoginRequiredMixin, View):

    def post(self, request, pk):
        book = Book.objects.filter(id=pk).first()

        if book is None:
            return HttpResponseBadRequest("Book not found!")

        if book.borrow(user=request.user):
            return HttpResponse()

        return HttpResponseBadRequest(
            "Book {} cannot be borrowed right now."
            "Try againg later!".format(book.title))


class BorrowingRequestListView(LoginRequiredMixin, ListView):
    model = BorrowingRequest

    def get_queryset(self):
        return BorrowingRequest.objects.select_related(
            'book__owner'
        ).filter(book__owner=self.request.user)

    def get_context_data(self, **kwargs):
        context = super(
            BorrowingRequestListView, self).get_context_data(**kwargs)
        context['title'] = 'Requests'
        return context


class MyBorrowingRequestListView(LoginRequiredMixin, ListView):
    model = BorrowingRequest

    def get_queryset(self):
        return BorrowingRequest.objects.select_related(
            'book__owner'
        ).filter(borrower=self.request.user)

    def get_context_data(self, **kwargs):
        context = super(
            MyBorrowingRequestListView, self).get_context_data(**kwargs)
        context['title'] = 'My requests'
        return context


class HandleRequest(LoginRequiredMixin, View):

    def post(self, request, pk, approve):
        br = BorrowingRequest.objects.select_related(
            'book__owner').filter(id=pk).first()

        if br is None:
            return HttpResponseBadRequest("Request not found!")

        if br.book.owner != request.user:
            return HttpResponseForbidden(
                "Cannot edit this request!")

        if approve and br.approve(user=request.user):
            return HttpResponse(br.get_status_display())

        if not approve and br.decline(user=request.user):
            return HttpResponse(br.get_status_display())

        return HttpResponseBadRequest(
            "Request for book {} cannot be approved or declined right now."
            "Try againg later!".format(br.book.title))
