# back-end

Repository for Meduzzen internship

## Requirements

- Python 3.12
- pip

## Installation

Clone git repository:

```bash
git clone <url>
cd back-end\
```

## Environment

- venv (default):

```bash
python -m venv .venv
.venv\Scripts\activate
```

- conda:

```bash
conda create --name <name> python=3.12
conda activate <name>
```

## Install requirements

```bash
pip install -r requirements.txt
```

## Set up environment

```bash
cp .env.sample .env
```

## Run the application

You can run the application using command

```bash
python main.py
```

or via Uvicorn:

```bash
uvicorn main:app --reload
```

## Run tests

```bash
python -m pytest tests/test_routers.py
```

## Run the application with Docker

To create image use command:

```bash
docker build -t <image-name> .
```

After image created run your container:

```bash
docker run -p <host-port>:<container-port> --env-file .env <image-name>
```

## Run the application with Docker Compose

To build and start all services (application, PostgreSQL, Redis):

```bash
docker compose up --build
```

To stop all containers:

```bash
docker compose down
```

To stop and remove volumes (database data):

```bash
docker compose down -v
```

## Environment variables

Fill in `.env` based on `.env.sample`:

| Variable | Description | Default |
|---|---|---|
| `APP_NAME` | Application name | `Meduzzen back-end` |
| `APP_HOST` | Host to bind | `0.0.0.0` |
| `APP_PORT` | Port to bind | `8000` |
| `APP_RELOAD` | Hot reload | `True` |
| `ALLOWED_ORIGINS` | CORS origins (JSON array) | `[]` |
| `DB_USER` | PostgreSQL username | `postgres` |
| `DB_PASSWORD` | PostgreSQL password | `postgres` |
| `DB_NAME` | PostgreSQL database name | `python-back-end` |
| `DB_HOST` | PostgreSQL host | `localhost` (use `db` for Docker) |
| `DB_PORT` | PostgreSQL port | `5432` |
| `REDIS_HOST` | Redis host | `localhost` (use `redis` for Docker) |
| `REDIS_PORT` | Redis port | `6379` |

## Check database connections

After starting the application verify database connections:

| Endpoint | Description |
|---|---|
| `GET /` | Application health check |
| `GET /db-health` | PostgreSQL connection check |
| `GET /redis-health` | Redis connection check |
