#!/usr/bin/env python
import json
import datetime
import requests
import requests_mock
from os import environ
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import *
import pandas as pd

SHOWINGS_ENDPOINT_FMT = "https://data.tmsapi.com/v1.1/movies/showings?startDate={0}&zip={1}&api_key={2}"
AIRINGS_ENDPOINT_FMT = "http://data.tmsapi.com/v1.1/movies/airings?startDateTime={0}&lineupId={1}&api_key={2}"

session = requests.Session()

# Create engine
db_uri = environ.get('SQLALCHEMY_DATABASE_URI')
engine = create_engine(db_uri, echo=False)

# Create All Tables
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
dbSession = Session()


def do_endpoint_mock():
    """do_endpoint_mock returns mock data on api calls"""
    adapter = requests_mock.Adapter()
    session.mount('mock://', adapter)

    adapter.register_uri("GET", "mock://test.com/showings",
                         text=open("./mock/showings.json", "r").read())

    adapter.register_uri("GET", "mock://test.com/airings",
                         text=open("./mock/airings.json", "r").read())


def get_genre_or_create(genre_name):
    """get_genre_or_create returns a genre reference or creates one if it does not exist"""

    genre = dbSession.query(Genre).filter(Genre.name == genre_name).first()

    if genre:
        return genre

    genre = Genre(name=genre_name)
    dbSession.add(genre)
    return genre


def get_showings(api_secret, start_date, zip_code):
    endpoint = SHOWINGS_ENDPOINT_FMT.format(start_date, zip_code, api_secret)
    resp = session.get(endpoint)
    # resp = session.get("mock://test.com/showings") -> uncomment to use mock data

    if not resp.ok:
        raise Exception(resp.text)

    showings = json.loads(resp.text)

    theatre_movies = []

    for showing in showings:
        theatre_movie = TheatreMovie()
        theatre_movie.title = showing.get("title", "")
        theatre_movie.releaseYear = showing.get("releaseYear", "")
        theatre_movie.description = showing.get("shortDescription", "")

        # add this movie to genres using backrefs
        for genre_name in showing.get("genres", []):
            # get a reference to the genre
            genre = get_genre_or_create(genre_name)
            genre.theatre_movies.append(theatre_movie)

        theatre_movie.theatres = []
        for showtime in showing.get("showtimes", []):
            theatre = showtime.get("theatre", None)
            if not theatre:
                continue
            theatre_movie.theatres.append(
                Theatre(theatre_id=theatre["id"], name=theatre["name"]))

        theatre_movies.append(theatre_movie)

    dbSession.add_all(theatre_movies)
    dbSession.commit()


def get_airings(api_secret, start_datetime, line_up_id):
    endpoint = AIRINGS_ENDPOINT_FMT.format(
        start_datetime, line_up_id, api_secret)

    resp = session.get(endpoint)
    # resp = session.get("mock://test.com/airings") -> uncomment to use mock data

    if not resp.ok:
        raise Exception(resp.text)

    airings = json.loads(resp.text)

    tv_movies = []

    for airing in airings:
        tv_movie = TvMovie()
        program = airing.get("program", None)
        if not program:
            continue

        tv_movie.title = program.get("title", "")
        tv_movie.releaseYear = program.get("releaseYear", "")
        tv_movie.description = program.get("shortDescription", "")

        # add tv_movie to genres using backrefs
        for genre_name in program.get("genres", []):
            genre = get_genre_or_create(genre_name)
            genre.tv_movies.append(tv_movie)

        tv_movie.channels = []
        for channel_name in airing.get("channels", []):
            tv_movie.channels.append(Channel(name=channel_name))

        tv_movies.append(tv_movie)

    dbSession.add_all(tv_movies)
    dbSession.commit()


def poll_data():
    api_secret = environ.get('API_SECRET')
    get_showings(api_secret, get_date(), "78701")
    get_airings(api_secret, get_date_time(), "USA-TX42500-X")


def get_date():
    return datetime.datetime.today().strftime('%Y-%m-%d')


def get_date_time():
    return datetime.datetime.now().strftime("%Y-%m-%dT%H:%Mz")


def get_top_genres(count):
    # get all genres
    genres = dbSession.query(Genre).all()

    df_theatre_movie = pd.DataFrame(
        columns=["title", "genre", "releaseYear", "description"])

    df_tv_movie = pd.DataFrame(
        columns=["title", "genre", "releaseYear", "description"])

    # Fill the dataframes
    for genre in genres:
        for theatre_movie in genre.theatre_movies:
            df_theatre_movie = df_theatre_movie.append({
                "title": theatre_movie.title,
                "genre": genre.name,
                "releaseYear": theatre_movie.releaseYear,
                "description": theatre_movie.description
            }, ignore_index=True)

        for tv_movie in genre.tv_movies:
            df_tv_movie = df_tv_movie.append({
                "title": tv_movie.title,
                "genre": genre.name,
                "releaseYear": tv_movie.releaseYear,
                "description": tv_movie.description
            }, ignore_index=True)

    merged_movies = pd.concat([df_theatre_movie, df_tv_movie])

    # Group by genre
    grouped = merged_movies.groupby("genre")

    top_labels = grouped.size().nlargest(count).index

    top_genre_movies = []
    for label in top_labels:
        movies_under_genre = merged_movies[merged_movies.genre == label]
        top_genre_movies.append({label: movies_under_genre})

    return top_genre_movies


if __name__ == '__main__':
    """
    #By default, pandas truncates large data at the terminal, 
    #prevent that behaviour by uncommenting these

    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)
    pd.set_option('display.max_colwidth', -1)
    """

    poll_data()  # replace with do_endpoint_mock() to use mock data
    top_genre_movies = get_top_genres(5)
    print(top_genre_movies)
