from django.db import models
from django.conf import settings

class Genre(models.Model):
    name = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f'{self.pk}: {self.name}'   

class Movie(models.Model):
    title = models.CharField(max_length=100)
    popularity = models.FloatField()
    vote_count = models.IntegerField()
    vote_average = models.FloatField()
    overview = models.TextField()
    release_date = models.DateField()
    production_company = models.CharField(max_length=100)
    poster_path = models.CharField(max_length=200, blank=True, null=True)
    youtube_path = models.CharField(max_length=200, blank=True)
    genres = models.ManyToManyField(Genre)
    scrap_users = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='scrap_movies')
    
    def __str__(self):
        return f'{self.pk}: {self.title}'    


class Comment(models.Model):
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="movie_comment")

    def __str__(self):
        return f'{self.pk}: {self.content}'    
