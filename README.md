# sherli_joking

Conversational AI (EE 596D) Project

## Setup

```sh
# Create a virtual environment for libraries
virtualenv --system-site-packages -p python3 sherli_venv
source sherli_venv/bin/activate

git clone git@github.com:elutow/sherli_joking.git
cd sherli_joking
pip install -r requirements.txt

# Setup pke
pip install git+https://github.com/boudinfl/pke.git
python3 -m nltk.downloader stopwords
python3 -m nltk.downloader universal_tagset
python3 -m spacy download en

# TODO: Literally the entire project
```

## Developing

Setup: Run `pip install -Ur dev-requirements.txt` to install requirements for development.

Steps before committing:

1. Run `devutils/process.sh` to fix code formatting and find any linter errors.
2. Run `devutils/test.sh` to run tests and code coverage utilities.

## Development docs

Various notes and design docs live under `docs/`

* [`docs/slowbro.md`](docs/slowbro.md) - Notes about `slowbro`

### Updating library requirements

Run `devutils/update_requirements.sh` and commit the changes.

## Credits

TODO

## Licenses

All code is licensed under the [MIT License](LICENSE), unless specified otherwise:

* `src/slowbro`: [MIT License](src/slowbro/LICENSE)
