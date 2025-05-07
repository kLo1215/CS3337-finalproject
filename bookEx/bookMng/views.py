from django.http import HttpResponse
from django.shortcuts import render
from django.shortcuts import get_object_or_404, redirect
from .models import Book, Rating
from .models import Comment
from .forms import CommentForm
# Create your views here.

from .models import MainMenu
from .forms import BookForm, BookSearchForm
from .models import Cart, CartItem
from .models import Book
from .models import Rating

from django.http import HttpResponseRedirect


from django.views.generic.edit import CreateView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy


def index(request):
    return render(request,
                  'bookMng/index.html',
                  {
                      'item_list': MainMenu.objects.all()
                  })

@login_required(login_url='/login')
def postbook(request):
    submitted = False
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES)
        if form.is_valid():
            book = form.save(commit=False)
            try:
                book.username = request.user
            except Exception:
                pass
            book.save()
            return HttpResponseRedirect('/postbook?submitted=True')
    else:
        form = BookForm()
        if 'submitted' in request.GET:
            submitted = True
    return render(request,
                  'bookMng/postbook.html',
                  {
                      'form': form,
                      'item_list': MainMenu.objects.all(),
                      'submitted': submitted
                  })


def displaybooks(request):
    books = Book.objects.all()
    for b in books:
        b.pic_path = b.picture.url[14:]
    return render(request,
                  'bookMng/displaybooks.html',
                  {
                      'item_list': MainMenu.objects.all(),
                      'books': books
                  })


def book_detail(request, book_id):
    book = get_object_or_404(Book, id=book_id) #small changes here for ratings

    book.pic_path = book.picture.url[14:]

    #rate
    total_ratings = book.ratings.count()  # Total ratings for the book
    positive_ratings = book.ratings.filter(is_positive=True).count()

    # Calculate percentage here
    if total_ratings > 0:
        percentage = (positive_ratings / total_ratings) * 100
    else:
        percentage = 0  # If no ratings, set percentage to 0

    # Comment section handling
    comment_form = CommentForm(request.POST or None)
    if request.method == 'POST' and comment_form.is_valid() and request.user.is_authenticated:
        content = comment_form.cleaned_data['content']
        Comment.objects.create(book=book, user=request.user, content=content)
        return redirect('book_detail', book_id=book.id)

    comments = Comment.objects.filter(book=book)

    return render(request,
                  'bookMng/book_detail.html',
                  {
                      'item_list': MainMenu.objects.all(),
                      'book': book,
                      'total_ratings': total_ratings,
                      'positive_ratings': positive_ratings,
                      'percentage': percentage,
                      'comment_form': comment_form,
                      'comments': comments
                  })

@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    book_id = comment.book.id
    comment.delete()
    return redirect('book_detail', book_id=book_id)

def book_delete(request, book_id):
    book = Book.objects.get(id=book_id)
    book.delete()

    return render(request,
                  'bookMng/book_delete.html',
                  {
                      'item_list': MainMenu.objects.all(),
                  })

def rate_book(request, book_id, is_positive):
    book = get_object_or_404(Book, id=book_id)

    if request.user.is_authenticated:
        is_positive_bool = True if is_positive.lower() == 'true' else False  # ensure it's a real bool
        Rating.objects.update_or_create(
            user=request.user,
            book=book,
            defaults={'is_positive': is_positive_bool}
        )

    return redirect('book_detail', book_id=book.id)


class Register(CreateView):
    template_name = 'registration/register.html'
    form_class = UserCreationForm
    success_url = reverse_lazy('register-success')

    def form_valid(self, form):
        form.save()
        return HttpResponseRedirect(self.success_url)

@login_required(login_url='/login')
def mybooks(request):
    books = Book.objects.filter(username=request.user)
    for b in books:
        b.pic_path = b.picture.url[14:]
    return render(request,
                  'bookMng/mybooks.html',
                  {
                      'item_list': MainMenu.objects.all(),
                      'books': books
                  })

def search_books(request):
    form = BookSearchForm(request.GET or None)
    results = Book.objects.all()


    if form.is_valid() and form.cleaned_data['query']:
        query = form.cleaned_data['query']
        results = results.filter(name__icontains=query)


    for b in results:
        b.pic_path = b.picture.url[14:]

    return render(request,
    'bookMng/search_results.html',
    {
        'item_list': MainMenu.objects.all(),
        'form': form,
        'results': results
    })

def about_us(request):
    return render(request,
                  'aboutUs/about_us.html',
                  {
                      'item_list': MainMenu.objects.all()
                  })

@login_required
def add_to_cart(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    item, created = CartItem.objects.get_or_create(cart=cart, book=book)
    if not created:
        item.quantity += 1
        item.save()
    return redirect('view_cart')


@login_required
def delete_from_cart(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    cart, _ = Cart.objects.get_or_create(user=request.user)

    try:
        item = CartItem.objects.get(cart=cart, book=book)
        if item.quantity > 1:
            item.quantity -= 1
            item.save()
        else:
            item.delete()
    except CartItem.DoesNotExist:
        pass

    return redirect('view_cart')

@login_required
def remove_from_cart(request, book_id):
    cart = get_object_or_404(Cart, user=request.user)
    CartItem.objects.filter(cart=cart, book_id=book_id).delete()
    return redirect('view_cart')

@login_required
def view_cart(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    return render(request, 'bookMng/cart.html', {
        'item_list': MainMenu.objects.all(),
        'cart': cart
    })


@login_required(login_url='/login')
def view_cart(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)

    cart_items = []
    cart_total = 0

    for item in cart.items.all():
        total_price = item.book.price * item.quantity
        cart_items.append({
            'book': item.book,
            'quantity': item.quantity,
            'total_price': total_price,
        })
        cart_total += total_price

    total_quantity = sum(item['quantity'] for item in cart_items)

    return render(request, 'bookMng/cart.html', {
        'item_list': MainMenu.objects.all(),
        'cart_items': cart_items,
        'cart_total': cart_total,
        'total_quantity': total_quantity,
    })
@login_required(login_url='/login')
def checkout(request):
    cart = get_object_or_404(Cart, user=request.user)

    # Clear cart items after "payment"
    cart.items.all().delete()

    return render(request, 'bookMng/checkout.html', {
        'item_list': MainMenu.objects.all(),
    })