import json

import sentry_sdk
from decouple import config
from flask import Flask, render_template, request
from flask_basicauth import BasicAuth
from kafka import KafkaProducer
from sentry_sdk.integrations.flask import FlaskIntegration

BOOTSTRAP_SERVERS = ALLOWED_HOSTS = config('BOOTSTRAP_SERVERS',
                                           default='kafka:9092',
                                           cast=lambda v: [s.strip() for s in v.split(',')])
TOPIC_NAME = 'slide_fetching'

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

basic_auth = BasicAuth(app)

app.config['BASIC_AUTH_USERNAME'] = config("BASIC_AUTH_USERNAME", default='pptk_slides', cast=str)
app.config['BASIC_AUTH_PASSWORD'] = config("BASIC_AUTH_PASSWORD", default='pptk_slides', cast=str)


def publish_message(producer_instance, topic_name, data):
    """ Excepts data to be a dictionary """
    try:
        if not isinstance(data, dict):
            raise ValueError
        producer_instance.send(topic_name, value=data)  # Send the message to the queue
        producer_instance.flush()
    except ValueError as e:
        app.logger.error('Error, data is expected to be a dictionary!')
    except Exception as e:
        app.logger.error(f'Unexpected error in publishing message. {str(e)}')


def connect_kafka_producer():
    _producer = None
    try:
        _producer = KafkaProducer(bootstrap_servers=BOOTSTRAP_SERVERS,
                                  api_version=(0, 10),
                                  value_serializer=lambda x: json.dumps(x).encode('utf-8'))
    except Exception as e:
        app.logger.error(f'Unexpected error while connecting to Kafka. {str(e)}')
    finally:
        return _producer


def request_fetching_slides(no_slides):
    """ Orders spider microservice to fetch no_slides of slides.

    Inserts messages to kafka queue. These messages will be pulled and processed
    by spider microservice later on.
    """
    kafka_producer = connect_kafka_producer()
    data = {'no_slides_to_fetch': 1}

    for _ in range(no_slides):
        publish_message(kafka_producer, TOPIC_NAME, data)

    app.logger.info(f'Requested to fetch {no_slides} slides.')

    if kafka_producer is not None:
        kafka_producer.close()  # Close the connection


@app.route('/')
@basic_auth.required
def index():
    return render_template("index.html")


@app.route('/fetch', methods=['GET', 'POST'])
@basic_auth.required
def fetch_slides():
    try:
        no_slides = int(request.args.get('no_slides', default=1))
    except ValueError as e:
        return f"Invalid argument!", 405

    if no_slides <= 0 or no_slides > MAX_SLIDES_DOWNLOADED:
        app.logger.warning(f"Attempt to download {no_slides} slides.")
        return "Invalid argument!", 405

    try:
        request_fetching_slides(no_slides)
    except Exception as e:
        return f"Unexpected error occured. {str(e)}", 500

    return render_template("fetch.html", no_slides=no_slides)


if __name__ == '__main__':
    app.run(debug=FLASK_DEBUG, host='0.0.0.0', port=8000)
