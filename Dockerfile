FROM python:3.11
WORKDIR  /app

COPY . /app

RUN pip install poetry

# WORKDIR /app/homeworkweb_1

RUN poetry install

EXPOSE 3000
# ENV . /app



ENTRYPOINT  ["poetry", "python", "main.py"]
