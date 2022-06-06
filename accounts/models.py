from django.db import models
from django.contrib.auth.models import AbstractUser
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFill

# 프로필 이미지 경로 설정

class User(AbstractUser):
    def profile_image_path(instance, filename):
        return f'user_profile_{instance.pk}/{filename}'

    nickname = models.CharField(max_length=10)
    followings = models.ManyToManyField('self', symmetrical=False, related_name="followers")
    # profile_image = models.ImageField(upload_to=profile_image_path, blank=True)
    profile_image = ProcessedImageField(
        blank=True,
        upload_to=profile_image_path,
        processors=[ResizeToFill(150, 150)],
        format='JPEG',
        options={'quality': 100}
    )

