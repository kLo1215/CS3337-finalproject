from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('postbook', views.postbook, name='postbook'),
    path('displaybooks', views.displaybooks, name='displaybooks'),
    path('mybooks', views.mybooks, name='mybooks'),
    path('book_detail/<int:book_id>', views.book_detail, name='book_detail'),
    path('book_delete/<int:book_id>', views.book_delete, name='book_delete'),
    path('search/', views.search_books, name='search_books'),
    path('about_us', views.about_us, name='about_us'),
    path('rate_book/<int:book_id>/<str:is_positive>/', views.rate_book, name='rate_book'),
]

