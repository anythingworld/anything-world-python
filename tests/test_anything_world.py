import pytest

from context import anything_world as aw

@pytest.mark.asyncio
async def test_find_by_name():
    client = aw.AWClient()
    response = await client.find_by_name(model_name="my cat")
    assert response, 'No response from /anything endpoint'


@pytest.mark.asyncio
async def test_find():
    client = aw.AWClient()
    response = await client.find(search_query="caat")
    assert response, 'No response from /anything endpoint'


@pytest.mark.asyncio
async def test_404_on_find():
    client = aw.AWClient()
    try:
        _ = await client.find(search_query="ararate")
    except Exception as e:
        assert e, 'No exception raised for 404 search query'


@pytest.mark.asyncio
async def _test_send_example_cat_to_animate():
    client = aw.AWClient()
    animate_response = await client.animate('./examples/cat', 'some_cat', 'cat', is_symmetric=True)
    assert animate_response, 'No response from /animate endpoint'
    model_id = animate_response["model_id"]

    is_finished = await client.is_animation_done(model_id)
    assert not is_finished, 'Model is finished before polling'

    animated_response = await client.get_animated_model(model_id, verbose=True)
    assert animated_response, 'No response from polling endpoint'

    is_finished = await client.is_animation_done(model_id)
    assert is_finished

