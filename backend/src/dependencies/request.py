import aiohttp


# Description: Request module for aiohttp
async def get_aiohttp_session():
    async with aiohttp.ClientSession() as session:
        yield session
