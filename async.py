"""File to test how fast is async against no async"""

from typing import List
from time import time
import asyncio
import aiohttp
from pydantic import BaseModel


class Value(BaseModel):
    """Class to type Value

    Args:
        BaseModel: Checks if the item has all attr
    """

    albumId: int
    id: int
    title: str
    url: str
    changed: str = None


async def fetch(url: str, session: aiohttp.ClientSession):
    """Def to be used as a util to fetch async requests

    Args:
        url (str): Link of the request
        session (aiohttp.ClientSession): Class to handle the async request

    Returns:
        Value: Data in Value format
    """
    async with session.get(url) as response:
        data = await response.json()
        return Value(**data)


class HandleValue:
    """Class that contains all methods to handle value"""

    def __init__(self) -> None:
        self.__values: List[Value] = []

        # allow multiple threads to do the work
        self.__semaphore = asyncio.Semaphore(100)

    async def generate_values(self, session: aiohttp.ClientSession):
        """Async method to generate values

        Args:
            session (aiohttp.ClientSession): Class to use async to fetch all data from url
        """

        async def fetch_with_semaphore(url):
            async with self.__semaphore:
                return await fetch(url, session)

        url = "https://jsonplaceholder.typicode.com/photos/"

        tasks = [fetch_with_semaphore(url + str(i)) for i in range(1, 5000)]
        self.__values = await asyncio.gather(*tasks)

    async def change_value(self, value: Value):
        """Async method to change value adding 'changed' = 'real_changed'

        Args:
            value (Value): Item of type Value

        Returns:
            Value: Item of type Value updated
        """
        value.changed = "real_changed"
        return value

    async def manipulate_values(self) -> List[Value]:
        """Async method to manipulate values calling the method change_value

        Returns:
            List[Value]: All values already changed
        """
        tasks = []

        async def change_value_with_semaphore(value):
            async with self.__semaphore:
                return await self.change_value(value)

        for value in self.__values:
            tasks.append(change_value_with_semaphore(value))

        self.__values = await asyncio.gather(*tasks)

    def get_values(self):
        """Getter for self.__values

        Returns:
            List[Value]: List of values
        """
        return self.__values


async def main():
    """Main async def to handle all project"""
    start_time = time()

    handle_value = HandleValue()

    async with aiohttp.ClientSession() as session:
        # Generate values from jsonplaceholder api
        await handle_value.generate_values(session)

        # Manipulate values adding new field
        await handle_value.manipulate_values()

        # Return values using get_values
        values = handle_value.get_values()

        print(values)

    end_time = time()

    # Calcs time spend
    print("tempo total: ", end_time - start_time)


if __name__ == "__main__":
    asyncio.run(main())
