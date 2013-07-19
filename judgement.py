from flask import Flask, render_template, redirect, request, session, g, url_for
import model

app = Flask(__name__)

#  check if user is logged in before each route request, and set g.user if so
@app.before_request
def before_request():
    user_id = session.get('user_id')
    if user_id:
        user = model.session.query(model.User).get(user_id)
        g.user = user
    else:
        g.user = None


@app.route('/')
def index():
    user_list = model.session.query(model.User).limit(5).all()
    if request.args.get("wrong_password"):
        wrong_password = True
    else:
        wrong_password = False
    return render_template("user_list.html", users=user_list, wrong_password=wrong_password)


@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    pw = request.form['password']
    # check if email/pw is correct
    user = model.check_login(email, pw)
    if user:
        session['user_id'] = user.id
        g.user = user
        return redirect('/user?user_id=' + str(user.id))
    else:
        return redirect('/?wrong_password=true')


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.pop('user_id', None)
    return redirect('/')


@app.route('/user', methods=['GET'])
def user_info():
    user_id = request.args.get("user_id")
    if not user_id:  # if user_id is empty, redirect to home
        return redirect("/")
    u = model.session.query(model.User).get(user_id)  # user object
    return render_template("user_info.html", user=u)


@app.route('/new_user', methods=['GET', 'POST'])
def new_user():
    if request.method == 'GET':
        return render_template("signup.html")
    email = request.form["email"]
    password = request.form["password"]
    age = request.form["age"]
    zipcode = request.form["zipcode"]
    g.user = model.add_new_user(email, password, age, zipcode)
    session['user_id'] = g.user.id
    return redirect("/")


@app.route('/new_rating', methods=['POST'])
def new_rating():
    rating = request.form['rating_box']
    movie_id = request.form['movie_id']
    user_id = g.user.id
    model.add_new_rating(user_id, movie_id, rating)
    return redirect(request.referrer)


@app.route('/movies/')
def show_all_movies():
    movie_list = model.session.query(model.Movie).limit(20).all()  # list of Movie objects
    return render_template("movies.html", movies=movie_list)


@app.route('/movies/<movie_name>')
def show_movie(movie_name):
    movie = model.session.query(model.Movie).filter_by(name=movie_name).one()

    user_rating = None
    if g.user:
        for r in g.user.ratings:
            if r.movie_id == movie.id:
                user_rating = r

    return render_template("movie.html", movie=movie, user_rating=user_rating)


app.secret_key = "anoraworjj8tj93498q36hui63nkatojht825q4"

if __name__ == "__main__":
    app.run(debug=True)

