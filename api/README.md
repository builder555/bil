### Prerequisites

- Python 3.9
- Poetry

### Installation

```bash
poetry install
```

### Run

```bash
poetry shell
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Development
```bash
poetry install
poetry shell
# to run tests once:
pytest -v
# to monitor files and re-run tests when they change:
ptw --runner 'pytest -v'
# to format all files:
black .
```