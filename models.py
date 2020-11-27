from sqlalchemy import Table, ForeignKey, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

thmg_association_table = Table('theatre_movie_genre_association', Base.metadata,
                               Column('movie_id', Integer,
                                      ForeignKey('theatre_movies.id')),
                               Column('genre_id', Integer,
                                      ForeignKey('genres.id'))
                               )

thth_association_table = Table('theatre_movie_theatre_association', Base.metadata,
                               Column('movie_id', Integer,
                                      ForeignKey('theatre_movies.id')),
                               Column('theatre_id', Integer,
                                      ForeignKey('theatres.id'))
                               )

tvmg_association_table = Table('tv_movie_genre_association', Base.metadata,
                               Column('movie_id', Integer,
                                      ForeignKey('tv_movies.id')),
                               Column('genre_id', Integer,
                                      ForeignKey('genres.id'))
                               )


tvch_association_table = Table('tv_movie_channel_association', Base.metadata,
                               Column('movie_id', Integer,
                                      ForeignKey('tv_movies.id')),
                               Column('channel_id', Integer,
                                      ForeignKey('channels.id'))
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

    id = Column(
        Integer,
        primary_key=True,
        nullable=False
    )

    name = Column(
        String(32)
    )

    def __repr__(self):
        return self.name


class Theatre(Base):
    __tablename__ = "theatres"

    id = Column(
        Integer,
        primary_key=True,
        nullable=False
    )

    theatre_id = Column(
        String(32),
    )

    name = Column(
        String(200)
    )

    def __repr__(self):
        return self.name


class Channel(Base):
    __tablename__ = "channels"

    id = Column(
        Integer,
        primary_key=True
    )

    name = Column(
        String(32)
    )

    def __repr__(self):
        return self.name


class TheatreMovie(Movie, Base):
    __tablename__ = "theatre_movies"

    # Relationships
    genres = relationship("Genre", backref="theatre_movies",
                          secondary=thmg_association_table)

    theatres = relationship("Theatre", secondary=thth_association_table)


class TvMovie(Movie, Base):
    __tablename__ = "tv_movies"

    # Relationships
    genres = relationship("Genre", backref="tv_movies",
                          secondary=tvmg_association_table)

    channels = relationship("Channel", secondary=tvch_association_table)
