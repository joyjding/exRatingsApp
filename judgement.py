from flask import Flask, render_template, redirect, request, session
import model

app = Flask (__name__)

@app.route('/')
def index():
    user_list = model.session.query(model.User).limit(5).all()
    if request.args.get("wrong_password"):
        wrong_password = True
    else:
        wrong_password = False
    return render_template("user_list.html", users=user_list, 
                                        username=session.get('username'),
                                        wrong_password=wrong_password)

@app.route('/user', methods=['GET', 'POST'])
def user_info():
    if request.method == 'POST':
        email = request.form['email']
        pw = request.form['password']
        # check if email/pw is correct
        id = model.check_login(email, pw)
        if id:
            session['username'] = id
            return redirect('/user?user_id=' + str(id))
        else:
            return redirect('/?wrong_password=true')
    user_id = request.args.get("user_id")
    if not user_id:# user_id is empty, redirect to home
        return redirect("/")
    u = model.session.query(model.User).get(user_id) #user object
    #ratings_list = u.ratings #list of ratings for user object
    return render_template("user_info.html", user=u, 
                                    username=session.get('username'))

@app.route('/new_user', methods=['POST'])
def new_user():
    email = request.form["email"]
    password = request.form["password"]
    age = request.form["age"]
    zipcode = request.form["zipcode"]
    model.add_new_user(email, password, age, zipcode)

    return redirect("/")

@app.route('/new_rating', methods=['POST'])
def new_rating():
    rating = request.form['rating_box']
    movie_id = request.form['movie_id']
    user_id = session.get('username')
    model.add_new_rating(user_id, movie_id, rating)
    return redirect(request.referrer)

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.pop('username', None)
    return redirect('/')

@app.route('/movies/')
def show_all_movies():
    movie_list = model.session.query(model.Movie).limit(20).all() # list of Movie objects
    return render_template("movies.html", movies=movie_list, username=session.get('username'))

@app.route('/movies/<movie_name>')
def show_movie(movie_name):
    movie = model.session.query(model.Movie).filter_by(name=movie_name).one()
    user_session = session.get('username')
    user_rating = None
    user = None
    if user_session:
        user = model.session.query(model.User).get(user_session)
        for r in user.ratings:
            if r.movie_id == movie.id:
                user_rating = r


    return render_template("movie.html", movie=movie, user=user, username=user_session, user_rating=user_rating)

app.secret_key = "anoraworjj8tj93498q36hui63nkatojht825q4"

if __name__ == "__main__":
    app.run(debug = True)



