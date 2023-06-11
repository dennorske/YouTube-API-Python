FROM python:3.11-bullseye

COPY task.sh .
ENTRYPOINT [ "task.sh" ]