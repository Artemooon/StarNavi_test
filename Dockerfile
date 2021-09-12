FROM python:3.8

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

RUN mkdir social_app/
WORKDIR /social_app

COPY requirements.txt /social_app/

RUN pip install -r requirements.txt

COPY . /social_app/

CMD ["python", "manage.py", "migrate", "--no-input"]
CMD ["python", "manage.py", "collectstatic", "--no-input"]