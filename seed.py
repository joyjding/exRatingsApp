import model
import csv
from datetime import datetime
import time

def load_users(session):
    filename = "seed_data/u.user"
    with open(filename) as csvfile:
        data = csv.reader(csvfile, delimiter="|")
        for row in data:
            new_user = model.User(id=row[0], age=row[1], zipcode=row[4])
            session.add(new_user)
    session.commit()



def load_movies(session):
    filename = "seed_data/u.item"
    with open(filename) as csvfile:
        data = csv.reader(csvfile, delimiter="|")
        for row in data:
            print row[0]
            if row[2]=="":
                make_date_time = None
            else:
                # TODO: make the below 2 lines be one line w/ datetime.strptime
                make_struct=time.strptime(row[2], "%d-%b-%Y")
                make_date_time = datetime(*make_struct[:6])
            new_movie = model.Movie(id=row[0], name=row[1].decode("latin-1"), released_at=make_date_time, imdb_url= row[4] )
            session.add(new_movie)
    print "DONE PROCESSING"
    session.commit()

def load_ratings(session):
    filename = "seed_data/u.data"
    with open(filename) as csvfile:
        data = csv.reader(csvfile, delimiter="\t")
        for row in data:

            new_rating = model.Rating(user_id=row[0], movie_id=row[1], rating=row[2])
            session.add(new_rating)
        session.commit()
#ctime([secs])
def main(session):
    # You'll call each of the load_* functions with the session as an argument
    load_users(session)
    #load_movies(session)
    load_ratings(session)

if __name__ == "__main__":
    s= model.connect()
    main(s)
