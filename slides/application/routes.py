import json

from flask import abort
from flask import current_app as app
from flask import request

from application import db
from application.models import Slide
from application.utils import get_slides_info

from sqlalchemy.sql.expression import func

@app.route('/health', methods=['GET'])
def health():
    return "OK", 200

@app.route('/api/v1/slides', methods=['GET'])
def get_slides():
    slides = Slide.query.filter_by(deleted=False).all()
    if not slides:
        abort(404)
    return repr(slides)

@app.route('/api/v1/slides/<string:slide_id>', methods=['GET'])
def get_slide(slide_id):
    slide = Slide.query.filter_by(id=slide_id, deleted=False).first()
    if not slide:
        abort(404)
    return repr(slide)

@app.route('/api/v1/slides', methods=['POST'])
def insert_slide():
    if not request.json or 'url' not in request.json:
        abort(400)

    url = request.json['url']
    funniness = request.json.get('funniness', None) # Not obligatory, default is None
    new_slide = Slide(url=url, funniness=funniness)

    db.session.add(new_slide)  # Adds new Slide record to database
    db.session.commit()  # Commits all changes
    return repr(new_slide), 201

@app.route('/api/v1/slides/random/<int:no_slides>', methods=['GET'])
def random_slides(no_slides):
    """ Return no_slides random slides. """
    slides = Slide.query.filter_by(deleted=False).order_by(func.random()).limit(no_slides).all()
    if not slides:
        abort(404)

    # Hack to convert slides obj to dict (json-like) format
    slides = json.loads(str(slides))

    response = {'slides': slides,
                'info': get_slides_info(slides)}
    return json.dumps(response)

@app.route('/api/v1/slides/<string:slide_id>', methods=['DELETE'])
def delete_slide(slide_id):
    slide = Slide.query.filter_by(id=slide_id, deleted=False).first()
    if not slide:
        abort(404)

    slide.deleted = True   # Don't actually delete the slide, mark it as deleted
    db.session.commit()    # Commit the change
    return repr(slide)
