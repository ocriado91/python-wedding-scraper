#!/usr/bin/env python3
'''
Python script for Wedding places from
spanish website https://www.bodas.net/
'''

import argparse
import logging
import pandas as pd
import requests

from bs4 import BeautifulSoup
from elasticsearch import Elasticsearch

from wedding_site import Place

es = Elasticsearch("http://localhost:9200")

mappings = {
    "properties" : {
        "name" : {"type": "keyword"},
        "price": {"type": "integer"},
        "guests": {"type": "integer_range"},
        "coordinates": {"type": "geo_point"},
        "website": {"type": "keyword"},
        "review_score": {"type": "float"},
        "has_more_info": {"type": "boolean"},
        "multiple_events": {"type": "boolean"},
        "location_type": {"type": "keyword"}
    }
}

TIMEOUT=5

LOG_FORMATTER = '%(asctime)s'\
                '- %(levelname)s - %(module)s - %(funcName)s - %(message)s'
logging.basicConfig(format=LOG_FORMATTER)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

URL='https://www.bodas.net/busc.php?id_grupo=1&id_provincia=3035&NumPage='

def save_data_to_csv(data: dict) -> None:
    '''
    Save data into CSV format
    '''

    acc_data = []
    print(data)
    for place in data.keys():
        if ( data[place]['price'] and
            data[place]['location']['lat'] and
            data[place]['location']['lon'] and
            data[place]['guests']):
            doc = {
                "name": place,
                "price": data[place]['price'],
                "min_guests": data[place]['guests']['lte'],
                "max_guests": data[place]['guests']['gte'],
                "latitude": data[place]['location']['lat'],
                "longitude": data[place]['location']['lon'],
                "website": data[place]['website'],
                "review_score": data[place]['review_score'],
                "has_more_info": data[place]["has_more_info"],
                "multiple_events": data[place]["multiple_events"],
                "location_type": data[place]["location_type"]

            }
            acc_data.append(doc)
        else:
            logger.warning('None enough data detected for %s', place)

    df = pd.DataFrame.from_dict(acc_data)
    df.to_csv(r'data.csv', index=False, header=True)
    logger.info('Successfully saved data into CSV format')

def inject_data(data: dict) -> None:
    '''
    Inject data into Elasticsearch
    '''

    logger.info('Injecting data into Elasticsearch...')

    es.indices.delete(index='test')
    es.indices.create(index='test', mappings=mappings)

    idx = 0
    for place in data.keys():
        if data[place]['price']:
            doc = {
                "name": place,
                "price": data[place]['price'],
                "guests": data[place]['guests'],
                "coordinates": data[place]['location'],
                "website": data[place]['website'],
                "review_score": data[place]['review_score'],
                "has_more_info": data[place]["has_more_info"],
                "multiple_events": data[place]["multiple_events"],
                "location_type": data[place]["location_type"]

            }
            idx += 1
            es.index(index='test', id=idx, document=doc)
        else:
            logger.warning('None price detected for %s', place)

    es.indices.refresh(index='test')
    logger.info('Successfully injected data (%d) into Elasticsearch', idx)

def parse_wedding_site(urlSite: str) -> Place:
    '''
    Extract data by each place
    '''

    return Place(urlSite).build_data()


def extract_data_from_list_page(first_page: int, last_page: int)->list:
    '''
    Extract URL of wedding site list page
    '''

    # Get all places page by page
    places = []
    for idx in range(first_page, last_page):
        urlSite = URL + str(idx)
        logger.info('Using URL = %s', urlSite)
        page = requests.get(urlSite, timeout=TIMEOUT)
        soup = BeautifulSoup(page.content, 'html.parser')

        # Detect list of places in current page list
        places_parent = soup.find_all('a',
                                    class_='vendorTile__title')
        places.extend(places_parent)

    # Parse data place by place
    logger.debug('Found %d wedding places', len(places))
    data = {}
    for idx, place in enumerate(places):
        logger.debug('%d/%d wedding website: %s', idx + 1,
                                                  len(places),
                                                  place['href'])
        site_data = parse_wedding_site(place['href'])
        if site_data:
            data.update(site_data)

    return data


def argument_parser() -> argparse.ArgumentParser:
    '''
    Argument parser function
    '''

    args = argparse.ArgumentParser()
    args.add_argument('--first_page',
                      help='First page to extract data',
                      type=int,
                      default=1)
    args.add_argument('--last_page',
                      help='Last page to extract data',
                      type=int,
                      default=11)
    args.add_argument('--store_csv',
                      help='Store data into CSV format',
                      action='store_true')

    return args.parse_args()

def main():
    '''
    Main function
    '''

    logger.info('Starting Wedding Scrapper script')
    args = argument_parser()
    data = extract_data_from_list_page(args.first_page, args.last_page)

    # Check if store_csv flag argument is set
    # if not, inject data into Elasticsearch
    if args.store_csv:
        logger.info('Storing data into CSV format')
        save_data_to_csv(data)
    else:
        logger.info('Storing data into Elasticsearch')
        inject_data(data)


if __name__ == '__main__':
    main()
