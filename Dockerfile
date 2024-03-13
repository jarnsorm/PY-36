FROM ubuntu:22.04.4

ENV PYTHONDONTWRITEBYTECODE 1

ENV PYTHONUNBUFFERED 1

RUN apk update && apk upgrade && apt install tesseract-ocr

FROM python:latest

WORKDIR /src

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

COPY . /src

EXPOSE 8000

ENV PYTHONPATH "/src"

CMD ["python3", "app/main.py"]
