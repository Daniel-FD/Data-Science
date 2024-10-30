from bs4 import BeautifulSoup
import requests
import pandas as pd
from typing import Dict, List
import logging
import time
import re
import random
from fake_useragent import UserAgent
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from datetime import datetime
import os

class IdealistaScraper:
    def __init__(self):
        self.base_url = "https://www.idealista.com"
        self.session = self._create_session()
        self.ua = UserAgent()
        
    def _create_session(self):
        """Create a session with retry strategy"""
        session = requests.Session()
        
        # Configure retry strategy
        retries = Retry(
            total=5,
            backoff_factor=1,
            status_forcelist=[500, 502, 503, 504]
        )
        
        # Mount the adapter to the session
        adapter = HTTPAdapter(max_retries=retries)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        
        return session
    
    def _get_headers(self):
        """Generate random headers for each request"""
        return {
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'DNT': '1',
            'Referer': 'https://www.google.com/'
        }
    
    def _random_delay(self):
        """Add random delay between requests"""
        time.sleep(random.uniform(3, 7))

    def make_request(self, url: str) -> requests.Response:
        """Make a request with all anti-detection measures"""
        self._random_delay()
        headers = self._get_headers()
        
        try:
            response = self.session.get(
                url,
                headers=headers,
                timeout=10,
                allow_redirects=True
            )
            
            # Check if we're being redirected to CAPTCHA
            if 'captcha' in response.url or 'blocked' in response.url:
                raise Exception("Detected CAPTCHA/blocking page")
                
            return response
            
        except Exception as e:
            logging.error(f"Request failed for {url}: {str(e)}")
            raise

    def clean_price(self, price_text: str) -> int:
        """Clean price text to integer"""
        if not price_text:
            return None
        return int(''.join(filter(str.isdigit, price_text)))
    
    def clean_area(self, area_text: str) -> float:
        """Clean area text to float"""
        if not area_text:
            return None
        match = re.search(r'(\d+(?:\.\d+)?)', area_text)
        return float(match.group(1)) if match else None

    def extract_location(self, text: str) -> Dict:
        """Extract neighborhood and zone from location text"""
        parts = [p.strip() for p in text.split(',')]
        return {
            'neighborhood': parts[0] if len(parts) > 0 else None,
            'zone': parts[1] if len(parts) > 1 else None
        }

    def scrape_property_details(self, item_soup) -> Dict:
        """Scrape comprehensive details from a property item"""
        try:
            details = {
                'property_id': None,
                'url': None,
                'title': None,
                'price': None,
                'price_per_sqm': None,
                'area': None,
                'floor': None,
                'neighborhood': None,
                'zone': None,
                'description': None,
                'features': [],
                'has_elevator': False,
                'energy_rating': None,
                'condition': None,
                'last_updated': datetime.now().isoformat(),
                'property_type': 'local-comercial'
            }
            
            # Debug the item HTML
            logging.debug(f"Property item HTML: {item_soup.prettify()}")
            
            # Get URL and ID - updated selectors
            link = item_soup.find('a', {'class': ['item-link', 'property-link']})
            if not link:
                link = item_soup.find('a', href=True)
            
            if link:
                details['url'] = self.base_url + link.get('href', '')
                id_match = re.search(r'/(\d+)\.html', details['url'])
                if id_match:
                    details['property_id'] = id_match.group(1)
            
            # Get title - updated selectors
            title_elem = item_soup.find(['h3', 'h4', 'h5'], {'class': ['item-title', 'property-title']})
            if title_elem:
                details['title'] = title_elem.text.strip()
            
            # Get price - updated selectors
            price_elem = item_soup.find(['span', 'div'], {'class': ['item-price', 'property-price']})
            if price_elem:
                details['price'] = self.clean_price(price_elem.text.strip())
            
            # Get area - updated selectors
            area_elem = item_soup.find(['span', 'div'], {'class': ['item-detail', 'property-size']})
            if area_elem:
                details['area'] = self.clean_area(area_elem.text.strip())
                if details['area'] and details['price']:
                    details['price_per_sqm'] = round(details['price'] / details['area'], 2)
            
            # Get location - updated selectors
            location_elem = item_soup.find(['span', 'div'], {'class': ['item-location', 'property-location']})
            if location_elem:
                location_info = self.extract_location(location_elem.text.strip())
                details.update(location_info)
            
            # Log found details for debugging
            logging.debug(f"Scraped details: {details}")
            
            return details
            
        except Exception as e:
            logging.error(f"Error scraping property details: {str(e)}")
            return None

    def update_existing_properties(self, new_properties: List[Dict], csv_file: str) -> pd.DataFrame:
        """Update existing properties with new data"""
        # Read existing data if file exists
        if os.path.exists(csv_file):
            existing_df = pd.read_csv(csv_file)
            existing_df['last_updated'] = pd.to_datetime(existing_df['last_updated'])
        else:
            existing_df = pd.DataFrame()

        # Convert new properties to DataFrame
        new_df = pd.DataFrame(new_properties)
        new_df['last_updated'] = pd.to_datetime(new_df['last_updated'])

        if not existing_df.empty:
            # Update existing properties
            merged_df = pd.concat([existing_df, new_df])
            # Keep most recent version of each property
            merged_df = merged_df.sort_values('last_updated').drop_duplicates(
                subset=['property_id'], 
                keep='last'
            )
            return merged_df
        else:
            return new_df

    def scrape_search_results(self, search_url: str) -> List[Dict]:
        """Scrape all properties from search results pages"""
        properties = []
        page = 1
        max_retries = 3
        retry_delay = 60  # seconds
        
        while True:
            try:
                page_url = f"{search_url}pagina-{page}.htm" if page > 1 else search_url
                logging.info(f"Scraping page {page}: {page_url}")
                
                retries = 0
                while retries < max_retries:
                    try:
                        response = self.make_request(page_url)
                        break
                    except Exception as e:
                        retries += 1
                        if retries == max_retries:
                            logging.error(f"Max retries reached for page {page}")
                            return properties
                        logging.warning(f"Retry {retries}/{max_retries}. Waiting {retry_delay} seconds...")
                        time.sleep(retry_delay)
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Debug HTML structure
                logging.debug(f"Page HTML: {soup.prettify()}")
                
                # Find all property items - updated selector
                property_items = soup.find_all('article', {'class': 'item-multimedia-container'})
                
                if not property_items:
                    # Try alternative selectors
                    property_items = soup.find_all('div', {'class': 'item-info-container'})
                    if not property_items:
                        property_items = soup.find_all('article', {'class': 'property-item'})
                
                if not property_items:
                    logging.info(f"No properties found on page {page}. Stopping search.")
                    break
                
                logging.info(f"Found {len(property_items)} properties on page {page}")
                
                for item in property_items:
                    property_details = self.scrape_property_details(item)
                    if property_details:
                        properties.append(property_details)
                
                if not properties and page == 1:
                    logging.error("No properties could be scraped. HTML structure might have changed.")
                    logging.debug("Available classes in HTML:")
                    for tag in soup.find_all(class_=True):
                        logging.debug(f"Found class: {tag.get('class')}")
                    break
                
                page += 1
                
            except Exception as e:
                logging.error(f"Error scraping page {page}: {str(e)}")
                break
        
        return properties

    def generate_search_url(self, city: str, property_type: str, operation: str) -> str:
        """Generate search URL based on parameters"""
        # Clean and validate inputs
        city = city.lower().strip()
        property_type = property_type.lower().strip()
        operation = operation.lower().strip()
        
        # Generate URL
        url = f"{self.base_url}/{operation}-{property_type}/{city}/"
        return url