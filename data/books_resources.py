import flask

from . import db_session
from .books import Books
from flask import jsonify, make_response, request, abort
from flask_restful import reqparse, abort, Api, Resource


def abort_if_job_not_found(job_id):
    session = db_session.create_session()
    jobs = session.query(Books).get(job_id)
    if not jobs:
        abort(404, message=f"Job {job_id} not found")


parser = reqparse.RequestParser()
parser.add_argument('team_leader', required=True)
parser.add_argument('job', required=True)
parser.add_argument('work_size', required=True)
parser.add_argument('collaborators', required=True)
parser.add_argument('start_date', required=True)
parser.add_argument('end_date', required=True)
parser.add_argument('is_finished', required=True)


class BooksResource(Resource):
    def get(self, job_id):
        abort_if_job_not_found(job_id)
        session = db_session.create_session()
        news = session.query(Books).get(job_id)
        return jsonify({'news': news.to_dict(
            only=('team_leader', 'job', 'work_size', 'collaborators'
                  , 'start_date', 'end_date', 'is_finished'))})

    def delete(self, job_id):
        abort_if_job_not_found(job_id)
        session = db_session.create_session()
        news = session.query(Books).get(job_id)
        session.delete(news)
        session.commit()
        return jsonify({'success': 'OK'})


class BooksListResource(Resource):
    def get(self):
        session = db_session.create_session()
        jobs = session.query(Books).all()
        return jsonify({'jobs': [item.to_dict(
            only=('team_leader', 'job', 'work_size', 'collaborators'
                  , 'start_date', 'end_date', 'is_finished')) for item in jobs]})

    def post(self):
        args = parser.parse_args()
        session = db_session.create_session()
        book = Books(
            picture=args['picture'],
            name=args['name'],
            author=args['author'],
            collaborators=args['collaborators'],
            genre=args['genre'],
            page=args['page']
        )
        session.add(book)
        session.commit()
        return jsonify({'success': 'OK'})
