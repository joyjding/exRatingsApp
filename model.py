from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm import sessionmaker, scoped_session
import correlation

import datetime

engine = create_engine("sqlite:///ratings2.db", echo=False)
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


    #returns pearson correlation
    def similarity(self, other_user):
        pairs = []
        user_dict = {}
        for r in self.ratings:
            user_dict[r.movie_id] = r.rating
        for r in other_user.ratings:
            if user_dict.get(r.movie_id):
                pairs.append((user_dict[r.movie_id], r.rating))
        if pairs:
            return correlation.pearson(pairs)
        else:
            return 0.0
    
    #take a single user and predict what the user would rate the movie
    #1) get the movie object?
    #2) get all the users that also rated that movie
    #3) compare all the users to the first user using similarity
    #4) sort that list
    #5) return the most similar user * similarity coefficient
    #*) check for most similar/least similar
    
    def predict_rating(self, movie_id):
        movie = session.query(Movie).get(movie_id)
        sim_list = []
        sum_product = 0
        sum_coefficients = 0
        for r in movie.ratings:
            if r.user!=self:
                print "calculating similarity for ", r.id
                sim = self.similarity(r.user)
                t = (sim, r.rating)
                if t[0]>0:
                    sum_product+=t[0]*t[1]
                    sum_coefficients+=t[0]
                    sim_list.append(t)

        if sum_coefficients == 0:
            return "You need to rate more movies before we can make a prediction!"
        else:
            return sum_product/sum_coefficients

    def get_judged(self, movie_id):
        the_eye = session.query(User).filter_by(email="thehound@ofjudgement.com").one()
        eye_rating = session.query(Rating).filter_by(user_id=the_eye.id, movie_id=movie_id).first()

        if not eye_rating:
            eye_rating = the_eye.predict_rating(movie_id)
        else:
            eye_rating = eye_rating.rating
        user_rating = session.query(Rating).filter_by(user_id=self.id, movie_id=movie_id).one()
        difference = abs(eye_rating - user_rating.rating)

        messages = ["I suppose you don't have such bad taste after all.",
                    "I regret every decision that I've ever made that has brought me to listen to your opinion",
                    "Words fail me, as your taste in movies has clearly failed you.",
                    "That movie is great. For a clown to watch. Idiot."]

        return messages[int(difference)]


class Movie(Base):
    __tablename__ = "movies"

    id = Column(Integer, primary_key=True)
    name = Column(String(64))
    release_year = Column(Integer, nullable=True)
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

    def get_ratings_distribution(self):
        ratings_count = [0, 0, 0, 0, 0]
        for r in self.ratings:
            ratings_count[r.rating-1] += 1
        return ratings_count



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
    # check if user has rated this movie before
    print "This is the user_id", user_id
    r = session.query(Rating).filter_by(user_id=user_id, movie_id=movie_id).first()
    if r:
        r.rating = rating
        session.commit()
        return
    # create new rating if user has not rated the movie
    r = Rating(movie_id=movie_id, rating=rating, user_id=user_id)
    session.add(r)
    session.commit()


def add_new_user(email, pw, age=None, zipcode=None):
    u = User(email=email, password=pw, age=age, zipcode=zipcode)
    session.add(u)
    session.commit()

def check_login(email, pw):
    u = session.query(User).filter_by(email=email, password=pw).first()
    if u:
        return u
    return None

def main():
    """In case we need this for something"""
    pass

if __name__ == "__main__":
    main()
