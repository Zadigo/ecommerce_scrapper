import datetime
import re
import unicodedata
from urllib.parse import urlparse, urlunparse

import pytz
from regex import R

from ecommerce_scrapper.models import Product


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
        breadcrumbs = ' > '.join([clean_text(breadcrumb.text)
                                 for breadcrumb in breadcrumbs])
    except:
        breadcrumbs = None

    try:
        info_section = soup.find(
            'div', {'class': 'col-12 col-lg-5 product-right add-to-cart-container'})
    except:
        pass
    else:
        try:
            price1 = clean_text(info_section.find(
                'span', {'class': 'product-price-club'}).text)
        except:
            price1 = None

        try:
            price2 = clean_text(info_section.find(
                'span', {'class': 'product-price-not-club'}).text)
        except:
            price2 = None

        price = str([price1, price2])

    try:
        name = soup.find('h1', {'class': 'product-name'})
        name = clean_text(name.text)
    except:
        name = None

    try:
        reference = soup.find(
            'span', {'class': 'product-specification-reference'})
        reference = clean_text(reference.text)
    except:
        reference = None

    try:
        colors = soup.find('div', {'class': 'product-colors-list'}
                           ).find_all('a', {'class': 'product-colors-item'})
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
        color = soup.find('a', {'class': 'product-colors-item-active'}
                          ).find('span', {'class': 'product-colors-item-caption'})
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


# let name = getText(document.querySelector('.lft-product-info-name'))
# let description = getText(document.querySelector('.lft-product-info-description'))
# let material = getText(document.querySelector('.info-composition-wrapper'))
# let price = getText(document.querySelector('.lft-product-info-price .price'))
# // let discountPrice = getText(document.querySelector('.product-card__info.product-detail__add-to-cart-container .product-card__price--old'))
# let reference = getText(document.querySelector('.lft-product-info-reference'))
# let color = getText(document.querySelector('.lft-product-info-color'))

# let imageElements = Array.from(document.querySelectorAll('.lft-product-images .lft-product-image'))
# imageElements.forEach(x => x.classList.add('image-loaded'))
# let images = Array.from(imageElements).map(x => x.querySelector('img').src).filter(x => x && x !== "")

# // let breadcrumb = Array.from(document.querySelectorAll('ol.breadcrumb li')).map(x => x.textContent.trim()).join(' > ')
# let numberOfColors = document.querySelectorAll('div[class="lft-product-info-colors"] div[data-color-id]').length

def lefties(soup, response):
    date = datetime.datetime.now(tz=pytz.UTC)

    try:
        breadcrumbs = soup.find('ol', {'class': 'breadcrumb'}).find_all('li')
        breadcrumbs = ' > '.join([
            clean_text(breadcrumb.text)
            for breadcrumb in breadcrumbs])
    except:
        breadcrumbs = None

    try:
        info_section = soup.find(
            'div', {'class': 'col-12 col-lg-5 product-right add-to-cart-container'})
    except:
        pass
    else:
        try:
            price1 = clean_text(info_section.find(
                'span', {'class': 'product-price-club'}).text)
        except:
            price1 = None

        try:
            price2 = clean_text(info_section.find(
                'span', {'class': 'product-price-not-club'}).text)
        except:
            price2 = None

        price = str([price1, price2])

    try:
        attrs = {'class': 'lft-product-info-name lft-medium space-mobile'}
        name = soup.find('div', attrs)
        name = clean_text(name.text)
    except:
        name = None

    try:
        attrs = {'class': 'lft-product-info-reference'}
        reference = soup.find('div', attrs)
        reference = clean_text(reference.text)
    except:
        reference = None

    try:
        attrs = {'class': 'lft-product-info-colors'}
        colors = soup.find('div', attrs).find_all(
            'div', {'data-color-id': True})
    except:
        colors = []
    else:
        colors = len(colors)

    try:
        attrs = {'class': 'description-wrapper'}
        description = soup.find('div', attrs).find('span')
        description = clean_text(description.text)
    except:
        description = None

    try:
        image_elements = soup.find(
            'div', {'class': 'lft-product-images lft-product-image'})
        image = image_elements.find_all('img')[0].attrs.get('src', None)
    except:
        image = None

    try:
        color = soup.find('div', {'class': 'lft-product-info-color'})
        color = clean_text(color.text)
    except:
        color = None

    try:
        sizes = []
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
    'orchestra': orchestra,
    'lefties': lefties
}
