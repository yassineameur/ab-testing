
# Patt

P.A.T.T stands for pumpkin's Ab Testing Tool.
As its name suggests, this project is an internal tool for ab testing. it is composed of:
- Web app where the user (marketing or products team member) can login and build a test. The user can watch also the results of his built tests in real time.
- A worker that, each time, parses the current tests and compute results (so that it will be shown to the final user via the web app)

### Technical stack
Datalake uses python 3.7 as a programming language. 
For data storage, Postgres is the used database system.
For web app, we have opted to Flask (so easy ann quick to use)


## You want to contribute ?
If you want to contribute, you are welcomed. Here is all you need to do to start developing.
- Install python 3.7
- Create a virtual environment (name it as you want)
- Install dependencies: `pip install -r requirements.txt`

## How to turn-on the engine?

- In order to start the backend worker, please use this command `python tests_worker.py`
- To start the webapp, please use this command `gunicorn --bind 0.0.0.0:${PORT:=3079} -k gevent api_starter:app` (You can of course change the port number if it is already occupied)


## Env variables

| Key | Commentary | Default value |
|-----|------------|---------------|
| DATALAKE_DB_URL | URL to datalake's database (write and remove rights) | `postgresql://postgres@localhost:5432/datalake` |
| PUMPKIN_DB_URL | URL to Pumpkin's database | `postgresql://postgres@localhost:5432/pumpkin` |
| WORKER_FREQUENCY | The tests worker execution frequency in minutes | `5` |
| PATT_DB_SCHEMA_NAME | The schema in which we build patt tables | `patt` |
| SECRET_KEY | The secret key that protects app from attacks | `023af5a0253f5ff468b25fa40fd5d85f` |
| ADMIN_EMAIL | The admin's email | `bi@pumpkin-app.com` |
| ADMIN_PASSWORD | The admin's password | `fake_password` |
| FRONT_PORT | The frontend port| `5000` |
