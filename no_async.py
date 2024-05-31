import requests
from tqdm import tqdm
from typing import List
from pydantic import BaseModel
from time import time


class Value(BaseModel):
    albumId: int
    id: int
    title: str
    url: str
    changed: str = None


fake_mock = []


def fetch(url: str):
    response = requests.get(url)
    data = response.json()
    return Value(**data)


def generate_values():
    values = []

    for i in tqdm(range(1, 5000)):
        values.append(fetch(f"https://jsonplaceholder.typicode.com/photos/{i}"))

    return values


def change_value(value: Value):
    value.changed = "real_changed"
    return value


def manipulate_values(values: List[Value]):
    tasks = [change_value(value) for value in values]
    fake_mock.extend(tasks)


def main():
    start_time = time()

    values = generate_values()

    manipulate_values(values)

    for value in fake_mock:
        print(value)

    end_time = time()

    print(end_time - start_time)


if __name__ == "__main__":
    main()
