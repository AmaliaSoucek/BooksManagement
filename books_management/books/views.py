from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.views import View
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from .models import Author, Book, BorrowingRequest


class UserRegisterLogin(LoginRequiredMixin, CreateView):
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

    def get_context_data(self, **kwargs):
        context = super(BookListView, self).get_context_data(**kwargs)
        context['title'] = 'All books'
        return context


class OwnedBookListView(LoginRequiredMixin, ListView):
    model = Book

    def get_queryset(self):
        return Book.objects.filter(owner=self.request.user)

    def get_context_data(self, **kwargs):
        context = super(OwnedBookListView, self).get_context_data(**kwargs)
        context['title'] = 'My books'
        return context


class BookCreateView(LoginRequiredMixin, CreateView):
    model = Book
    fields = ('title', 'author')
    success_url = '/'

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
