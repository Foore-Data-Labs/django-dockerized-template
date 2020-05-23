FROM python:3.6.9-slim

ENV PYTHONUNBUFFERED 1

WORKDIR /django_web_template/


RUN python -m pip install --upgrade pip


COPY requirements.txt /django_web_template/
RUN pip install -r requirements.txt

COPY . /django_web_template/
