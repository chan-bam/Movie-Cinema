from django import forms
from .models import Review, Comment


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ('title', 'rank', 'content', 'is_spoiler', 'user_upload_image',) # movie는 제외

class ReviewNewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ('title', 'rank', 'content', 'is_spoiler', 'user_upload_image', 'movie') # movie 포함

class CommentForm(forms.ModelForm):
    content = forms.CharField(
        label="댓글",
        widget=forms.Textarea(
            attrs={
                'class': 'my-content form-control',
                'placeholder': '댓글 작성하기',
                'rows': 3,
            }
        )
    )
    class Meta:
        model = Comment
        fields = ('content',)