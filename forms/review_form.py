from flask_wtf import FlaskForm
from wtforms import TextAreaField
from wtforms import SubmitField, SelectField


class ReviewForm(FlaskForm):
    rating = SelectField('Ваша оценка книги', choices=
                         ['1', '2', '3', '4', '5',
                          '6', '7', '8', '9', '10'])
    content = TextAreaField('Текст отзыва')
    submit = SubmitField('Применить')
