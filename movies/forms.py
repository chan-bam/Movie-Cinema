from django import forms
from .models import Movie, Comment

class MovieForm(forms.ModelForm):
    class Meta:
        model= Movie
        exclude = ('scrap_users',)

from django import forms
from .models import Movie, Comment

class MovieForm(forms.ModelForm):
    class Meta:
        model= Movie
        exclude = ('scrap_users',)

class CommentForm(forms.ModelForm):
    content = forms.CharField(
        label="한줄평 남기기",
        widget=forms.Textarea(
            attrs={
                'class': 'my-content form-control',
                'placeholder': '한줄평을 작성해주세요',
                'rows': 3,
            }
        )
    )
    class Meta:
        model = Comment
        fields = ('content',)