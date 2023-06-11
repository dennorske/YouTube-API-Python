FROM --platform=linux/amd64 python:3.11-bullseye

WORKDIR /usr/src/app

COPY . .

RUN pip install -r requirements.txt
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
