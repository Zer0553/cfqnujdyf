from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms import SubmitField, IntegerField, TextAreaField
from flask_wtf.file import FileField, FileRequired


class BooksForm(FlaskForm):
    picture = FileField('Загрузите обложку книги', validators=[FileRequired()])
    name = StringField('Название книги')
    author = StringField('Имя автора')
    genre = StringField('Жанры')
    page = IntegerField('Кол-во страниц')
    description = TextAreaField('Краткое описание книги')
    submit = SubmitField('Применить')
