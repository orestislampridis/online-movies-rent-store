FROM python:3.10

RUN mkdir /code
WORKDIR /code

COPY requirements.txt /code/
RUN pip install -r requirements.txt
EXPOSE 5000
COPY . /code/

CMD python run.py