import json
import secrets
from datetime import datetime as dt

from application import db
from application.utils import put_into_s3, read_data_from_url
from flask import current_app as app


class Slide(db.Model):
    """Model for slides."""

    __tablename__ = 'slides'
    id = db.Column(db.String(128),
                   primary_key=True)
    url = db.Column(db.String(1024),
                    index=False,
                    unique=False,
                    nullable=False)
    funniness = db.Column(db.Float,
                          index=False,
                          unique=False,
                          nullable=True)
    created = db.Column(db.DateTime,
                        index=False,
                        unique=False,
                        nullable=False)
    deleted = db.Column(db.Boolean,
                        index=False,
                        unique=False,
                        nullable=False)
    s3_stored = db.Column(db.Boolean,
                          index=False,
                          unique=False,
                          nullable=False)

    def __init__(self, url, funniness=None):
        self.id = secrets.token_urlsafe(20)
        self.url = url
        self.funniness = funniness
        self.created = dt.now()
        self.deleted = False
        self.s3_stored = False

        try:
            image_data = read_data_from_url(url)
            uploaded = put_into_s3(self.id, image_data)
            self.s3_stored = uploaded
        except Exception as e:
            app.logger.warning(f'Couldn\'t fetch the image from url {url}. {str(e)}')

    def __repr__(self):
        """ Represents Slide model as a json."""
        json_representation = {'id': self.id,
                               'url': self.url,
                               'funniness': self.funniness,
                               'created': str(self.created),
                               's3_stored': self.s3_stored
                               }
        return json.dumps(json_representation)

    def __str__(self):
        return 'Slide {}.'.format(self.url)
