import pandas as pd
import requests
import urllib.request, json
import numpy as np

# Define the URLs for movie data
movies_url = "https://liangfgithub.github.io/MovieData/movies.dat?raw=true"
ratings_url = "https://liangfgithub.github.io/MovieData/ratings.dat?raw=true"
with urllib.request.urlopen('https://red-smartbit.s3.us-west-2.amazonaws.com/test.json') as url:
    data = json.load(url)

# Fetch the data from the URL
movies_response = requests.get(movies_url)
ratings_response = requests.get(ratings_url)

aux_df = pd.DataFrame.from_dict(data)
S = aux_df.values
S = S.astype('float64')

# Split the data into lines and then split each line using "::"
movie_lines = movies_response.text.split('\n')
movie_data = [line.split("::") for line in movie_lines if line]
ratings_lines = ratings_response.text.split('\n')
ratings_data = [line.split("::") for line in ratings_lines if line]

# Create DataFrames from the movie data
movies = pd.DataFrame(movie_data, columns=['movie_id', 'title', 'genres'])
movies['movie_id'] = movies['movie_id'].astype(int)
ratings = pd.DataFrame(ratings_data, columns=['user_id', 'movie_id', 'rating', 'timestamp'])
ratings['movie_id'] = ratings['movie_id'].astype(int)
ratings['user_id'] = ratings['user_id'].astype(int)
ratings['rating'] = ratings['rating'].astype(int)
merged_data = pd.merge(movies, ratings, on='movie_id')

genres = list(
    sorted(set([genre for genres in movies.genres.unique() for genre in genres.split("|")]))
)

genre_recs = {}

def get_displayed_movies():
    return movies.head(100)

def get_recommended_movies(new_user_ratings):
    return movies.head(10)

# returns a list of most watched movies in a genre
# input: genre (str)
# output: list of movies
def most_watched_movies(genre):
    genre_filtered_data = merged_data[merged_data['genres'].str.contains(genre)]
    ratings_per_movie = genre_filtered_data.groupby('movie_id')['rating'].count().reset_index()
    ratings_per_movie.columns = ['movie_id', 'num_ratings']
    ratings_per_movie_with_titles = pd.merge(ratings_per_movie, movies[['movie_id', 'title']], on='movie_id')
    return ratings_per_movie_with_titles

# returns a list of highly rated movies in a genre
# input: genre (str)
# output: list of movies
def highly_rated_movies(genre):
    genre_filtered_data = merged_data[merged_data['genres'].str.contains(genre)]
    average_rating_per_movie = genre_filtered_data.groupby('movie_id')['rating'].mean().reset_index()
    average_rating_per_movie.columns = ['movie_id', 'avg_rating']
    average_rating_per_movie_with_titles = pd.merge(average_rating_per_movie, movies[['movie_id', 'title']], on='movie_id')
    return average_rating_per_movie_with_titles

# return a list of movies that are ranked by most watched and highly rated
# input: genre (str), number of movies (int)
# output: list of movies
def ranking(genre, n):
    popularity = most_watched_movies(genre)
    avg_rating = highly_rated_movies(genre)
    rank = pd.merge(popularity, avg_rating, on=['movie_id', 'title'])

    # popularity 1/3, avg_rating 2/3
    rank['score'] = rank['num_ratings'] / 3 + rank['avg_rating'] * 2 / 3
    # scale
    rank['score'] = rank['score'] / rank['score'].max()
    top_n_movies = rank.sort_values(by='score', ascending=False).head(n)
    genre_recs[genre] = top_n_movies
    return top_n_movies

def get_popular_movies(genre: str):
    if genre in genre_recs:
        return genre_recs[genre]
    else:
        return ranking(genre, 10)

def myIBCF(w):
    nan_indices = np.argwhere(np.isnan(w)).flatten()
    recommendations = {}
    for l in nan_indices:
        l_neighbors = np.argwhere(~np.isnan(S[l])).flatten()
        w_top = w[l_neighbors]

        mask = np.where(np.isnan(w_top), 0, 1)
        fac_1 = 1 / np.nansum(S[l, l_neighbors] * mask.T)
        fac_2 = np.nansum(S[l, l_neighbors] * w[l_neighbors])
        val = fac_1 * fac_2
        recommendations[int(l)] = val if not np.isnan(val) else 0
    r_sorted = sorted(recommendations.items(), key=lambda x: x[1])[::-1]
    return r_sorted[: 10]

