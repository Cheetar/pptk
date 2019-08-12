FROM python:3.7

ARG WORDS_URL=https://raw.githubusercontent.com/dwyl/english-words/master/words.txt

COPY requirements.txt /
RUN pip install -r requirements.txt

RUN apt-get update \
	&& apt-get install -y --no-install-recommends ca-certificates curl firefox-esr wget \
	&& rm -fr /var/lib/apt/lists/* \
	&& curl -L https://github.com/mozilla/geckodriver/releases/download/v0.24.0/geckodriver-v0.24.0-linux64.tar.gz | tar xz -C /usr/local/bin \
	&& mkdir -p /code/assets && wget -O /code/assets/words.txt ${WORDS_URL} \
	&& apt-get purge -y ca-certificates curl wget

COPY . /code
WORKDIR /code

# https://stackoverflow.com/questions/29663459/python-app-does-not-print-anything-when-running-detached-in-docker
# -u is for unbuffering the output, so logs can be seen in Docker
CMD ["python", "-u", "spider.py"]
