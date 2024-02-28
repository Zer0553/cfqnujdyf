from flask import Flask, render_template, redirect, request
from data.users import User
from data.books import Books
from data.reviews import Reviews
import datetime
from forms.user import RegisterForm
from forms.login_form import LoginForm
from forms.Books_form import BooksForm
from forms.review_form import ReviewForm
from data import db_session, books_api
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_restful import abort, Api
from data import books_resources, users_resources
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
api = Api(app)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(
    days=365
)

login_manager = LoginManager()
login_manager.init_app(app)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/review_edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_book(id):
    form = ReviewForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        review = db_sess.query(Reviews).filter(Reviews.id == id).first()
        if review:
            review.rating = form.rating.data
            review.content = form.content.data
            db_sess.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('review.html',
                           title='Редактирование отзыва',
                           form=form
                           )


@app.route("/")
def index():
    db_sess = db_session.create_session()
    if current_user.is_authenticated:
        books = db_sess.query(Books).all()
        return render_template("index.html", title="Book reviewer", books=books)
    return render_template("base.html")


@app.route('/review_delete/<int:id>', methods=['GET', 'POST'])
def book_delete(id):
    db_sess = db_session.create_session()
    review = db_sess.query(Reviews).filter(Reviews.id == id).first()
    db_sess.delete(review)
    db_sess.commit()
    return redirect('/')


@app.route('/books',  methods=['GET', 'POST'])
@login_required
def add_book():
    form = BooksForm()
    if form.validate_on_submit():
        f = form.picture.data
        filename = secure_filename(f.filename)
        f.save(os.path.join('static/photos', filename))
        db_sess = db_session.create_session()
        try:
            book = Books(
                description=form.description.data,
                picture=filename,
                name=form.name.data,
                author=form.author.data,
                genre=form.genre.data,
                page=form.page.data,
            )
            db_sess.add(book)
            db_sess.commit()
            return redirect('/')
        except Exception:
            return render_template('books.html', title='Добавление киниги',
                                   form=form, message='Проверте правильность написания данных')
    print(form.errors)
    return render_template('books.html', title='Добавление киниги',
                           form=form)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.name == form.name.data).first()
        if user.check_password(form.password.data):
            login_user(user)
            return redirect("/")
        return render_template('login.html', message="Wrong password", form=form)
    return render_template('login.html', title='Authorization', form=form)


@app.route('/book/review/<int:book_id>', methods=['GET', 'POST'])
def review(book_id):
    form = ReviewForm()
    db_sess = db_session.create_session()
    print(book_id)
    if form.validate_on_submit():
        review = Reviews(
            user_name=current_user.__dict__['name'],
            book_id=int(book_id),
            rating=form.rating.data,
            content=form.content.data
        )
        db_sess.add(review)
        db_sess.commit()
        return redirect('/book' + '/' + str(book_id))
    return render_template('review.html', title='Отзыв', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/book/<int:book_id>', methods=['GET'])
def book_info(book_id):
    db_sess = db_session.create_session()
    book = db_sess.query(Books).filter(Books.id == book_id).first()
    reviews = db_sess.query(Reviews).filter(Reviews.book_id == book_id).all()
    already_exists = db_sess.query(Reviews).filter(
        Reviews.user_name == current_user.__dict__['name'],
        Reviews.book_id == book_id).first()
    if already_exists:
        if reviews:
            all_rating = 0
            num_rating = 0
            for i in reviews:
                all_rating += i.rating
                num_rating += 1
            try:
                stars = all_rating // num_rating
            except Exception:
                stars = 0
            return render_template('book.html', title=book.name,
                                   book=book, review=reviews,
                                   already_exists=True,
                                   user_name=current_user.__dict__['name'],
                                   rating=('★' * stars) + ('✩' * (10 - stars)))
        else:
            all_rating = 0
            num_rating = 0
            for i in reviews:
                all_rating += i.rating
                num_rating += 1
            try:
                stars = all_rating // num_rating
            except Exception:
                stars = 0
            return render_template('book.html', title=book.name, book=book, review=reviews, already_exists=True,
                                   rating=('★' * stars) + ('✩' * (10 - stars)))
    if reviews:
        all_rating = 0
        num_rating = 0
        for i in reviews:
            all_rating += i.rating
            num_rating += 1
        try:
            stars = all_rating // num_rating
        except Exception:
            stars = 0
        return render_template('book.html', title=book.name, book=book, review=reviews,
                               already_exists=False,
                               user_name=current_user.__dict__['name'],
                               rating=('★' * stars) + ('✩' * (10 - stars)))
    return render_template('book.html', title=book.name, book=book,
                           already_exists=False)


def main():
    db_session.global_init("db/books_&_people.db")
    app.register_blueprint(books_api.blueprint)
    api.add_resource(users_resources.UsersListResource, '/api/v2/user')
    api.add_resource(users_resources.UsersResource, '/api/v2/users/<int:user_id>')
    api.add_resource(books_resources.BooksListResource, '/api/v2/jobs')
    api.add_resource(books_resources.BooksResource, '/api/v2/jobs/<int:job_id>')
    app.run()


if __name__ == '__main__':
    main()
