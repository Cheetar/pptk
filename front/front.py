import requests

import sentry_sdk
from decouple import config
from flask import Flask, render_template
from sentry_sdk.integrations.flask import FlaskIntegration

FLASK_DEBUG = config("FLASK_DEBUG", default=False, cast=bool)

SLIDES_API_URL = "http://slides:8000/api/v1/slides/random/100"

AWS_REGION = config("AWS_REGION", default=None, cast=str)
BUCKET_NAME = config("BUCKET_NAME", default=None, cast=str)

GA_TRACKING_CODE = config("GA_TRACKING_CODE", default=None, cast=str)

SENTRY_DNS = config("SENTRY_DNS", default=None, cast=str)

# Log the errors to sentry
if SENTRY_DNS and not FLASK_DEBUG:
    # In production mode, track all errors with sentry.
    sentry_sdk.init(
        dsn=SENTRY_DNS,
        integrations=[FlaskIntegration()]
    )

app = Flask(__name__)


def fetch_slides():
    """ Send HTTP request to slides microservice for slides"""
    res = requests.get(SLIDES_API_URL)
    if res.status_code == 404:
        raise KeyError  # No slides are currently stored in slides microservice
    elif res.status_code != 200:
        raise RuntimeError("Invalid status code.")
    return res.json()


@app.context_processor
def inject_ga_tracking_code():
    """ Adds ga_tracking_code for every template. """
    return dict(ga_tracking_code=GA_TRACKING_CODE)


@app.context_processor
def inject_debug():
    """ Adds debug information for every template. """
    return dict(debug=FLASK_DEBUG)


@app.errorhandler(404)
def not_found(e):
    return render_template("error.html", header="404 Not Found", message=str(e)), 404


@app.errorhandler(500)
def server_error(e):
    return render_template("error.html", header="500 Internal server problem", message=str(e)), 500


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/slider/')
def slider():
    try:
        data = fetch_slides()
        return render_template("slider.html", slides=data['slides'],
                               aws_region=AWS_REGION,
                               bucket_name=BUCKET_NAME)
    except requests.exceptions.ConnectionError:
        return render_template("error.html",
                               header="Connection error",
                               message="Couldn't fetch the slides, please try again later")
    except KeyError as e:
        return render_template("error.html",
                               header="404 Not found",
                               message="No slides are currently stored in slides microservice")
    except Exception as e:
        return render_template("error.html", header="Unexpected error", message=str(e))


if __name__ == '__main__':
    app.run(debug=FLASK_DEBUG, host='0.0.0.0', port=8000)
