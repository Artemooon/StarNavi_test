FROM python:3.8

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

RUN mkdir social_app/
WORKDIR /social_app

COPY poetry.lock pyproject.toml /social_app/

RUN pip install --upgrade pip && pip install poetry && poetry config virtualenvs.create false && poetry install

COPY . /social_app/

CMD ["python", "manage.py", "migrate", "--no-input"]
CMD ["python", "manage.py", "collectstatic", "--no-input"]