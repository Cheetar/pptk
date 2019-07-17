import sentry_sdk
from decouple import config
from flask import Flask, render_template, request
from sentry_sdk.integrations.flask import FlaskIntegration

FLASK_DEBUG = config("FLASK_DEBUG", default=False, cast=bool)
SENTRY_DNS = config("SENTRY_DNS", default=None, cast=str)

MAX_SLIDES_DOWNLOADED = 1000

# Log the errors to sentry
if SENTRY_DNS and not FLASK_DEBUG:
    # In production mode, track all errors with sentry.
    sentry_sdk.init(
        dsn=SENTRY_DNS,
        integrations=[FlaskIntegration()]
    )

app = Flask(__name__)


def fetch_slides_async(no_slides):
    """ Orders fetching of no_slides slides to spider microservice.

    Inserts tickets to async queue. These tickets will pulled by spider microservice
    later on and processed.
    """

    for _ in range(no_slides):
        # TODO insert slide fetch order into async queue
        pass


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/fetch', methods=['GET', 'POST'])
def fetch_slides():
    try:
        no_slides = int(request.args.get('no_slides', default=1))
    except ValueError as e:
        return f"Invalid argument!", 405

    if no_slides <= 0 or no_slides > MAX_SLIDES_DOWNLOADED:
        app.logger.warning(f"Attempt to download {no_slides} slides.")
        return "Invalid argument!", 405

    try:
        fetch_slides_async(no_slides)
    except Exception as e:
        return f"Unexpected error occured. {str(e)}", 500

    return render_template("fetch.html", no_slides=no_slides)


if __name__ == '__main__':
    app.run(debug=FLASK_DEBUG, host='0.0.0.0', port=8000)
