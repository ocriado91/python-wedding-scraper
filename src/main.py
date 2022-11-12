#!/usr/bin/env python3
'''
Python script for Wedding sites from
spanish site https://www.bodas.net/
'''

import argparse
import logging
import requests

from bs4 import BeautifulSoup

TIMEOUT=5

LOG_FORMATTER = '%(asctime)s'\
                '- %(levelname)s - %(module)s - %(funcName)s - %(message)s'
logging.basicConfig(format=LOG_FORMATTER)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

URL='https://www.bodas.net/busc.php?id_grupo=1&id_provincia=3035&NumPage='

def parse_wedding_site(urlSite: str)->None:
    '''
    Extract data from wedding sitepage
    '''

    logger.debug('Checking %s', urlSite)
    page = requests.get(urlSite, timeout=TIMEOUT)
    soup = BeautifulSoup(page.content, 'html.parser')

    # Extract title from wedding site
    title = soup.find_all('h1', class_='storefrontHeading__title')[0].string

    # Try to extract price from wedding site
    try:
        price = soup.find_all('span', class_='quickInfo__itemLabel')[0]
        price = int(price.string.replace('€', ''))
    except ValueError:
        logger.warning("Price doesn't for %s", title)
        return
    except IndexError:
        logger.warning("Info doesn't found for %s", title)
        return

    # Extract guests range from wedding site
    guests = []
    guests_string = soup.find_all('span',
                                  class_='quickInfo__itemValue')[0].string
    if 'Hasta' in guests_string:
        guests = [0, int(guests_string.replace('Hasta', ''))]
    elif 'a' in guests_string:
        guests = [int(x) for x in guests_string.split('a')]

    # Extract address
    address = soup.find_all('p', class_='storefrontMap__address')[0].string

    logger.info('Site = %s | Price = %s | Guests = %s | Addres = %s'\
        ,title, price, guests, address)



def extract_data_from_list_page(iters: int)->list:
    '''
    Extract URL of wedding site list page
    '''

    # Get all sites page by page
    sites = []
    for idx in range(1, iters):
        urlSite = ('%s%s', URL, idx)
        logger.info('Using URL = %s', urlSite)
        page = requests.get(urlSite, timeout=TIMEOUT)
        soup = BeautifulSoup(page.content, 'html.parser')

        # Detect list of sites in current page list
        sites_parent = soup.find_all('a',
                                    class_='vendorTile__title')
        sites.extend(sites_parent)

    # Parse data site by site
    logger.debug('Found %d wedding places', len(sites))
    for idx, site in enumerate(sites):
        logger.debug('%d/%d wedding website: %s', idx + 1,
                                                  len(sites),
                                                  site['href'])
        parse_wedding_site(site['href'])

def argument_parser() -> argparse.ArgumentParser:
    '''
    Argument parser function
    '''

    args = argparse.ArgumentParser()
    args.add_argument('--iters',
                      help='Number of iterations (default = 10)',
                      type=int,
                      default=10)

    return args.parse_args()

def main():
    '''
    Main function
    '''

    logger.info('Starting Wedding Scrapper script')
    args = argument_parser()
    extract_data_from_list_page(args.iters)

if __name__ == '__main__':
    main()
