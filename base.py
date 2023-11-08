import asyncio
import json
import os
import random
from asyncio.queues import Queue
from itertools import islice

from bs4 import BeautifulSoup
from requests.models import Request
from requests.sessions import Session

from ecommerce_scrapping_1 import PROJECT_PATH, URLS_FILE, logger
from ecommerce_scrapping_1.parsers import COMPANIES

SESSION = Session()

QUEUE = Queue()

QUEUE2 = []

CACHED_PRODUCTS = []

FAILED_URLS = []


class URLsGenerator:
    def __init__(self):
        with open(URLS_FILE, mode='r') as f:
            self.data = json.load(f)

    def __repr__(self):
        return f'<{self.__class__.__name__} [{len(self.data)}]>'

    def __iter__(self):
        return self.data
    
    async def chunks(self, k=100):
        it = iter(self.data)
        while (batch := tuple(islice(it, k))):
            yield batch


class UserAgents:
    def __init__(self):
        with open(PROJECT_PATH / 'user_agents.txt', mode='r') as f:
            data = f.read()
            self.user_agents = data.split('\n')

    def __repr__(self):
        return f'<{self.__class__.__name__} [{len(self.user_agents)}]>'

    def get(self):
        return random.choice(self.user_agents)


async def parse_responses(chunked_responses, company='orchestra'):
    products = []
    for response in chunked_responses:
        try:
            soup = BeautifulSoup(response.content, 'html.parser')
        except:
            logger.critical(f'Could not par response. Got: {response}')
            continue
        else:
            func = COMPANIES[company]
            products.append(func(soup, response))
    return products


async def create_chunks(urls, k=5):
    it = iter(urls)
    while (batch := tuple(islice(it, k))):
        yield batch


async def sender(index, url):
    await asyncio.sleep(2)
    user_agent = UserAgents()
    headers = {'User-Agent': user_agent.get()}

    try:
        request = Request(method='get', url=url, headers=headers)
        prepared_request = SESSION.prepare_request(request)
        response = SESSION.send(prepared_request)
    except Exception as e:
        FAILED_URLS.append(url)
        logger.error(f'Request failed for: {url}')
        logger.error(e)
        return False
    else:
        if response.ok:
            logger.info(f"Sent request number: {index}")
            return response
        logger.error(f'No response for: {url}')
        return False
    

async def write_json(data, path):
    with open(path, mode='w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
        logger.info(f'Wrote: {len(data)} products')

async def webhook(data):
    webhook_url = os.getenv('webhook')
    if webhook_url is not None:
        request = Request(
            method='post', 
            url=webhook_url,
            json=data,
            headers={'Content-Type': 'application/json'}
        )
        prepared_request = SESSION.prepare_request(request)
        
        try:
            response = SESSION.send(prepared_request)
        except:
            pass
        else:
            return response


async def main():
    logger.info('Started...')
    instance = URLsGenerator()
    
    async for chunk in instance.chunks():
        await QUEUE.put(chunk)

    while not QUEUE.empty():
        chunks = await QUEUE.get()

        tasks = []
        for i, url in enumerate(chunks):
            tasks.append(asyncio.create_task(sender(i, url)))
            
        responses = await asyncio.gather(*tasks)
        products = await parse_responses(responses)
        
        items = [product.as_dict() for product in products]
        CACHED_PRODUCTS.extend(items)
        
        await write_json(CACHED_PRODUCTS, PROJECT_PATH / 'products.json')
        await write_json(FAILED_URLS, PROJECT_PATH / 'failed_urls.json')
        await webhook(items)

        wait_time = random.randrange(3, 15)
        logger.debug(f'Waiting {wait_time}s')
        await asyncio.sleep(wait_time)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        asyncio.run(write_json(CACHED_PRODUCTS, PROJECT_PATH / 'products.json'))
        asyncio.run(write_json(FAILED_URLS, PROJECT_PATH / 'failed_urls.json'))
