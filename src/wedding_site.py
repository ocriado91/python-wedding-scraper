#!/usr/bin/env python3
'''
Wrapper class to extract wedding place data
'''

import logging
import requests

from bs4 import BeautifulSoup
from geopy.geocoders import Nominatim

geolocator = Nominatim(user_agent='http')

TIMEOUT=5

logger = logging.getLogger()

def address2coordinates(address: str) -> dict:
    '''
    Convert address to coordinates
    '''

    logger.info('Converting %s address to coordinates', address)
    location = geolocator.geocode(address)
    if not location:
        logger.warning("It cannot converted %s address", address)
        return None
    logger.info('Converted address -> lat = %d; long = %d',
        location.latitude, location.longitude)
    return {"lat": location.latitude, "lon": location.longitude}

class Place:

    def __init__(self, website: str):
        '''
        Constructor Wedding Place class
        '''

        self.website = website
        self.soup = None

        # Init attributes
        self.title = ""
        self.price = 0
        self.guests = {}
        self.review_score = 0
        self.more_info = False
        self.location = {}
        self.multiple_events = None
        self.location_type = None

        # Extract data
        self.extract_info()
        self.extract_title()
        self.extract_price()
        self.extract_guests()
        self.extract_review_score()
        self.extract_more_info()
        self.extract_location()
        self.extract_multiple_events_per_day()
        self.extract_location_type()

    def extract_info(self):
        '''
        Extract website place data with BeautifulSoup
        '''

        page = requests.get(self.website, timeout=TIMEOUT)
        self.soup = BeautifulSoup(page.content, 'html.parser')

    def extract_title(self):
        '''
        Extract wedding place name
        '''

        self.title = self.soup.find_all('h1',
            class_='storefrontHeading__title')[0].string

    def extract_price(self):
        '''
        Extract price info
        '''

        try:
            price = self.soup.find_all('span',
                class_='quickInfo__itemLabel')[0]
            self.price = int(price.string.replace('€', ''))
        except ValueError:
            logger.warning("Price doesn't detected for %s", self.title)
            self.price = None
        except IndexError:
            logger.warning("Info doesn't found for %s", self.title)
            self.price = None

    def extract_guests(self):
        '''
        Extract range of guests
        '''

        logger.info('Extracting guests data from %s', self.title)
        try:
            guests_string = self.soup.find_all('span',
                class_='quickInfo__itemValue')[0].string
            if 'Hasta' in guests_string:
                min_guests = 0
                max_guests = int(guests_string.replace('Hasta', ''))
            elif 'a' in guests_string:
                min_guests = int(guests_string.split('a')[0])
                max_guests = int(guests_string.split('a')[1])
            elif 'Desde' in guests_string:
                min_guests = int(guests_string.split()[1])
                max_guests = 9999

            self.guests = {"gte": min_guests, "lte": max_guests}
        except IndexError:
            logger.warning('None guests info detected into %s', self.website)

    def extract_review_score(self):
        '''
        Extract review score
        '''

        try:
            self.review_score =  float(self.soup.find_all('div',
                class_='storefrontReviewsSummary__punctuationNumber')[0].string)
        except IndexError:
            logger.warning('None review score info detected into %s', self.website)

    def extract_more_info(self):
        '''
        Extract has_more_info flag
        '''

        more_info = self.soup.find_all('h2',
        class_='storefrontFaqs__title')
        has_more_info = False
        if more_info:
            has_more_info = True
        self.has_more_info =  has_more_info

    def extract_location(self):
        '''
        Extract location from address info
        '''

        address = self.soup.find_all('span',
            class_='storefrontHeading__locationName')[0].string
        self.location = address2coordinates(address)

    def extract_multiple_events_per_day(self):
        '''
        Extract if there are multiple events per day
        '''

        items = self.soup.find_all('h3',
            class_='storefrontFaqs__itemTitle')
        items_values = [x.string for x in items]
        try:
            index = items_values.index('¿Celebras más de un evento al día?')

            answer_item = self.soup.find_all('div',
                class_='storefrontFaqs__itemBlock')[index].string

            # Replace '\n' from string
            answer_value = answer_item.replace('\n', '').replace(' ', '')
            self.multiple_events = False
            if 'Sí' in answer_value:
                self.multiple_events = True
            elif 'No' in answer_value:
                self.multiple_events = False
        except (ValueError, IndexError):
            logger.warning('None detected multiple event per day info')

    def extract_location_type(self):
        '''
        Extract location type
        '''

        items = self.soup.find_all('p',
            class_='app-miniFaqs-read-more')
        for item in items:
            if 'En el campo' in item.string:
                self.location_type = 'campo'
            elif 'En ciudad' in item.string:
                self.location_type = 'ciudad'

    def build_data(self) -> dict:
        '''
        Save all data into dictionary
        '''

        data = {self.title: {'price': self.price,
                             'guests': self.guests,
                             'location': self.location,
                             'website': self.website,
                             'review_score': self.review_score,
                             'has_more_info': self.has_more_info,
                             'multiple_events': self.multiple_events,
                             'location_type': self.location_type}

               }

        logger.debug(data)
        return data





