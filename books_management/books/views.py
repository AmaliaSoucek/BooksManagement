from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, UpdateView

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


class AuthorUpdateView(LoginRequiredMixin, UpdateView):
    model = Author
    fields = ('first_name', 'last_name',)
    success_url = '/authors'


@login_required
def index(request):
    return render(request, 'books/index.html', {})
