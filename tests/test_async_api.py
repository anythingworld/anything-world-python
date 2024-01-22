import pytest
import asyncio

from context import async_api

@pytest.mark.asyncio
async def test_async_find_by_name():
    client = async_api.AWClient()
    response = await client.find_by_name(model_name="my cat")
    assert response, 'No response from /anything endpoint'


@pytest.mark.asyncio
async def test_async_find():
    client = async_api.AWClient()
    response = await client.find(search_query="caat")
    assert response, 'No response from /anything endpoint'


@pytest.mark.asyncio
async def test_async_404_on_find():
    client = async_api.AWClient()
    try:
        _ = await client.find(search_query="ararate")
    except Exception as e:
        assert e, 'No exception raised for 404 search query'


@pytest.mark.asyncio
async def _test_async_send_example_cat_to_animate():
    client = async_api.AWClient()
    animate_response = await client.animate('./examples/cat', 'some_cat', 'cat', is_symmetric=True)
    assert animate_response, 'No response from /animate endpoint'
    model_id = animate_response["model_id"]
    is_finished = await client.is_animation_done(model_id)
    assert not is_finished, 'Model is finished before polling'

    animated_response = await client.get_animated_model(model_id)
    assert animated_response, 'No response from polling endpoint'

    is_finished = await client.is_animation_done(model_id)
    assert is_finished


@pytest.mark.asyncio
async def _test_async_send_example_cat_for_extra_formats_to_animate():
    client = async_api.AWClient()
    animate_response = await client.animate('./examples/cat', 'some_cat', 'cat', is_symmetric=True)
    assert animate_response, 'No response from /animate endpoint'
    model_id = animate_response["model_id"]
    is_finished = await client.is_animation_done(model_id, extra_formats=True)
    assert not is_finished, 'Model is finished before polling'

    animated_response = await client.get_animated_model(model_id, extra_formats=True)
    assert animated_response, 'No response from polling endpoint'

    is_finished = await client.is_animation_done(model_id, extra_formats=True)
    assert is_finished