FROM python:3.7

WORKDIR /app/

# -- Adding Pipfiles
COPY requirements.txt requirements.txt

# -- Install dependencies:
RUN pip install -r requirements.txt

COPY . .

CMD [ "python", "tests_worker.py" ]
