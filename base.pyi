import pathlib
from asyncio.queues import Queue
from typing import Any, AsyncGenerator, Coroutine, Generator, List, Union

from requests.models import Response
from requests.sessions import Session

from ecommerce_scrapper.models import Product

SESSION = Session()

QUEUE = Queue()

CACHED_PRODUCTS = []

FAILED_URLS = []



class URLsGenerator:
    data: List[dict]

    def __init__(self) -> None: ...
    def __repr__(self) -> str: ...

    def __iter__(self) -> Generator[List[dict], None, List[dict]]: ...

    async def chunks(
        self,
        k: int = ...
    ) -> AsyncGenerator[tuple[str], None]: ...


async def parse_responses(
    chunked_responses: tuple[str],
    company: str = ...
) -> Coroutine[List[Product]]: ...


async def create_chunks(
    urls: List[str],
    k: int = ...
) -> Generator[tuple[str], Any, None]: ...


async def sender(
    index: int,
    url: str
) -> Coroutine[Union[Response, False]]: ...


async def write_json(
    data: List[dict[str, str]],
    path: pathlib.Path
) -> Coroutine[None]: ...


async def webhook(data: List[dict[str, str]]) -> Coroutine[Response]: ...


async def main() -> None: ...
