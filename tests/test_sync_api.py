import pytest

from context import sync_api

def test_sync_find_by_name():
    client = sync_api.AWClient()
    response = client.find_by_name(model_name="my cat")
    assert response, 'No response from /anything endpoint'


def test_sync_find():
    client = sync_api.AWClient()
    response = client.find(search_query="caat")
    assert response, 'No response from /anything endpoint'


def test_sync_404_on_find():
    client = sync_api.AWClient()
    try:
        _ = client.find(search_query="ararate")
    except Exception as e:
        assert e, 'No exception raised for 404 search query'


def test_sync_send_example_cat_to_animate():
    client = sync_api.AWClient()
    animate_response = client.animate('./examples/cat', 'some_cat', 'cat', is_symmetric=True)
    print("animate response", animate_response)
    assert animate_response, 'No response from /animate endpoint'
    model_id = animate_response["model_id"]
    is_finished = client.is_animation_done(model_id)
    assert not is_finished, 'Model is finished before polling'

    animated_response = client.get_animated_model(model_id, verbose=True)
    assert animated_response, 'No response from polling endpoint'

    is_finished = client.is_animation_done(model_id)
    assert is_finished


def test_sync_send_example_cat_for_extra_formats_to_animate():
    client = sync_api.AWClient()
    animate_response = client.animate('./examples/cat', 'some_cat', 'cat', is_symmetric=True)
    print("animate response", animate_response)
    assert animate_response, 'No response from /animate endpoint'
    model_id = animate_response["model_id"]
    is_finished = client.is_animation_done(model_id, extra_formats=True)
    assert not is_finished, 'Model is finished before polling'

    animated_response = client.get_animated_model(model_id, extra_formats=True, verbose=True)
    assert animated_response, 'No response from polling endpoint'

    is_finished = client.is_animation_done(model_id, extra_formats=True)
    assert is_finished
