FROM python:3

WORKDIR /app

RUN apt-get clean && apt-get -y update
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY start.sh /app/deployment/start.sh
RUN chmod 777 /app/deployment/start.sh
