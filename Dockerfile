#FROM ubuntu:22.04.4
#
#RUN apk update && apk upgrade && apt install tesseract-ocr
#
#FROM python:latest
#
#WORKDIR /app
#
#COPY . .
#
#RUN pip3 install -r requirements.txt
#
#EXPOSE 8000
#
#CMD ["python3", "main.py"]
#
#CMD ["celery", "-A", "celery_config", "worker", "--loglevel=INFO"]

