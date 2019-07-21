import json

import requests

from decouple import config
from kafka import KafkaConsumer

VERIFIER_URL = 'http://verifier:8000/api/v1/verify?image='
SLIDES_URL = 'http://slides:8000/api/v1/slides'

TOPIC_NAME = 'slide_fetching'
BOOTSTRAP_SERVERS = config('BOOTSTRAP_SERVERS',
                           cast=lambda v: [s.strip() for s in v.split(',')])


def add_slide(url, image_funniness):
    """ Call REST API of Slides microservice to add the slide. """
    res = requests.post(SLIDES_URL, json={"url": url,
                                          'funniness': image_funniness})
    if res.status_code is not 201:
        raise SystemError("Couldn't add the slide, microservice slides rejected the request")


def is_suitable_for_presentation(image_data):
    """ Check if the image is suitable_for_presentation. """
    if image_data is None:
        return False

    return image_data['suitable_for_presentation']


def get_image_funniness_data(url):
    """ Ask verifier microservice for the image funniness. """
    res = requests.get(VERIFIER_URL + url)
    if res.status_code is not 200:
        raise SystemError("Couldn't add the slide, microservice verifier rejected the request")

    return json.loads(res.content)


def get_random_image_url():
    """ Get the url of a random image from the Internet. """
    # TODO get the real urls from the Internet.
    return "http://lorempixel.com/400/200/"


def fetch_slide():
    """ Handle slide downloading.

    1) Get a url of an image from the Internet
    2) Ask verifier if the image is funny
    3) If not suitable for presentation, go to 1)
    4) Add the slide using slides microservice REST API
    """
    print("Fetching slide..")

    image_data = None
    while not is_suitable_for_presentation(image_data):
        url = get_random_image_url()
        image_data = get_image_funniness_data(url)

    image_funniness = image_data['image_funniness']
    add_slide(url, image_funniness)
    return True


def consume_message(data):
    if not isinstance(data, dict) or 'no_slides_to_fetch' not in data:
        raise ValueError('Invalid message format!')

    for _ in range(data['no_slides_to_fetch']):
        # Slide fetching can fail, so fetch slides until success
        slide_fetched = False
        while not slide_fetched:
            try:
                slide_fetched = fetch_slide()
            except Exception as e:
                print(f"Unexpected error when fetching a slide. {str(e)}")


if __name__ == '__main__':
    print('Spider starting..')

    consumer = KafkaConsumer(TOPIC_NAME,
                             auto_offset_reset='latest',
                             bootstrap_servers=BOOTSTRAP_SERVERS,
                             api_version=(0, 10),
                             consumer_timeout_ms=1000,
                             enable_auto_commit=True,
                             value_deserializer=lambda x: json.loads(x.decode('utf-8')))

    consumer.subscribe([TOPIC_NAME])  # Poll messages from the topic

    try:
        while True:
            # Response format is {TopicPartiton('topic1', 1): [msg1, msg2]}
            msg_pack = consumer.poll(timeout_ms=1000,  # Wait for 1s when no data in buffer
                                     max_records=1)  # Poll maximum 1 record at a time

            for tp, messages in msg_pack.items():
                for message in messages:
                    try:
                        consume_message(message.value)
                    except Exception as e:
                        print(f'Error while consuming the message. {str(e)}')
    finally:
        consumer.close()
