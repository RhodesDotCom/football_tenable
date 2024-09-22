FROM python:latest

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . /app

ENTRYPOINT ["python"]
CMD ["db_load.py"]