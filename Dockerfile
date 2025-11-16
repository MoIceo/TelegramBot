FROM python:3.13-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir --upgrade -r requirements.txt && apt-get update && apt-get install bash

EXPOSE 8000

CMD ["bash", "start.sh"]
