# Anything World Python Client

Python library and CLI for Anything World API.

To use this package you'll need to obtain a valid Anything World API key.
Please, create an account in
[our website](https://app.anything.world/register) and then visit
[your profile page](https://app.anything.world/profile) to
get access to your API key.

Before sending your 3D models to be animated, please make sure to follow [our guidelines](https://anything-world.gitbook.io/anything-world/api/preparing-your-3d-model)
on preparing your 3D model for success.

To understand better the underlying web requests called by this
Python package, please check our
[API documentation](https://anything-world.gitbook.io/anything-world/api/rest-api-references).

For more information of what changed between versions, please check the
[CHANGELOG](./CHANGELOG.md) file.

# Installing

```bash
pip install anything-world
```

# Using

First of all, create a new `.env` file with your Anything World API key:

```bash
AW_API_KEY=<YOUR API KEY>
```

## From Python

This library provides both synchronous and asynchronous implementations.
The sync implementation is based on `requests` and tries to keep dependencies
at minimum (i.e. no need to install `asyncio` nor `aiohttp`). However,
if you use-case requires async calls, please follow the next section for its
implementation.

## Sync

### Animating an existing model

```python
from anything_world.sync_api import AWClient
from dotenv import load_dotenv
load_dotenv()

# Create a client to be able to query Anything World's API
client = AWClient()

# Search for 3D models of `cats`:
response = client.find('cats')

# Upload files from ./examples/cat folder to be animated
response = client.animate(
    files_dir='./examples/cat',
    model_name='some_cat',
    model_type='cat',
    auto_rotate=True,
    is_symmetric=True
)

# If the `model_type` is not given, the AI pipeline will try to find it automatically!
response = client.animate(
    files_dir='./examples/cat',
    model_name='some_cat',
    auto_rotate=True,
    is_symmetric=True
)

# Response has the model_id of the 3D model that our AI pipeline is currently animating
model_id = response["model_id"]

# Runs a long-polling loop, starting it only after 10 seconds and after that,
# checking every 5 secs if the API is done animating the model
model_data = client.get_animated_model(
    model_id=model_id,
    waiting_time=5,
    warmup_time=10,
    verbose=True
)

# Check if our AI pipeline is done animating the model
is_finished = client.is_animation_done(model_id)
assert is_finished == True

# Gets all model data
model_data = client.get_model(model_id)
```

### Generating 3D models from text or image prompts

You can also generate 3D models by providing a text prompt:

```python
response = client.generate_from_text(
    prompt="cow using a helmet",
)

model_data = client.get_generated_model(
    model_id = response["model_id"]
)
```

Or by providing an image:

```python
response = client.generate_from_image(
    file_path = "./examples/cowboy.jpg",
)

model_data = client.get_generated_model(
    model_id = response["model_id"]
)
```

### Generating AND ANIMATING 3D models from text or image prompts

Anything World is the only place where you can not only generate, but
animate 3D models giving only a single text prompt:

```python
response = client.generate_animated_from_text(
    prompt="cow using a helmet",
)

model_data = client.get_generated_model(
    model_id = response["model_id"]
)
```

Or by providing a single image:

```python
response = client.generate_animated_from_image(
    file_path = "./examples/cowboy.jpg",
)

model_data = client.get_generated_model(
    model_id = response["model_id"]
)
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
anything find "cat"
anything animate ./examples/cat "some cat" --is_symmetric --auto_rotate
anything get_animated_model <MODEL_ID> --verbose
anything get_model <MODEL_ID>

anything generate_from_text "cow with a helmet"
anything generate_from_image ./examples/cowboy.jpg "a cowboy"
anything get_generated_model <MODEL_ID>

anything generate_animated_from_text "soldier"
anything generate_animated_from_image ./examples/cowboy.jpg "a cowboy"
```

To know more about the parameters of a specific command, just run the
command with no arguments to get a help message:

```bash
anything find
```

For more information about a command, please run the command with the `--help`
suffix:

```bash
anything find --help
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

First bump the version in `pyproject.toml` and then:

```bash
rm -rf dist/*
python3 -m build
python3 -m twine upload dist/* --username __token__ --password <password>
```

# License

This Python module has a MIT-style license, as found in the LICENSE file.

The cat model in `examples/cat` folder is from Google Poly (CC-BY 4.0) license.

The ASCII logo was generated by https://patorjk.com/software/taag/ using the
original font fuzzy.flf by Juan Car (jc@juguete.quim.ucm.es).
