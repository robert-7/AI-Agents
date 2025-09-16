# AI Agents

This repository will host code for all course materials.

## Getting Set Up

The steps below should help you get set up virtualenv and pre-commit on an Ubuntu system.

```bash
# install python 3 and dependencies
sudo apt update
sudo apt install -y \
    build-essential \
    libffi-dev \
    libssl-dev \
    pre-commit \
    python3 \
    python-dev \
    python3-pip \
    python3-venv

# set up pre-commit so basic linting happens before every commit
pre-commit install
pre-commit run --all-files
```

The steps below should help you get set up the tool on an Ubuntu system.

```shell
# set up virtualenv
python -m venv '.venv'
source .venv/bin/activate

# install requirements
pip install -r requirements.txt

cp .env.template .env
sed -i 's/LINKUP_API_KEY=.*/LINKUP_API_KEY=INSERT_KEY_HERE/g'
sed -i 's/OPENAI_API_KEY=.*/OPENAI_API_KEY=INSERT_KEY_HERE/g'
```

### Recurring

To deactivate or reactivate your virtual environment, simply run:

```bash
deactivate                # deactivates virtualenv
source .venv/bin/activate # reactivates virtualenv
```

### Debugging

For additional details for

* [Linkup](https://app.linkup.so/home)
* [OpenAI Observability](https://platform.openai.com/logs)
