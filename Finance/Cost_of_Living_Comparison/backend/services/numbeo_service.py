import os
import logging
from typing import Dict, List, Optional
from cachetools import TTLCache
from datetime import datetime
from .data_loader import get_data_loader

logger = logging.getLogger(__name__)


class NumbeoService:
    """
    Service for fetching cost of living data
    Uses Kaggle dataset (primary) with fallback to mock data
    """
    
    def __init__(self):
        self.api_key = os.getenv("NUMBEO_API_KEY", "")
        # Cache with 24 hour TTL
        self.cache = TTLCache(maxsize=1000, ttl=86400)
        
        # Load real dataset
        self.data_loader = get_data_loader()
        
        # Initialize mock data as fallback
        self._initialize_mock_data()
        
        # Log data source
        if self.data_loader.cities_data:
            logger.info(f"Using Kaggle dataset with {len(self.data_loader.cities_data)} cities")
        else:
            logger.warning("Using mock data (20 cities). Please download the Kaggle dataset.")
    
    def _initialize_mock_data(self):
        """Initialize mock data for development"""
        self.mock_cities = {
            "New York, United States": {
                "overall_index": 100.0,
                "country": "United States",
                "latitude": 40.7128,
                "longitude": -74.0060,
                "categories": {
                    "rent": 100.0,
                    "food": 100.0,
                    "transport": 100.0,
                    "utilities": 100.0,
                    "entertainment": 100.0
                }
            },
            "London, United Kingdom": {
                "overall_index": 87.3,
                "country": "United Kingdom",
                "latitude": 51.5074,
                "longitude": -0.1278,
                "categories": {
                    "rent": 85.2,
                    "food": 88.5,
                    "transport": 90.1,
                    "utilities": 85.0,
                    "entertainment": 89.3
                }
            },
            "Paris, France": {
                "overall_index": 89.5,
                "country": "France",
                "latitude": 48.8566,
                "longitude": 2.3522,
                "categories": {
                    "rent": 82.4,
                    "food": 91.2,
                    "transport": 88.7,
                    "utilities": 87.5,
                    "entertainment": 92.1
                }
            },
            "Tokyo, Japan": {
                "overall_index": 91.2,
                "country": "Japan",
                "latitude": 35.6762,
                "longitude": 139.6503,
                "categories": {
                    "rent": 75.3,
                    "food": 95.8,
                    "transport": 92.4,
                    "utilities": 88.9,
                    "entertainment": 93.7
                }
            },
            "Singapore, Singapore": {
                "overall_index": 94.8,
                "country": "Singapore",
                "latitude": 1.3521,
                "longitude": 103.8198,
                "categories": {
                    "rent": 98.5,
                    "food": 92.3,
                    "transport": 91.6,
                    "utilities": 93.2,
                    "entertainment": 94.9
                }
            },
            "Berlin, Germany": {
                "overall_index": 71.4,
                "country": "Germany",
                "latitude": 52.5200,
                "longitude": 13.4050,
                "categories": {
                    "rent": 62.8,
                    "food": 73.5,
                    "transport": 72.1,
                    "utilities": 68.9,
                    "entertainment": 75.3
                }
            },
            "Barcelona, Spain": {
                "overall_index": 68.9,
                "country": "Spain",
                "latitude": 41.3851,
                "longitude": 2.1734,
                "categories": {
                    "rent": 58.3,
                    "food": 71.2,
                    "transport": 69.8,
                    "utilities": 67.4,
                    "entertainment": 72.5
                }
            },
            "Toronto, Canada": {
                "overall_index": 76.3,
                "country": "Canada",
                "latitude": 43.6532,
                "longitude": -79.3832,
                "categories": {
                    "rent": 72.5,
                    "food": 77.8,
                    "transport": 75.4,
                    "utilities": 74.2,
                    "entertainment": 78.9
                }
            },
            "Sydney, Australia": {
                "overall_index": 88.7,
                "country": "Australia",
                "latitude": -33.8688,
                "longitude": 151.2093,
                "categories": {
                    "rent": 87.3,
                    "food": 89.5,
                    "transport": 88.2,
                    "utilities": 86.7,
                    "entertainment": 90.4
                }
            },
            "Dubai, United Arab Emirates": {
                "overall_index": 78.9,
                "country": "United Arab Emirates",
                "latitude": 25.2048,
                "longitude": 55.2708,
                "categories": {
                    "rent": 73.4,
                    "food": 80.2,
                    "transport": 76.8,
                    "utilities": 77.5,
                    "entertainment": 82.3
                }
            },
            "Amsterdam, Netherlands": {
                "overall_index": 84.2,
                "country": "Netherlands",
                "latitude": 52.3676,
                "longitude": 4.9041,
                "categories": {
                    "rent": 79.5,
                    "food": 85.8,
                    "transport": 83.4,
                    "utilities": 82.1,
                    "entertainment": 86.7
                }
            },
            "Hong Kong, Hong Kong": {
                "overall_index": 98.3,
                "country": "Hong Kong",
                "latitude": 22.3193,
                "longitude": 114.1694,
                "categories": {
                    "rent": 115.2,
                    "food": 92.7,
                    "transport": 88.9,
                    "utilities": 91.4,
                    "entertainment": 93.8
                }
            },
            "San Francisco, United States": {
                "overall_index": 102.5,
                "country": "United States",
                "latitude": 37.7749,
                "longitude": -122.4194,
                "categories": {
                    "rent": 125.3,
                    "food": 98.2,
                    "transport": 95.7,
                    "utilities": 92.8,
                    "entertainment": 99.4
                }
            },
            "Lisbon, Portugal": {
                "overall_index": 60.3,
                "country": "Portugal",
                "latitude": 38.7223,
                "longitude": -9.1393,
                "categories": {
                    "rent": 48.5,
                    "food": 63.7,
                    "transport": 61.2,
                    "utilities": 58.9,
                    "entertainment": 65.4
                }
            },
            "Mexico City, Mexico": {
                "overall_index": 45.8,
                "country": "Mexico",
                "latitude": 19.4326,
                "longitude": -99.1332,
                "categories": {
                    "rent": 35.2,
                    "food": 48.9,
                    "transport": 46.7,
                    "utilities": 44.3,
                    "entertainment": 50.1
                }
            },
            "Buenos Aires, Argentina": {
                "overall_index": 42.1,
                "country": "Argentina",
                "latitude": -34.6037,
                "longitude": -58.3816,
                "categories": {
                    "rent": 32.8,
                    "food": 45.3,
                    "transport": 43.6,
                    "utilities": 40.9,
                    "entertainment": 46.7
                }
            },
            "Mumbai, India": {
                "overall_index": 35.7,
                "country": "India",
                "latitude": 19.0760,
                "longitude": 72.8777,
                "categories": {
                    "rent": 28.4,
                    "food": 38.2,
                    "transport": 36.5,
                    "utilities": 34.1,
                    "entertainment": 39.8
                }
            },
            "Bangkok, Thailand": {
                "overall_index": 48.3,
                "country": "Thailand",
                "latitude": 13.7563,
                "longitude": 100.5018,
                "categories": {
                    "rent": 38.7,
                    "food": 51.2,
                    "transport": 47.9,
                    "utilities": 46.5,
                    "entertainment": 52.8
                }
            },
            "Istanbul, Turkey": {
                "overall_index": 38.9,
                "country": "Turkey",
                "latitude": 41.0082,
                "longitude": 28.9784,
                "categories": {
                    "rent": 29.5,
                    "food": 41.7,
                    "transport": 39.2,
                    "utilities": 37.8,
                    "entertainment": 43.4
                }
            },
            "Seoul, South Korea": {
                "overall_index": 82.4,
                "country": "South Korea",
                "latitude": 37.5665,
                "longitude": 126.9780,
                "categories": {
                    "rent": 68.9,
                    "food": 85.7,
                    "transport": 81.3,
                    "utilities": 79.8,
                    "entertainment": 87.2
                }
            }
        }
    
    def get_available_cities(self) -> List[str]:
        """Get list of available cities"""
        # Try real dataset first
        if self.data_loader.cities_data:
            cities = self.data_loader.get_cities()
            # Sort cities alphabetically for better UX
            return sorted(cities)
        
        # Fallback to mock data
        return sorted(list(self.mock_cities.keys()))
    
    def get_city_index(self, city: str) -> Optional[Dict]:
        """Get basic index for a city"""
        cache_key = f"city_index_{city}"
        
        # Check cache
        if cache_key in self.cache:
            logger.info(f"Cache hit for {city}")
            return self.cache[cache_key]
        
        # Try real dataset first
        if self.data_loader.cities_data:
            data = self.data_loader.get_city_data(city)
            if data:
                result = {
                    "overall_index": data["overall_index"],
                    "country": data["country"],
                    "latitude": data.get("latitude"),
                    "longitude": data.get("longitude")
                }
                self.cache[cache_key] = result
                return result
        
        # Fallback to mock data
        data = self.mock_cities.get(city)
        if data:
            result = {
                "overall_index": data["overall_index"],
                "country": data["country"],
                "latitude": data.get("latitude"),
                "longitude": data.get("longitude")
            }
            self.cache[cache_key] = result
            return result
        
        logger.warning(f"City not found: {city}")
        return None
    
    def get_city_detailed_data(self, city: str) -> Optional[Dict]:
        """Get detailed data including category indices for a city"""
        cache_key = f"city_detailed_{city}"
        
        # Check cache
        if cache_key in self.cache:
            logger.info(f"Cache hit for detailed data: {city}")
            return self.cache[cache_key]
        
        # Try real dataset first
        if self.data_loader.cities_data:
            data = self.data_loader.get_city_data(city)
            if data:
                self.cache[cache_key] = data
                return data
        
        # Fallback to mock data
        data = self.mock_cities.get(city)
        if data:
            self.cache[cache_key] = data
            return data
        
        logger.warning(f"City not found: {city}")
        return None
    
    def _fetch_from_api(self, city: str) -> Optional[Dict]:
        """
        Fetch data from Numbeo API (placeholder for actual implementation)
        
        To implement:
        1. Make API request to Numbeo
        2. Parse response
        3. Transform to expected format
        """
        # TODO: Implement actual API call
        # Example:
        # url = f"https://api.numbeo.com/city_price?api_key={self.api_key}&query={city}"
        # response = requests.get(url)
        # return response.json()
        pass
