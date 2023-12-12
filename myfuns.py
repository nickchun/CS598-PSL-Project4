import pandas as pd
import requests

# Define the URLs for movie data
movies_url = "https://liangfgithub.github.io/MovieData/movies.dat?raw=true"
ratings_url = "https://liangfgithub.github.io/MovieData/ratings.dat?raw=true"

# Fetch the data from the URL
movies = requests.get(movies_url)
ratings = requests.get(ratings_url)

# Split the data into lines and then split each line using "::"
movie_lines = response.text.split('\n')
movie_data = [line.split("::") for line in movie_lines if line]
ratings_lines = response.text.split('\n')
ratings_data = [line.split("::") for line in ratings_lines if line]

# Create DataFrames from the movie data
movies = pd.DataFrame(movie_data, columns=['movie_id', 'title', 'genres'])
movies['movie_id'] = movies['movie_id'].astype(int)
ratings = pd.DataFrame(ratings_data, columns=['user_id', 'movie_id', 'rating', 'timestamp'], dtype=int)

genres = list(
    sorted(set([genre for genres in movies.genres.unique() for genre in genres.split("|")]))
)

def get_displayed_movies():
    return movies.head(100)

def get_recommended_movies(new_user_ratings):
    return movies.head(10)

def get_popular_movies(genre: str):
    if genre == genres[1]:
        return movies.head(10)
    else: 
        return movies[10:20]