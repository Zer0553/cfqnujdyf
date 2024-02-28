import flask

from . import db_session
from .books import Books
from flask import jsonify, request
blueprint = flask.Blueprint(
    'news_api',
    __name__,
    template_folder='templates'
)


@blueprint.route('/api/book')
def get_books():
    db_sess = db_session.create_session()
    books = db_sess.query(Books).all()
    return jsonify(
        {
            'books':
                [item.to_dict(only=('team_leader', 'job', 'work_size',
                                    'collaborators', 'start_date', 'end_date',
                                    'is_finished'))
                 for item in books]
        }
    )


@blueprint.route('/api/book/<int:books_id>', methods=['GET'])
def get_one_book(books_id):
    db_sess = db_session.create_session()
    books = db_sess.query(Books).get(books_id)
    if not books:
        return jsonify({'error': 'Not found'})
    return jsonify(
        {
            'books:':
                [books.to_dict(only=('team_leader', 'job', 'work_size',
                                     'collaborators', 'start_date', 'end_date',
                                     'is_finished'))]
        }
    )


@blueprint.route('/api/books', methods=['POST'])
def create_books():
    if not request.json:
        return jsonify({'error': 'Empty request'})
    elif not all(key in request.json for key in
                 ['picture', 'name', 'author',
                  'genre']):
        return jsonify({'error': 'Bad request'})
    db_sess = db_session.create_session()
    books = Books(
        picture=request.json['picture'],
        name=request.json['name'],
        author=request.json['author'],
        genre=request.json['genre']
    )
    db_sess.add(books)
    db_sess.commit()
    return jsonify({'success': 'OK'})
