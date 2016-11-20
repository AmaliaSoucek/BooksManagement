from django.conf.urls import url
from django.contrib import auth
from django.contrib.auth.views import login, logout
from django.views.generic import TemplateView

from . import views


urlpatterns = [
    url(r'', views.BookListView.as_view()),

    url(r'register/?$', views.UserRegisterLogin.as_view()),
    url(r'^login/?$', auth.views.login),
    url(r'^logout/?$', auth.views.logout, {'next_page': '/goodbye'}),
    url(r'^goodbye/?$',
        TemplateView.as_view(template_name='registration/goodbye.html')),

    url(r'^authors/?$', views.AuthorListView.as_view()),
    url(r'^authors/create/?$', views.AuthorCreateView.as_view()),
    url(r'^authors/(?P<pk>[0-9]+)/?$', views.AuthorUpdateView.as_view()),

    url(r'^books/(?P<pk>[0-9]+)/?$', views.BookDetailOrUpdateView.as_view()),
    url(r'^books/detail/(?P<pk>[0-9]+)/?$',
        views.BookDetailView.as_view(template_name='books/book_detail.html'),
        name='book-detail'),
    url(r'^books/update/(?P<pk>[0-9]+)/?$',
        views.BookUpdateView.as_view(), name='book-update'),
    url(r'^books/create/?$', views.BookCreateView.as_view()),
    url(r'^books/remove/(?P<pk>[0-9]+)/?$', views.BookDeleteView.as_view()),
    url(r'^books/owned?$', views.OwnedBookListView.as_view()),

    url(r'^books/borrow/(?P<pk>[0-9]+)/?$', views.BorrowBook.as_view()),
    url(r'^books/requests/?$', views.BorrowingRequestListView.as_view()),
    url(r'^books/requests/mine?$', views.MyBorrowingRequestListView.as_view()),
    url(r'^books/requests/(?P<pk>[0-9]+)/approve/?$', views.HandleRequest.as_view(), {'approve': True}),
    url(r'^books/requests/(?P<pk>[0-9]+)/decline/?$', views.HandleRequest.as_view(), {'approve': False}),
]
