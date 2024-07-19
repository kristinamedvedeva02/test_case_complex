FROM python:3.11

WORKDIR /app

COPY requirements.txt requirements.txt
COPY . .

RUN pip install -r requirements.txt

RUN python manage.py migrate

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "weath_prog.wsgi:application"]

EXPOSE 8000
