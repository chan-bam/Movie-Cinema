from django.shortcuts import get_object_or_404, redirect, render
from django.http.response import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from community.forms import CommentForm, ReviewForm, ReviewNewForm
from .models import Review, Comment
from movies.models import Movie # 다른 앱의 model을 참조할 때....
from django.views.decorators.http import require_POST, require_http_methods, require_safe

from django.core.paginator import Paginator 

@require_safe   # index 페이지네이터 이용한 페이징
def index(request):
    reviews = Review.objects.order_by('-pk')
    paginator = Paginator(reviews, 5) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'reviews': page_obj,
    }
    return render(request, 'community/index.html', context)

@login_required
@require_http_methods(['GET', 'POST'])
def create(request, movie_pk): # 리뷰 생성하는 경로에 따라 movie(FK) 부분 정보 가져오는 부분 수정해야 할 수 있음
    if request.method == 'POST':
        if movie_pk: # pk 0 아닌 값이면 : 영화메뉴에서 타고 들어간 경우
            form = ReviewForm(request.POST, request.FILES)
        else: # pk 0이면 : 외부 메뉴에서 들어간 경우 : 영화 선택하도록
            form = ReviewNewForm(request.POST, request.FILES)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            if movie_pk: # pk 0 아닌 값이면 : 영화메뉴에서 타고 들어간 경우
                movie = get_object_or_404(Movie, pk=movie_pk)
                review.movie = movie  # 영화정보 자동 저장
            review.save()
            return redirect('community:detail', review.pk)
    else:
        if movie_pk:  # pk 0 아닌 값이면 : 영화메뉴에서 타고 들어간 경우
            form = ReviewForm()
            movie_title = get_object_or_404(Movie, pk=movie_pk).title
        else:
            form = ReviewNewForm()  # pk 0이면 : 외부 메뉴에서 들어간 경우 : 영화 선택하도록
            movie_title = False
    context = {
        'form': form,
        'movie_title': movie_title,
    }
    return render(request, 'community/create.html', context)

@require_safe
def detail(request, review_pk):
    review = get_object_or_404(Review, pk=review_pk)
    comments = review.comment_set.all()
    comment_form = CommentForm()
    context = {
        'review': review,
        'comment_form': comment_form,
        'comments': comments,
    }
    return render(request, 'community/detail.html', context)

@login_required
@require_http_methods(['GET', 'POST'])
def update(request, review_pk): # 리뷰 수정 
    review = get_object_or_404(Review, pk=review_pk)
    if request.user == review.user: # 작성자만 영화정보 수정 가능
        if request.method == 'POST':
            form = ReviewForm(request.POST, request.FILES, instance=review) # 미디어 관련 설정 반영
            if form.is_valid():
                review = form.save()
                return redirect('community:detail', review.pk)
        else:
            form = ReviewForm(instance=review)
        context = {
            'form': form,
            'review': review, # 리뷰정보도 보냄.... page_title에서 활용
        }
        return render(request, 'community/update.html', context)
    return redirect('community:detail', review_pk) # 작성자가 아닌 user가 url로 수정 시도할 경우 해당 영화의 detail 페이지를 보여준다

@require_POST
def delete(request, review_pk): # 리뷰 삭제 # 관리자도 가능
    if request.user.is_authenticated:
        review = get_object_or_404(Review, pk=review_pk)
        if request.user == review.user or request.user.is_staff: # 작성자거나 스태프 권한이 있으면
            review.delete() # 리뷰 삭제
        return redirect('community:index') # 삭제에 성공하면 index로

@login_required
@require_POST
def comment_create(request, review_pk):
    review = get_object_or_404(Review, pk=review_pk)
    comment_form = CommentForm(request.POST)
    if comment_form.is_valid():
        comment = comment_form.save(commit=False)
        comment.review = review
        comment.user = request.user
        comment.save()
        return redirect('community:detail', review.pk)
    context = {
        'comment_form': comment_form,
        'review': review,
        'comments': review.comment_set.all(),
    }
    return render(request, 'community/detail.html', context)

@require_POST
def comment_delete(request, review_pk, comment_pk): # 코멘트 삭제 # staff도 가능
    if request.user.is_authenticated:
        comment = get_object_or_404(Comment, pk=comment_pk)
        if request.user == comment.user or request.user.is_staff: # staff권한이 있으면 다른 user의 댓글도 삭제 가능하도록 작성
            comment.delete()
    return redirect('community:detail', review_pk)

@login_required
@require_http_methods(['GET', 'POST'])
def comment_update(request, review_pk, comment_pk): # 코멘트 수정
    comment = get_object_or_404(Comment, pk=comment_pk)
    if request.user == comment.user: # 작성자만 코멘트 수정 가능
        if request.method == 'POST':
            comment_form = CommentForm(request.POST, instance=comment)
            if comment_form.is_valid():
                comment_form.save()
                return redirect('community:detail', review_pk)
        else:
            comment_form = CommentForm(instance=comment)
        context = {
            'comment': comment,
            'comment_form': comment_form,
        }
        return render(request, 'community/comment_update.html', context)
    return redirect('community:detail', review_pk)


@require_POST
def like(request, review_pk): # 좋아요 기능
    if request.user.is_authenticated:
        review = get_object_or_404(Review, pk=review_pk)
        user = request.user
        cancel_dislike = False

        if review.like_users.filter(pk=user.pk).exists():
            review.like_users.remove(user) # 좋아요 취소
            isLiked = False
        else:
            review.like_users.add(user) # 좋아요 누름
            isLiked = True
            if review.dislike_users.filter(pk=user.pk).exists(): # 싫어요에 있으면.. (이미 싫어요를 했는데 좋아요를 누른 경우)
                review.dislike_users.remove(user) # 싫어요는 취소
                cancel_dislike = True
        context = {
            'isLiked': isLiked,
            'like_count': review.like_users.count(),
            'cancel_dislike': cancel_dislike,
            'dislike_count': review.dislike_users.count(),
        }
        return JsonResponse(context)
    return HttpResponse(status=401)

@require_POST
def dislike(request, review_pk): # 싫어요 기능
    if request.user.is_authenticated:
        review = get_object_or_404(Review, pk=review_pk)
        user = request.user
        cancel_like = False

        if review.dislike_users.filter(pk=user.pk).exists():
            review.dislike_users.remove(user) # 싫어요 취소
            isDisliked = False
        else:
            review.dislike_users.add(user) # 싫어요 누름
            isDisliked = True
            if review.like_users.filter(pk=user.pk).exists(): # 좋아요에 있으면.. (이미 좋아요를 했는데 싫어요를 누른 경우)
                review.like_users.remove(user) # 좋아요는 취소
                cancel_like = True
        context = {
            'isDisliked': isDisliked,
            'dislike_count': review.dislike_users.count(),
            'cancel_like': cancel_like,
            'like_count': review.like_users.count(),
        }
        return JsonResponse(context)
    return HttpResponse(status=401)