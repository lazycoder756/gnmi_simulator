FROM python:3.9.18-slim-bullseye

WORKDIR /app

COPY gnmi_server/requirements.txt ./

RUN pip install -r requirements.txt


COPY gnmi_server /app

EXPOSE 50051

CMD ["python","server.py"]