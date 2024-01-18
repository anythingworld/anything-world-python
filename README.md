# Anything World Python Client

Python library and CLI for Anything World API.

:warning: Please make sure to follow [our guidelines](https://anything-world.gitbook.io/anything-world/)
on preparing your 3D model for success before sending them to be animated,
by using our `/animate` endpoint.

For more information of what changed between versions, please check the
[CHANGELOG](./CHANGELOG.md) file.

# Installing

```bash
pip install anything-world
```

# Using

First of all, create a new `.env` file with the right API key and URLs:

```bash
AW_API_KEY=<YOUR API KEY>
AW_API_URL=https://api.anything.world
AW_POLLING_URL=https://api.anything.world/user-processed-model
```

## From Python

This library provides both synchronous and asynchronous implementations.
The sync implementation is based on `requests` and tries to keep dependencies
at minimum (i.e. no need to install `asyncio` nor `aiohttp`). However,
if you use-case requires async calls, please follow the next section for its
implementation.

## Sync

```python
from anything_world.sync_api import AWClient

# Create a client to be able to query Anything World's API
client = AWClient()

# Search for 3D models of `cats`:
response = client.find('cats')

# Upload files from ./examples/cat folder to be animated
response = client.animate('./examples/cat', 'some_cat', 'cat', is_symmetric=True)

# Response has the model_id of the 3D model that our AI pipeline is currently animating
model_id = response["model_id"]

# Runs a long-polling loop, starting it only after 2 minutes and after that,
# checking every 5 secs if the API is done animating the model
animated_response = client.get_animated_model(model_id, waiting_time=5, warmup_time=120)

# Check if our AI pipeline is done animating the model
is_finished = client.is_animation_done(model_id)
assert is_finished == True
```

## Async

```python
import asyncio
from anything_world.async_api import AWClient

# Create a client to be able to query Anything World's API
client = AWClient()

# Search for 3D models of `cats`:
response = asyncio.run(
    client.find('cats'))

# Upload files from ./examples/cat folder to be animated
response = asyncio.run(
    client.animate('./examples/cat', 'some_cat', 'cat', is_symmetric=True))

# Response has the model_id of the 3D model that our AI pipeline is currently animating
model_id = response["model_id"]

# Runs a long-polling loop, starting it only after 2 minutes and after that,
# checking every 5 secs if the API is done animating the model
animated_response = asyncio.run(
    client.get_animated_model(model_id, waiting_time=5, warmup_time=120))

# Check if our AI pipeline is done animating the model
is_finished = asyncio.run(
    client.is_animation_done(model_id))
assert is_finished == True
```

## From CLI

All `AWClient` methods are exposed as commands of the `anything` CLI tool.
Just call the `anything` tool and it will display a manual page of the
available commands:

```bash
anything
```

You can do exactly the same we did in Python before through the CLI:

```bash
anything find <QUERY STRING>
anything animate ./examples/cat "some cat" "cat" --is_symmetric
anything get_animated_model <MODEL_ID>
...
```

# Developing

## Installing from source

```bash
git clone git@github.com:anythingworld/anything-world-python.git
cd anything-world-python
python3 -m venv venv
source venv/bin/activate
pip install -e .
```

## Testing

```bash
pytest -v -s
```

## Releasing a new pip package

Bump the version in `pyproject.toml` and then:

```bash
rm -rf dist/*
python3 -m build
python3 -m twine upload dist/*
```

# License

This Python module has a MIT-style license, as found in the LICENSE file.

The cat model in `examples/cat` folder is from Google Poly (CC-BY 4.0) license.

The ASCII logo was generated by https://patorjk.com/software/taag/ using the
original font fuzzy.flf by Juan Car (jc@juguete.quim.ucm.es).
