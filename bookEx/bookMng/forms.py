from django import forms
from django.forms import ModelForm
from .models import Book
from .models import Rating
from .models import Comment

class BookForm(ModelForm):
    class Meta:
        model = Book
        fields = [
            'name',
            'web',
            'price',
            'picture',
        ]

class BookSearchForm(forms.Form):
    query = forms.CharField(label='Search books', max_length=100, required=False)

class RatingForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = ['is_positive']

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'placeholder': 'Leave a comment...'}),
        }