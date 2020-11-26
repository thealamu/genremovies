from sqlalchemy import Table, ForeignKey, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

tmg_association_table = Table('theatre_movie_genre_association', Base.metadata,
                              Column('movie_id', Integer,
                                     ForeignKey('theatre_movies.id')),
                              Column('genre_id', String,
                                     ForeignKey('genres.name'))
                              )

tth_association_table = Table('theatre_movie_theatre_association', Base.metadata,
                              Column('movie_id', Integer,
                                     ForeignKey('theatre_movies.id')),
                              Column('theatre_id', String,
                                     ForeignKey('theatre.id'))
                              )

amg_association_table = Table('tv_movie_genre_association', Base.metadata,
                              Column('movie_id', Integer,
                                     ForeignKey('tv_movies.id')),
                              Column('genre_id', String,
                                     ForeignKey('genres.name'))
                              )


ttv_association_table = Table('tv_movie_channel_association', Base.metadata,
                              Column('movie_id', Integer,
                                     ForeignKey('tv_movies.id')),
                              Column('channel_id', String,
                                     ForeignKey('channel.name'))
                              )


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


class Genre(Base):
    __tablename__ = "genres"

    name = Column(
        String(32),
        primary_key=True,
        nullable=False
    )

    def __repr__(self):
        return self.name


class Theatre(Base):
    __tablename__ = "theatres"

    id = Column(
        String(32),
        primary_key=True,
        nullable=False
    )

    name = Column(
        String(200)
    )

    def __repr__(self):
        return self.name


class Channel(Base):
    __tablename__ = "channels"

    name = Column(
        String(32),
        primary_key=True
    )

    def __repr__(self):
        return self.name


class TheatreMovie(Movie, Base):
    __tablename__ = "theatre_movies"


class TvMovie(Movie, Base):
    __tablename__ = "tv_movies"
