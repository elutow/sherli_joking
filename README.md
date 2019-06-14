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

# Download corpora for newspaper3k
python3 download_corpora.py

# Symlink intent models
ln -s /path/to/know-your-intent-sherli/models intent_models
# OR copy models from elutow/know-your-intent-sherli
cp -r /path/to/know-your-intent-sherli/models intent_models

mkdir config
# Add News API key
printf 'API_KEY_HERE' > config/newsapi_key

# Start the Alexa Skill server
# Make sure to use a DynamoDB instance, such as DynamoDB Local (https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/Tools.DynamoDBLocal.html)
# Pass in -h for docs on available arguments
python3 sherlibot_server.py
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

* `slowbro` - From [hao-cheng/ee596\_spr2019\_lab2](https://github.com/hao-cheng/ee596_spr2019_lab2)
* `know_your_intent.py` - [elutow/know-your-intent-sherli](https://github.com/elutow/know-your-intent-sherli), a fork of [kumar-shridhar/Know-Your-Intent](https://github.com/kumar-shridhar/Know-Your-Intent)

## Licenses

All code is licensed under the [MIT License](LICENSE), unless specified otherwise:

* `slowbro`: [MIT License](src/slowbro/LICENSE)
