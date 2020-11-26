from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Movie():
    id = Column(
        Integer,
        primary_key=True,
        nullable=False
    )

    title = Column(
        String(100),
        nullable=False
    )

    releaseYear = Column(
        String(4)
    )

    description = Column(
        String(200)
    )

    def __repr__(self):
        return "(%s, %s)" % self.title, self.releaseYear


class TheatreMovie(Movie, Base):
    __tablename__ = "theatre_movies"


class TvMovie(Movie, Base):
    __tablename__ = "tv_movies"
