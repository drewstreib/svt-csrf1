FROM python:3.9
WORKDIR /code

COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./app /code/app
COPY ./static /code/static
COPY ./templates /code/templates

# start just one worker so that global variables work in this simple test environment
ENV WEB_CONCURRENCY=1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80", "--workers", "1"]

