from django.db import models
from django.conf import settings

from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill

class Review(models.Model):
    RANKS = [
        (1, '★'),
        (2, '★★'),
        (3, '★★★'),
        (4, '★★★★'),
        (5, '★★★★★'),
    ]

    # 사용자 이미지 저장할 경로 지정
    def review_image_path(instance, filename):
        return f'review_image_{instance.pk}/{filename}' 

    title = models.CharField(max_length=100)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    rank = models.IntegerField(choices=RANKS, default=5) # 리뷰평점
    is_spoiler = models.BooleanField() # 스포일러 유무
    user_upload_image = models.ImageField(upload_to=review_image_path, blank=True) # 리뷰에 유저가 업로드한 이미지
    thumbnail = ImageSpecField(source='user_upload_image', processors=[ResizeToFill(100,150)], format='JPEG', options={'quality':80}) # source필드의 이미지를 리사이징해서 별도의 작은 이미지 생성해줌
    
    movie = models.ForeignKey('movies.Movie', on_delete=models.CASCADE, related_name='reviews')  # 다른 앱에 있는 모델 참조하기!!! '앱이름.모델명'  # 리뷰가 작성된 영화 정보 
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)    # 리뷰 작성자
    like_users = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='like_reviews')    # 좋아요한 유저
    dislike_users = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='dislike_reviews')     # 싫어요한 유저

    def __str__(self):
        return f'{self.pk}: {self.title}'    


class Comment(models.Model):
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    review = models.ForeignKey(Review, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='review_comment')

    def __str__(self):
        return f'{self.pk}: {self.content}'   