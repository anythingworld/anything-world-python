# Anything World Python Client

Python library and CLI for Anything World API.

# Installing

```bash
pip install anythingworld
```

# Using

First of all, edit the provided `env.example` file with the right API key and rename
it to `.env`.

## From Python

```python
from anythingworld import AWClient

# Create a client to be able to query Anything World's API
client = AWClient()

# Upload files from ./examples/cat folder to be animated
response = await client.animate('./examples/cat', 'some_cat', 'cat', is_symmetric=True)

# Response has the model_id of the 3D model that our AI pipeline is currently animating
model_id = response["model_id"]

# Runs a long-polling loop, starting it only after 2 minutes and after that,
# checking every 5 secs if the API is done animating the model
animated_response = await client.get_animated_model(model_id, waiting_time=5, warmup_time=120)

# Check if our AI pipeline is done animating the model
is_finished = await client.is_animation_done(model_id)
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
anything animate ./examples/cat "some cat" "cat" --is_symmetric
anything get_animated_model <MODEL_ID>
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
python -m build
twine upload dist/anything-world-<x.y.z>.tar.gz
```

# License

This Python module has a MIT-style license, as found in the LICENSE file.

The cat model in `examples/cat` folder is from Google Poly (CC-BY 4.0) license.

The ASCII logo was generated by https://patorjk.com/software/taag/ using the
original font fuzzy.flf by Juan Car (jc@juguete.quim.ucm.es).
