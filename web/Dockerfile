FROM python:3.10

RUN mkdir /code
WORKDIR /code

COPY requirements.txt /code/
RUN pip install -r requirements.txt
EXPOSE 5000
COPY . /code/

CMD gunicorn -b 0.0.0.0:5000 -w 3 run:app