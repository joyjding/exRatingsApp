import model
import csv

def load_users(session):
    filename = "seed_data/u.user"
    with open(filename) as csvfile:
        data = csv.reader(csvfile, delimiter="|")
        for row in data:
            print row
            new_user = model.User(id=row[0], age=row[1], zipcode=row[4])
            session.add(new_user)
    session.commit()



def load_movies(session):
    # use u.item
    pass

def load_ratings(session):
    # use u.data
    pass

def main(session):
    # You'll call each of the load_* functions with the session as an argument
    load_users(session)

if __name__ == "__main__":
    s= model.connect()
    main(s)
