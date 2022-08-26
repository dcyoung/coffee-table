FROM python:3.10-slim-buster

ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update

COPY requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

COPY src/ src/

ENV PYTHONUNBUFFERED 1
EXPOSE 8501
CMD ["streamlit", "run", "src/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
