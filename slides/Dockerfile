FROM python:3.7

COPY requirements.txt /
RUN pip install -r requirements.txt

COPY . /code
WORKDIR /code

EXPOSE 8000

CMD ["./start.sh"]
