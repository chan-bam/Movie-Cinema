from django.http.response import JsonResponse, HttpResponse
from django.shortcuts import redirect, render, get_object_or_404
from .forms import CustomUserCreationForm, CustomUserChangeForm
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.views.decorators.http import require_http_methods, require_POST, require_safe
from django.contrib.auth.decorators import login_required

from django.contrib import messages # 메시지 관련


@require_http_methods(['GET', 'POST'])
def signup(request):
    if request.user.is_authenticated:
        return redirect('movies:index')
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            auth_login(request, user, backend='django.contrib.auth.backends.ModelBackend') # allauth 관련해서 인증 multiple authentication backend (중첩) 관련 설정 추가 
            return redirect('accounts:profile', user.username)
    else:
        form = CustomUserCreationForm()
    context = {
        'form':form,
    }
    return render(request, 'accounts/signup.html', context)

@require_http_methods(['GET', 'POST'])
def login(request):
    if request.user.is_authenticated:
        return redirect('movies:index')

    if request.method == 'POST':
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            auth_login(request, form.get_user())
            return redirect(request.GET.get('next') or 'movies:index')
    else:
        form = AuthenticationForm()
    context = {
        'form': form,
    }
    return render(request, 'accounts/login.html', context)

@require_POST
def logout(request):
    if request.user.is_authenticated:
        auth_logout(request)
    return redirect('movies:index')

@require_POST
def signout(request):
    if request.user.is_authenticated:
        request.user.delete()
        auth_logout(request)
    return redirect('movies:index')

@login_required
@require_http_methods(['GET', 'POST'])
def update(request):
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('accounts:profile', request.user.username)
    else:
        form = CustomUserChangeForm(instance=request.user)
    context = {
        'form':form,
    }
    return render(request, 'accounts/update.html', context)

@login_required
@require_http_methods(['GET', 'POST'])
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            return redirect('movies:index')
    else:
        form = PasswordChangeForm(request.user)
    context = {
        'form':form,
    }
    return render(request, 'accounts/change_password.html', context)

@require_safe
def profile(request, username):
    person = get_object_or_404(get_user_model(), username=username)
    if person.is_staff and not request.user.is_staff: # staff권한 가진 경우 프로필페이지 접근하지 못하도록 함 # staff는 접근 가능 가능
        # messages.warning(request, "권한이 없습니다.") # 권한 없을때 메시지를 띄우고 요청을 보내기 이전 페이지로 redirect하는 방법을 고민....  
        return redirect('movies:index')
    context = {
        'person': person,
    }
    return render(request, 'accounts/profile.html', context)


@require_POST
def follow(request, user_pk):
    if request.user.is_authenticated:
        person = get_object_or_404(get_user_model(), pk=user_pk)
        user = request.user
        if person != user:
            if person.followers.filter(pk=user.pk).exists():
                # 팔로우 끊음
                person.followers.remove(user)
                isFollowed = False
            else:
                # 팔로우 신청
                person.followers.add(user)
                isFollowed = True
            context = {
                'isFollowed': isFollowed,
                'followings_count': person.followings.count(),
                'followers_count': person.followers.count(),
            }
            return JsonResponse(context)
    return HttpResponse(status=401) # 로그인 안했는데 follow 요청을 보낸 경우 # 에러를 발생시킴


@require_safe
def follow_list(request, username):
    person = get_object_or_404(get_user_model(), username=username)
    if person.is_staff and not request.user.is_staff: # staff권한 가진 경우 프로필페이지 접근하지 못하도록 함
        # messages.warning(request, "권한이 없습니다.") # 권한 없을때 메시지를 띄우고 요청을 보내기 이전 페이지로 redirect하는 방법을 고민....
        return redirect('movies:index')
    context = {
        'person': person,
    }
    return render(request, 'accounts/follow_list.html', context)