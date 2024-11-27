import pytest

from pprint import pprint
from context import sync_api


def test_sync_find_by_name():
    """
    Test the find_by_name() method of the AWClient class.

    It should return a response from the /anything endpoint when
    searching for a model by name.
    """
    client = sync_api.AWClient()
    response = client.find_by_name(model_name="my cat")
    assert response, 'No response from /anything endpoint'
    pprint(response)


def test_sync_find():
    """
    Test the find() method of the AWClient class.

    It should return a response from the /anything endpoint when
    searching for models by a query string.
    """
    client = sync_api.AWClient()
    response = client.find(search_query="cat")
    assert response, 'No response from /anything endpoint'
    pprint(response)


def test_sync_404_on_find():
    """
    Test the find() method of the AWClient class.

    It should raise an exception when the search query does not return any
    results.
    """
    client = sync_api.AWClient()
    try:
        _ = client.find(search_query="ararate")
    except Exception as e:
        assert e, 'No exception raised for 404 search query'


def test_sync_send_example_cat_to_animate():
    """
    Test the animate() method of the AWClient class.

    It should return a response from the /animate endpoint when
    sending a model (with files stored in `files_dir`) to animate.
    """
    client = sync_api.AWClient()
    animate_response = client.animate(
        files_dir='./examples/cat',
        model_name='some_cat',
        model_type='cat',
        is_symmetric=True
    )
    assert animate_response, 'No response from /animate endpoint'
    model_id = animate_response["model_id"]

    is_finished = client.is_animation_done(model_id)
    assert not is_finished, 'Model is finished before polling'

    animated_response = client.get_animated_model(model_id, verbose=True)
    assert animated_response, 'No response from polling endpoint'

    is_finished = client.is_animation_done(model_id)
    assert is_finished
    pprint(animated_response)


def test_sync_send_example_cat_for_extra_formats_to_animate():
    """
    Test the animate() method of the AWClient class.

    It should return a response from the /animate endpoint when
    sending a model (with files stored in `files_dir`) to animate.
    And it should return the extra formats (glb, usdz, and gltf) when
    polling for the animated model.
    """
    client = sync_api.AWClient()
    animate_response = client.animate(
        files_dir='./examples/cat',
        model_name='some_cat',
        model_type='cat',
        is_symmetric=True
    )
    assert animate_response, 'No response from /animate endpoint'
    model_id = animate_response["model_id"]

    is_finished = client.is_animation_done(model_id, extra_formats=True)
    assert not is_finished, 'Model is finished before polling'

    animated_response = client.get_animated_model(
        model_id=model_id,
        extra_formats=True,
        verbose=True
    )
    assert animated_response, 'No response from polling endpoint'

    is_finished = client.is_animation_done(model_id, extra_formats=True)
    assert is_finished
    pprint(animated_response)


def test_sync_generate_from_text():
    """
    Test the generate_from_text() method of the AWClient class.

    It should return a response from the /text-to-3d endpoint when
    generating a 3D model from a text prompt.
    """
    client = sync_api.AWClient()
    response = client.generate_from_text(
        prompt="blue cat with zebra stripes"
    )
    assert response, 'No response from generate_from_text'
    assert "model_id" in response, 'No model_id in response'

    response = client.get_generated_model(response["model_id"])

    assert response, 'No response from get_generated_model'
    assert "model" in response, 'No model in response'
    assert "mesh" in response["model"], 'No mesh in response'
    assert "glb" in response["model"]["mesh"], 'No glb in response'
    pprint(response)


def test_sync_generate_from_image():
    """
    Test the generate_from_image() method of the AWClient class.

    It should return a response from the /image-to-3d endpoint when
    generating a 3D model from an image file.
    """
    client = sync_api.AWClient()
    response = client.generate_from_image(
        file_path="./examples/cowboy.jpg",
        model_name="cowboy",
    )
    assert response, 'No response from generate_from_image'
    assert "model_id" in response, 'No model_id in response'

    response = client.get_generated_model(response["model_id"])

    assert response, 'No response from get_generated_model'
    assert "model" in response, 'No model in response'
    assert "mesh" in response["model"], 'No mesh in response'
    assert "glb" in response["model"]["mesh"], 'No glb in response'
    pprint(response)


def test_sync_generate_animated_from_text():
    """
    Test the generate_animated_from_text() method of the AWClient class.

    It should return a response from the /text-to-3d and /animate endpoints
    when generating an animated 3D model from a text prompt.
    """
    client = sync_api.AWClient()
    response = client.generate_animated_from_text(
        prompt="blue cat with zebra stripes"
    )
    assert response, 'No response from generate_from_text'
    pprint(response)


def test_sync_generate_animated_from_image():
    """
    Test the generate_animated_from_image() method of the AWClient class.

    It should return a response from the /image-to-3d and /animate endpoints
    when generating an animated 3D model from an image file.
    """
    client = sync_api.AWClient()
    response = client.generate_animated_from_image(
        file_path="./examples/cowboy.jpg",
        model_name="cowboy",
    )
    assert response, 'No response from generate_from_image'
    pprint(response)
