FROM python:3.7-alpine
# Install dependencies for psycopg2
RUN apk update && apk add postgresql-dev gcc python3-dev musl-dev

COPY requirements.txt /
RUN pip install -r requirements.txt

COPY . /code
WORKDIR /code

EXPOSE 8000

CMD ["sh", "./start.sh"]
