#!/usr/bin/env python
import json
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


def do_endpoint_mock():
    adapter = requests_mock.Adapter()
    session.mount('mock://', adapter)

    adapter.register_uri("GET", "mock://test.com/showings",
                         text=open("./tmp/showings.json", "r").read())

    adapter.register_uri("GET", "mock://test.com/airings",
                         text=open("./tmp/airings.json", "r").read())


def get_showings(api_secret, start_date, zip_code):
    resp = session.get("mock://test.com/showings")
    showings = json.loads(resp.text)
    print(len(showings))


def get_airings(api_secret, start_datetime, line_up_id):
    resp = session.get("mock://test.com/airings")
    airings = json.loads(resp.text)
    print(len(airings))


def get_data():
    get_showings("", "", "")
    get_airings("", "", "")


if __name__ == '__main__':
    # Create engine
    db_uri = environ.get('SQLALCHEMY_DATABASE_URI')
    engine = create_engine(db_uri, echo=True)

    # Create All Tables
    Base.metadata.create_all(engine)

    do_endpoint_mock()
    get_data()
