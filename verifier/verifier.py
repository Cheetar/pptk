import json
import os
import random
import string
import urllib

import numpy as np

import cv2
import sentry_sdk
from decouple import config
from flask import Flask, abort, request
from keras.models import load_model
from sentry_sdk.integrations.flask import FlaskIntegration

SENTRY_DNS = config("SENTRY_DNS", default=None, cast=str)
FLASK_DEBUG = config("FLASK_DEBUG", default=False, cast=bool)

# Log the errors to sentry
if SENTRY_DNS and not FLASK_DEBUG:
    # In production mode, track all errors with sentry.
    sentry_sdk.init(
        dsn=SENTRY_DNS,
        integrations=[FlaskIntegration()]
    )

app = Flask(__name__)

DOWNLOADED_IMAGE_PATH = "images"
TOKEN_LEN = 15


def delete_image(filename):
    file_path = "%s/%s/%s" % (os.getcwd(), DOWNLOADED_IMAGE_PATH, filename)
    os.remove(file_path)


def get_random_filename():
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(TOKEN_LEN))


def download_photo(img_url, filename):
    directory = "%s/%s/" % (os.getcwd(), DOWNLOADED_IMAGE_PATH)
    file_path = "%s%s" % (directory, filename)
    app.logger.info("Downloading photo from url {0} at path {1}".format(img_url, file_path))

    # Create directory if doesn't exist
    if not os.path.exists(directory):
        os.makedirs(directory)

    f = open(file_path, 'wb+')
    f.write(urllib.request.urlopen(img_url).read())
    f.close()


def get_image_funniness(filename):
    file_path = "%s/%s/%s" % (os.getcwd(), DOWNLOADED_IMAGE_PATH, filename)

    img = cv2.imread(file_path)
    # Neural network needs the image to be of shape (300, 300, 3)
    img = cv2.resize(img, (300, 300))
    img = cv2.normalize(img, None, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_32F)
    img = np.reshape(img, [1, 300, 300, 3])

    # Use neural network to predict how funny the image is
    model = load_model("PPTK-CNN.h5")
    funniness = float(model.predict(img))

    return funniness


def get_response(image_funniness):
    res = {'image_funniness': image_funniness,
           'suitable_for_presentation': bool(image_funniness > 0.33)}
    return json.dumps(res)


@app.route('/api/v1/verify')
def verify():
    image_url = request.args.get('image', default=None, type=str)
    if image_url is None:
        app.logger.error("Error: can't fetch image, no image url given")
        abort(404)

    filename = get_random_filename()

    try:
        download_photo(image_url, filename)
    except Exception as e:
        app.logger.error("An error occured when downloading the photo: {}".format(e))
        abort(500)

    try:
        image_funniness = get_image_funniness(filename)
    except Exception as e:
        app.logger.error("An error occured when calculating the funniness of the photo: {}".format(e))
        abort(500)

    response = get_response(image_funniness)
    delete_image(filename)
    return response


if __name__ == '__main__':
    app.run(debug=FLASK_DEBUG, host='0.0.0.0', port=8000)
