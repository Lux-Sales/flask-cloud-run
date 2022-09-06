FROM python:3.10-slim
ADD . /app
WORKDIR /app
RUN ["pip", "install", "--disable-pip-version-check", "-r", "requirements.txt"]

ENTRYPOINT ["/bin/bash", "entrypoint.sh"]

EXPOSE 8080
