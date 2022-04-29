FROM python:3.8-alpine

WORKDIR /app

COPY . /app

RUN python3 -m pip install --upgrade pip

RUN pip3 install -r requirements.txt

ENTRYPOINT ["sh","./docker-entrypoint.sh"]
