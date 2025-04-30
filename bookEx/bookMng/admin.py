from django.contrib import admin

# Register your models here.

from .models import MainMenu
from .models import Book
from .models import Rating
from .models import Cart, CartItem

admin.site.register(MainMenu)
admin.site.register(Book)
admin.site.register(Rating)
admin.site.register(Cart)
admin.site.register(CartItem)