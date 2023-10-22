from api.converter import check_length
from pytest import mark

@mark.asyncio
async def test_check_length():
    assert await check_length("https://youtube.com/watch?v=MGNZJib6KxI") == 369



