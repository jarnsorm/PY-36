FROM ubuntu:22.04.4

RUN apk update && apk upgrade && apt install tesseract-ocr

FROM python:latest

WORKDIR /src

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

COPY ./app app

EXPOSE 8000

CMD ["python3", "app/main.py"]
