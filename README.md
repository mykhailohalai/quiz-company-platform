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
