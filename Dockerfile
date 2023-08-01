FROM python:3.9

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /code

COPY requirements.txt /code/
RUN pip install -r requirements.txt
#RUN apt-get update && apt-get install -y firefox-esr
#CMD python your_selenium_script.py
COPY . /code/
