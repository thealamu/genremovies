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

SHOWINGS_ENDPOINT_FMT = "https://data.tmsapi.com/v1.1/movies/showings?startDate={0}&zip={1}&api_key={2}"
AIRINGS_ENDPOINT_FMT = "http://data.tmsapi.com/v1.1/movies/airings?startDateTime={0}&lineupId={1}&api_key={2}"

session = requests.Session()
dbSession = None


def do_endpoint_mock():
    adapter = requests_mock.Adapter()
    session.mount('mock://', adapter)

    adapter.register_uri("GET", "mock://test.com/showings",
                         text=open("./tmp/showings.json", "r").read())

    adapter.register_uri("GET", "mock://test.com/airings",
                         text=open("./tmp/airings.json", "r").read())


def get_showings(api_secret, start_date, zip_code):
    endpoint = SHOWINGS_ENDPOINT_FMT.format(start_date, zip_code, api_secret)
    resp = session.get(endpoint)
    if not resp.ok:
        raise Exception(resp.text)

    showings = json.loads(resp.text)

    theatre_movies = []

    for showing in showings:
        theatre_movie = TheatreMovie()
        theatre_movie.title = showing.get("title", "")
        theatre_movie.releaseYear = showing.get("releaseYear", "")
        theatre_movie.description = showing.get("shortDescription", "")
        theatre_movie.genres = []
        for genre_name in showing.get("genres", []):
            theatre_movie.genres.append(Genre(name=genre_name))

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
        tv_movie.genres = []
        for genre_name in program.get("genres", []):
            tv_movie.genres.append(Genre(name=genre_name))

        tv_movie.channels = []
        for channel_name in airing.get("channels", []):
            tv_movie.channels.append(Channel(name=channel_name))

        print(tv_movie.channels)
        tv_movies.append(tv_movie)

    dbSession.add_all(tv_movies)
    dbSession.commit()


def get_data():
    api_secret = environ.get('API_SECRET')
    get_showings(api_secret, get_date(), "78701")
    get_airings(api_secret, get_date_time(), "USA-TX42500-X")


def get_date():
    return datetime.datetime.today().strftime('%Y-%m-%d')


def get_date_time():
    return datetime.datetime.now().strftime("%Y-%m-%dT%H:%Mz")


def get_top_genres():
    pass


if __name__ == '__main__':
    # Create engine
    db_uri = environ.get('SQLALCHEMY_DATABASE_URI')
    engine = create_engine(db_uri, echo=False)

    # Create All Tables
    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    dbSession = Session()

    do_endpoint_mock()
    get_data()
