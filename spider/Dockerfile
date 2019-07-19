FROM python:3.7

COPY requirements.txt /
RUN pip install -r requirements.txt

COPY . /code
WORKDIR /code

# https://stackoverflow.com/questions/29663459/python-app-does-not-print-anything-when-running-detached-in-docker
# -u is for unbuffering the output, so logs can be seen in Docker
CMD ["python", "-u", "spider.py"]
