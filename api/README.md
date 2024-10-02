## Budget Insight Ledger

A simple bookkeeping and finance management application.

> [!CAUTION]
> **NB:** THIS API IS NOT SECURED!! <br/>
> IT IS MEANT TO BE A BASIS FOR YOUR OWN IMPLEMENTATION.
> !!DO NOT USE IN PRODUCTION!!

### Prerequisites

- Python 3.10
- Poetry
- libmagic:
```shell
sudo apt install libmagic1
# or
brew install libmagic
```

### Installation

```bash
poetry install
```

### Run

```bash
poetry run uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Development
```bash
poetry install
# to run tests once:
poetry run pytest -v
# to monitor files and re-run tests when they change:
poetry run ptw --runner 'pytest -v'
# to format all files:
poetry run black .
```