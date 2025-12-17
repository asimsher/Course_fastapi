FROM python:3.12

ENV PYTHONUNBUFFERED=1

WORKDIR /course_app

COPY req.txt /course_app/
RUN pip install -r req.txt &&  \
    pip install --upgrade pip


COPY . /course_app/