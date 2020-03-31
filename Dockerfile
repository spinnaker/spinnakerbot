FROM python:3-alpine

RUN adduser -D -S spinbot

WORKDIR /usr/src/app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

USER spinbot

ENTRYPOINT ["/usr/local/bin/python", "./spinbot.py" ]
