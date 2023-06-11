FROM --platform=linux/amd64 python:3.11-bullseye

WORKDIR /usr/src/app

COPY . .

RUN pip install -r requirements.txt

CMD ["uvicorn", "main:app"]
