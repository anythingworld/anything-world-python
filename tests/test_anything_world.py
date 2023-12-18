import pytest

from context import anything_world as aw

@pytest.mark.asyncio
async def test_animate():
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
