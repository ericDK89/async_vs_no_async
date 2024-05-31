import asyncio
import aiohttp
from pydantic import BaseModel
from typing import List
from tqdm import tqdm
from time import time


class Value(BaseModel):
    albumId: int
    id: int
    title: str
    url: str
    changed: str = None


fake_mock = []


async def fetch(url: str, session: aiohttp.ClientSession):
    async with session.get(url) as response:
        data = await response.json()
        return Value(**data)


async def generate_values(session: aiohttp.ClientSession):
    semaphore = asyncio.Semaphore(10)
    values = []

    async def fetch_with_semaphore(url):
        async with semaphore:
            return await fetch(url, session)

    url = "https://jsonplaceholder.typicode.com/photos/"

    tasks = [fetch_with_semaphore(url + str(i)) for i in tqdm(range(1, 1000))]
    values = await asyncio.gather(*tasks)

    return values


async def change_value(value: Value):
    value.changed = "real_changed"
    return value


async def manipulate_values(values: List[Value]):
    semaphore = asyncio.Semaphore(10)
    tasks = []

    async def change_value_with_semaphore(value):
        async with semaphore:
            return await change_value(value)

    for value in tqdm(values):
        tasks.append(change_value_with_semaphore(value))

        if len(tasks) % 10 == 0:
            result = await asyncio.gather(*tasks)
            fake_mock.extend(result)
            tasks = []

    if tasks:
        result = await asyncio.gather(*tasks)
        fake_mock.extend(result)


async def main():
    start_time = time()

    async with aiohttp.ClientSession() as session:
        # Generate values from jsonplaceholder api
        values = await generate_values(session)

        # Manipulate values adding new field
        await manipulate_values(values)

        for value in fake_mock:
            print(value)

    end_time = time()

    print(end_time - start_time)


if __name__ == "__main__":
    asyncio.run(main())
