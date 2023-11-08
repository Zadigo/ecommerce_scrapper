import datetime
import re
import unicodedata
from urllib.parse import urlparse, urlunparse

import pytz
from regex import R

from ecommerce_scrapping_1.models import Product


def drop_null(items, remove_empty_strings=True):
    for item in items:
        if remove_empty_strings and item == '':
            continue

        if item is not None:
            yield item


def normalize_spaces(text_or_tokens):
    """Remove excess spaces from a given text"""
    if isinstance(text_or_tokens, str):
        tokens = text_or_tokens.split(' ')
    else:
        tokens = text_or_tokens
    return ' '.join(drop_null(tokens))


def clean_text(text, encoding='utf-8'):
    if not isinstance(text, str):
        return text

    text = text.replace('\n', '')
    text = unicodedata.normalize('NFKD', text)
    text = text.encode(encoding).decode()
    return normalize_spaces(text)


def get_origin(response):
    return urlparse(response.url)


def build_origin(response):
    origin = get_origin(response)
    return f'{origin.scheme}://{origin.netloc}'


def join_url(response, path):
    if path.startswith('/'):
        origin = get_origin(response)
        return urlunparse((
            origin.scheme,
            origin.netloc,
            path,
            None,
            None,
            None
        ))
    return path


def orchestra(soup, response):
    date = datetime.datetime.now(tz=pytz.UTC)

    try:
        breadcrumbs = soup.find('ol', {'class': 'breadcrumb'}).find_all('li')
        breadcrumbs = ' > '.join([clean_text(breadcrumb.text) for breadcrumb in breadcrumbs])
    except:
        breadcrumbs = None

    try:
        info_section = soup.find('div', {'class': 'col-12 col-lg-5 product-right add-to-cart-container'})
    except:
        pass
    else:
        try:
            price1 = clean_text(info_section.find('span', {'class': 'product-price-club'}).text)
        except:
            price1 = None

        try:
            price2 = clean_text(info_section.find('span', {'class': 'product-price-not-club'}).text)
        except:
            price2 = None

        price = str([price1, price2])

    try:
        name = soup.find('h1', {'class': 'product-name'})
        name = clean_text(name.text)
    except:
        name = None

    try:
        reference = soup.find('span', {'class': 'product-specification-reference'})
        reference = clean_text(reference.text)
    except:
        reference = None

    try:
        colors = soup.find('div', {'class': 'product-colors-list'}).find_all('a', {'class': 'product-colors-item'})
    except:
        colors = []
    else:
        colors = len(colors)

    try:
        description = soup.find('div', {'class': 'product-description-text'})
        description = clean_text(description.text)
    except:
        description = None
    
    try:
        image = soup.find('div', {'class': 'product-image'})
    except:
        image = None
    else:
        result = re.search(r'url\((.*)\)', image.attrs['style'])
        if result:
            image = join_url(response, result.group(1))
        else:
            image = None

    try:
        color = soup.find('a', {'class': 'product-colors-item-active'}).find('span', {'class': 'product-colors-item-caption'})
        color = clean_text(color.text)
    except:
        color = None

    try:
        sizes = soup.find('div', {'class': 'product-sizes-list'}).find_all('a')
        sizes = [clean_text(size.text) for size in sizes]
    except:
        sizes = []
    
    return Product(
        name, 
        description, 
        price,
        company='Orchestra',
        company_url=build_origin(response),
        breadcrumb=breadcrumbs,
        date=str(date),
        url=response.url, 
        images=[image],
        sizes=sizes,
        color=color,
        number_of_colors=colors,
        id_or_reference=reference
    )


COMPANIES = {
    'orchestra': orchestra
}
