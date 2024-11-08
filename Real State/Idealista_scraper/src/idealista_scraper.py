from bs4 import BeautifulSoup
import requests
import pandas as pd
from typing import Dict, List
import logging
import time
import random
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

class IdealistaScraper:
    def __init__(self):
        self.base_url = "https://www.idealista.com"
        self.session = requests.Session()  # Use session to maintain cookies
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0'
        }
        # Add some common cookies (you can get these from your browser)
        self.cookies = {
            'userUUID': 'some-uuid',  # Replace with actual values
            'SESSION': 'session-id',  # from your browser when
            'csrf': 'csrf-token'      # accessing idealista.com
        }
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=3,  # number of retries
            backoff_factor=1,  # wait 1, 2, 4 seconds between retries
            status_forcelist=[403, 429, 500, 502, 503, 504]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        self.user_agents = [
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:123.0) Gecko/20100101 Firefox/123.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0'
        ]
        
    def get_random_user_agent(self):
        return random.choice(self.user_agents)
        
    def generate_search_url(self, city: str, property_type: str, operation: str) -> str:
        """Generate search URL based on parameters"""
        # Convert spaces to hyphens and make lowercase
        city = city.lower().replace(" ", "-")
        property_type = property_type.lower().replace(" ", "-")
        operation = operation.lower()
        
        # Map property types to URL segments
        property_map = {
            "local-comercial": "locales",
            "locales": "locales",
            "casa": "casas",
            "apartamento": "apartamentos",
            "parking": "garajes",
            "trastero": "trasteros"
        }
        
        # Map operations
        operation_map = {
            "venta": "venta",
            "alquiler": "alquiler"
        }
        
        # Generate URL
        url = f"{self.base_url}/{operation_map[operation]}-{property_map[property_type]}/{city}/"
        return url
    
    def scrape_property_details(self, property_url: str) -> Dict:
        """Scrape details from a single property page"""
        try:
            response = requests.get(property_url, headers=self.headers)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            details = {
                'url': property_url,
                'price': None,
                'area': None,
                'description': None,
                'property_type': None
            }
            
            # Extract price
            price_elem = soup.find('span', {'class': 'price'})
            if price_elem:
                details['price'] = price_elem.text.strip()
                
            # Extract area
            area_elem = soup.find('div', {'class': 'area'})
            if area_elem:
                details['area'] = area_elem.text.strip()
                
            # Extract description
            desc_elem = soup.find('div', {'class': 'description'})
            if desc_elem:
                details['description'] = desc_elem.text.strip()
                
            return details
            
        except Exception as e:
            logging.error(f"Error scraping property {property_url}: {str(e)}")
            return None
    
    def scrape_search_results(self, search_url: str) -> List[Dict]:
        """Scrape all properties from search results pages"""
        properties = []
        page = 1
        
        while True:
            try:
                # Increase delay between requests (more realistic)
                time.sleep(random.uniform(5, 10))  # Increased delay
                
                page_url = f"{search_url}pagina-{page}.htm" if page > 1 else search_url
                
                # Add more browser-like headers
                self.headers.update({
                    'User-Agent': self.get_random_user_agent(),
                    'sec-ch-ua': '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
                    'sec-ch-ua-mobile': '?0',
                    'sec-ch-ua-platform': '"macOS"',
                    'Sec-Fetch-Dest': 'document',
                    'Sec-Fetch-Mode': 'navigate',
                    'Sec-Fetch-Site': 'none',
                    'Sec-Fetch-User': '?1'
                })
                
                response = self.session.get(
                    page_url, 
                    headers=self.headers,
                    cookies=self.cookies
                )
                
                if response.status_code == 403:
                    logging.error("Access forbidden (403). The website might be blocking our requests.")
                    logging.info("Try the following:\n" +
                               "1. Use a different IP address\n" +
                               "2. Wait for some time before trying again\n" +
                               "3. Consider using a proxy service")
                    break
                
                if response.status_code != 200:
                    logging.error(f"Unexpected status code: {response.status_code}")
                    break
                    
                soup = BeautifulSoup(response.content, 'html.parser')
                property_items = soup.find_all('div', {'class': 'item'})
                
                if not property_items:
                    break
                    
                for item in property_items:
                    property_url = self.base_url + item.find('a')['href']
                    property_details = self.scrape_property_details(property_url)
                    if property_details:
                        properties.append(property_details)
                
                page += 1
                
            except Exception as e:
                logging.error(f"Error scraping page {page}: {str(e)}")
                break
                
        return properties 