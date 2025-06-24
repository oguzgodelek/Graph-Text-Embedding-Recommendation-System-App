FROM python:3.12

WORKDIR /server

COPY requirements.txt /server/
COPY /src /server/src

RUN pip install --no-cache-dir --upgrade -r requirements.txt

CMD ["uvicorn", "src.server:app", "--host", "0.0.0.0", "--port", "8000"]