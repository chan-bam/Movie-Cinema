import requests
import json

TMDB_API_KEY = 'e40e599e7176f5cb90028270852f4bf5'


def get_movie_datas():
    total_data = []

    # 1페이지부터 10페이지까지 (페이지당 20개, 총 200개)
    for i in range(1, 11):
        request_url = f'https://api.themoviedb.org/3/movie/popular?api_key={TMDB_API_KEY}&language=ko-KR&page={i}'
        video_url_1 = f'https://api.themoviedb.org/3/movie/'
        video_url_2 = f'/videos?api_key={TMDB_API_KEY}&language=ko-KR'
        movies = requests.get(request_url).json()

        youtube_path=str(),
        for movie in movies['results']:
            movie_id = movie['id']

            # videos 데이터 가져오기
            videos = requests.get(f'{video_url_1}{movie_id}{video_url_2}').json()

            if len(videos['results']) > 0:
                youtube_path = videos['results'][0]['key']
            else:
                youtube_path = ''

            if movie.get('release_date', ''):
                fields = {
                    'title': movie['title'],
                    'popularity': movie['popularity'],
                    'vote_count': movie['vote_count'],
                    'vote_average': movie['vote_average'],
                    'overview': movie['overview'],
                    'release_date': movie['release_date'],
                    'poster_path': movie['poster_path'],
                    'youtube_path': youtube_path,
                    'genres': movie['genre_ids'],
                }

                data = {
                    "pk": movie['id'],
                    "model": "movies.movie",
                    "fields": fields
                }

                total_data.append(data)

    with open("movie_data.json", "w", encoding="utf-8") as w:
        json.dump(total_data, w, ensure_ascii=False)

get_movie_datas()