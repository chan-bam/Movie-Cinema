from django.http.response import JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_safe, require_POST, require_http_methods
from django.contrib.auth.decorators import login_required
from .models import Movie, Comment
from .forms import MovieForm, CommentForm
from django.core.paginator import Paginator
from django.core import serializers
from django.http import HttpResponse

from django.db.models import Q
from django.db.models import Avg, Count

import random

import requests

TMDB_API_KEY = 'e40e599e7176f5cb90028270852f4bf5'

@require_safe
def index(request): # 인피니티 스크롤 기능 반영
    movies = Movie.objects.order_by('-popularity')
    # print(len(movies))
    paginator = Paginator(movies, 20) # 20개씩 잘라서 가져오기
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    # print(len(page_obj))

    # /movies/?page=2 ajax 요청 => json
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        data = serializers.serialize('json', page_obj)
        return HttpResponse(data, content_type='application/json')
    # /movies/ 첫번째 페이지 요청 => html
    else:
        context = {
            'movies': page_obj,
        }
        return render(request, 'movies/index.html', context)


@require_safe
def movie_list(request, option):   # 정렬 기능 반영 # 페이지네이션으로 넘어가도록 처리하려했으나 구현에 실패해서 그냥 인피니티스크롤 유지   
    if option == 1:
        movies = Movie.objects.order_by('title') 
    elif option == 2: # 최신순
        movies = Movie.objects.order_by('-release_date')
    elif option == 3: # 평점순
        movies = Movie.objects.order_by('-vote_average')
    elif option == 4: # 스크랩 많은 순
        movies = Movie.objects.annotate(scrap_count=Count('scrap_users')).order_by('-scrap_count', '-popularity')
    else: # 기본값은 인기순
        movies = Movie.objects.order_by('-popularity')

    paginator = Paginator(movies, 12) # 12개씩 잘라서 가져오기
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    # print(len(page_obj))

    context = {
        'movies': page_obj,
    }
    return render(request, 'movies/movie_list.html', context)


@require_safe
def detail(request, movie_pk):
    movie = get_object_or_404(Movie, pk=movie_pk)
    comment_form = CommentForm()
    comments = movie.comment_set.all()
    reviews = movie.reviews.all()[:5] # 영화에 달린 리뷰 정보 5개 보냄
    reviewer_rank = movie.reviews.all().aggregate(Avg('rank'))['rank__avg'] # 리뷰어 평점 추가
    reviewer_count = movie.reviews.all().count() # 리뷰어 수 추가
    
    context = {
        'movie': movie,
        'comment_form': comment_form,
        'comments': comments,
        'reviews': reviews,
        'reviewer_rank': reviewer_rank,
        'reviewer_count': reviewer_count,
    }
    return render(request, 'movies/detail.html', context)

@login_required
@require_http_methods(['GET', 'POST'])
def create(request):
    if request.user.is_staff:
        if request.method == 'POST': # 스태프만 영화정보 작성 가능
            form = MovieForm(request.POST)
            if form.is_valid():
                movie = form.save()
                return redirect('movies:detail', movie.pk)
        else:
            form = MovieForm()
        context = {
            'form': form,
        }
        return render(request, 'movies/create.html', context)
    return redirect('movies:index')

@login_required
@require_http_methods(['GET', 'POST'])
def update(request, movie_pk):
    if request.user.is_staff: # 스태프만 영화정보 수정 가능
        movie = get_object_or_404(Movie, pk=movie_pk)
        if request.method == 'POST':
            form = MovieForm(request.POST, instance=movie)
            if form.is_valid():
                movie = form.save()
                return redirect('movies:detail', movie.pk)
        else:
            form = MovieForm(instance=movie)
        context = {
            'form': form,
            'movie_title': movie.title, # 영화제목정보도 보냄 : page_title에서 활용
        }
        return render(request, 'movies/update.html', context)
    return redirect('movies:detail', movie_pk) # 스태프 아닌 user가 url로 수정 시도할 경우... 로그인 후 해당 영화의 detail 페이지를 보여준다


@require_POST
def delete(request, movie_pk):
    if request.user.is_staff: # 스태프만 영화정보 삭제 가능
        movie = get_object_or_404(Movie, pk=movie_pk)
        movie.delete()
    return redirect('movies:index')

@login_required
@require_POST
def comment_create(request, movie_pk):
    movie = get_object_or_404(Movie, pk=movie_pk)
    comment_form = CommentForm(request.POST)
    if comment_form.is_valid():
        comment = comment_form.save(commit=False)
        comment.movie = movie
        comment.user = request.user
        comment.save()
    return redirect('movies:detail', movie_pk)

@require_POST
def comment_delete(request, movie_pk, comment_pk):
    if request.user.is_authenticated:
        comment = get_object_or_404(Comment, pk=comment_pk)
        if request.user == comment.user or request.user.is_staff: # staff권한이 있으면 다른 user의 댓글도 삭제 가능하도록 작성
            comment.delete()
    return redirect('movies:detail', movie_pk)

@login_required
@require_http_methods(['GET', 'POST'])
def comment_update(request, movie_pk, comment_pk): # 한줄평 수정
    comment = get_object_or_404(Comment, pk=comment_pk)
    if request.user == comment.user: # 작성자만 한줄평 수정 가능
        if request.method == 'POST':
            comment_form = CommentForm(request.POST, instance=comment)
            if comment_form.is_valid():
                comment_form.save()
                return redirect('movies:detail', movie_pk)
        else:
            movie = get_object_or_404(Movie, pk=movie_pk) # 수정하는 영화정보 가져와서 form에 보여줌
            comment_form = CommentForm(instance=comment)
        context = {
            'comment': comment,
            'comment_form': comment_form,
            'movie_title': movie.title,  # 수정하는 영화정보 제목만 가져와서 form에 보여줌
        }
        return render(request, 'movies/comment_update.html', context)
    return redirect('movies:detail', movie_pk)

@require_POST
def scraps(request, movie_pk):
    if request.user.is_authenticated:
        movie = get_object_or_404(Movie, pk=movie_pk)
        if movie.scrap_users.filter(pk=request.user.pk).exists(): # 스크랩 한 경우
            movie.scrap_users.remove(request.user)
            isScraped = False
        else: # 스크랩 하지 않은 경우
            movie.scrap_users.add(request.user)
            isScraped = True
        context = {
            'isScraped': isScraped,
            'scrap_count': movie.scrap_users.count(),
        }
        return JsonResponse(context)
    return HttpResponse(status=401)
    
@require_safe
def recommended(request, options):

    def real_random_movies(): # 가지고 있는 데이터 중에서 랜덤으로 10개 보여주는 함수
        if options:
            if options == 1:
                movies = Movie.objects.order_by('title')
            if options == 2:
                movies = Movie.objects.order_by('-release_date')
            if options == 3:
                movies = Movie.objects.order_by('-vote_average')
        else:
            movies = Movie.objects.order_by('-popularity')

        random_nums = random.sample(range(0, len(movies)), 12)
        random_nums.sort()
        for i in random_nums:
            random_movies.append(movies[i])
    
    def sort_tmdb(tmdb_movies):
        if options: # 제목순 # 개봉일순 # 평점순
            if options == 1:
                sorted_movies = sorted(tmdb_movies, key=lambda product: product['title'])
            elif options == 2:
                sorted_movies = sorted(tmdb_movies, key=lambda product: product['released_date'], reverse=True)
            elif options == 3:
                sorted_movies = sorted(tmdb_movies, key=lambda product: product['vote_average'], reverse=True)

        else: # 인기순
            sorted_movies = sorted(tmdb_movies, key=lambda product: product['popularity'], reverse=True)
        return sorted_movies

    random_movies = []
    tmdb_base = False

    if not request.user.is_authenticated or not request.user.scrap_movies.all(): # 로그인하지 않았거나 스크랩한 영화가 없을 때
        real_random_movies() # db 데이터에서 랜덤으로 10개 보여준다
    
    else: # 로그인 했고 스크랩한 영화가 있을 때
        try: # tmdb 요청시 에러 발생시
            random_num = random.randrange(0, request.user.scrap_movies.all().count()) # 스크랩한 영화의 인덱스 중에서 한개를 랜덤하게 가져온다
            random_movie_id = request.user.scrap_movies.all()[random_num].pk # 랜덤으로 가져온 인덱스 번호의 pk를 추출한다
            request_url = f'https://api.themoviedb.org/3/movie/{random_movie_id}/recommendations?api_key=e40e599e7176f5cb90028270852f4bf5&language=ko' # tmdb로 추천 영화 요청을 보낸다
            random_movies_info = requests.get(request_url).json()

            if random_movies_info['results']: # tmdb로 받은 추천 영화 데이터의 결과가 비어있지 않은 값이면
                random_movies = random_movies_info['results'] # tmdb 기준 추천 영화를 보여준다
                random_movies = sort_tmdb(random_movies)
                tmdb_base = True
            else: # tmdb 추천영화가 없을 때(results가 비어있을 때)
                real_random_movies() # db 데이터에서 랜덤으로 10개 보여준다
        except: # 에러 발생시 
            real_random_movies() # db 데이터에서 랜덤으로 10개 보여준다

    context = {
        'random_movies': random_movies,
        'tmdb_base': tmdb_base
    }
    return render(request, 'movies/recommended.html', context)

def movie_search(request):
    keyword = request.GET.get('message')
    if keyword == '':
        movies = []
    else:
        movies = Movie.objects.filter(Q(title__contains=keyword)|Q(overview__contains=keyword))

    context = {
        'keyword': keyword,
        'movies': movies,
    }
    return render(request, 'movies/movie_search.html', context)