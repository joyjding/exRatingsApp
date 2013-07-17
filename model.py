from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm import sessionmaker, scoped_session

import datetime

engine = create_engine("sqlite:///ratings.db", echo=False)
session = scoped_session(sessionmaker(bind=engine, 
                                    autocommit = False, 
                                    autoflush = False))

Base = declarative_base()
Base.query = session.query_property()

### Class declarations go here

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String(64), nullable=True)
    password = Column(String(64), nullable=True)
    age = Column(Integer, nullable=True)
    zipcode = Column(String(15), nullable=True)


class Movie(Base):
    __tablename__ = "movies"

    id = Column(Integer, primary_key=True)
    name = Column(String(64))
    released_at = Column(DateTime, nullable=True)
    imdb_url = Column(String(128), nullable=True)

    def get_avg_rating(self):
        rating_sum = 0.0
        num = 0
        for r in self.ratings:
            rating_sum += r.rating
            num += 1
        if num == 0:
            return "No ratings yet for this movie."
        return rating_sum/num


class Rating(Base):
    __tablename__ = "ratings"

    id = Column(Integer, primary_key=True)
    movie_id = Column(Integer, ForeignKey('movies.id'))
    user_id = Column(Integer, ForeignKey('users.id'))
    rating = Column(Integer)

    user = relationship("User", backref=backref("ratings", order_by=rating.desc()))
    movie = relationship("Movie", backref=backref("ratings", order_by=rating.desc())) 


### End class declarations

def add_new_rating(user_id, movie_id, rating):
    r = Rating(movie_id=movie_id, rating=rating, user_id=user_id)
    session.add(r)
    session.commit()


def add_new_user(email, pw, age=None, zipcode=None):
    u = User(email=email, password=pw, age=age, zipcode=zipcode)
    session.add(u)
    session.commit()

def check_login(email, pw):
    u = session.query(User).filter_by(email=email, password=pw).one()
    if u:
        return u.id
    return None


def main():
    """In case we need this for something"""
    pass

if __name__ == "__main__":
    main()
