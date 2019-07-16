FROM python:3.5

COPY requirements.txt /
RUN pip install -r requirements.txt

COPY . /code
WORKDIR /code

EXPOSE 80

ENTRYPOINT ["python"]
CMD ["front.py"]
