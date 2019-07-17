FROM python:3.5

COPY requirements.txt /
RUN pip install -r requirements.txt

COPY . /code
WORKDIR /code

EXPOSE 8000

ENTRYPOINT ["python"]
CMD ["front.py"]
