"""
Data loader for Cost of Living dataset
Loads and processes the Kaggle Global Cost of Living dataset
"""

import pandas as pd
import os
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path

logger = logging.getLogger(__name__)


class DataLoader:
    """Load and process cost of living data from CSV files."""
    
    def __init__(self, csv_path: str = "data/kaggle/cost-of-living_v2.csv"):
        self.csv_path = Path(csv_path)
        self.data = None
        self.cities = []
        
    def load_data(self) -> bool:
        """Load data from CSV file."""
        try:
            if not self.csv_path.exists():
                logger.error(f"CSV file not found: {self.csv_path}")
                return False
            
            # Read CSV file
            df = pd.read_csv(self.csv_path)
            
            # Process and validate data
            self.data = self._process_dataframe(df)
            self.cities = sorted(self.data.keys())
            
            logger.info(f"Loaded {len(self.cities)} cities from v2 dataset")
            return True
            
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            return False
    
    def _process_dataframe(self, df: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
        """Process dataframe into city dictionary.
        
        The v2 dataset uses x1-x55 columns for various cost metrics.
        We'll use x2 (Cost of Living Index) and x29 (Rent Index) as primary indices.
        """
        data = {}
        
        # Use geopy for geocoding (fallback coordinates)
        city_coords = {}
        
        for _, row in df.iterrows():
            try:
                city = row.get('city', '')
                country = row.get('country', '')
                
                if not city or not country:
                    continue
                
                city_key = f"{city}, {country}"
                
                # Calculate cost of living index from x2 (meal price inexpensive restaurant)
                # and other relevant metrics - normalize to 100 = average
                cost_index = float(row.get('x2', 50)) * 2  # x2 is meal price, scale up
                rent_index = float(row.get('x29', 50)) * 2  # x29 is rent for 1br city center
                groceries_index = float(row.get('x1', 5)) * 10  # x1 is milk price
                restaurant_index = float(row.get('x2', 50)) * 2  # x2 is meal price
                
                # Get geocoding data (simple lookup for major cities)
                lat, lon = self._get_coordinates(city, country)
                
                data[city_key] = {
                    'city': city,
                    'country': country,
                    'cost_of_living_index': cost_index,
                    'rent_index': rent_index,
                    'groceries_index': groceries_index,
                    'restaurant_index': restaurant_index,
                    'local_purchasing_power': 100.0,  # Default value
                    'latitude': lat,
                    'longitude': lon
                }
                
            except Exception as e:
                logger.warning(f"Error processing row for {city}: {e}")
                continue
        
        return data
    
    def _get_coordinates(self, city: str, country: str) -> tuple:
        """Get approximate coordinates for a city (simple mapping for common cities)."""
        # Major cities coordinates lookup
        coords_map = {
            "Seoul": (37.5665, 126.9780),
            "Shanghai": (31.2304, 121.4737),
            "Mumbai": (19.0760, 72.8777),
            "Delhi": (28.6139, 77.2090),
            "Tokyo": (35.6762, 139.6503),
            "New York": (40.7128, -74.0060),
            "London": (51.5074, -0.1278),
            "Paris": (48.8566, 2.3522),
            "Singapore": (1.3521, 103.8198),
            "Dubai": (25.2048, 55.2708),
            "Sydney": (-33.8688, 151.2093),
            "Toronto": (43.6532, -79.3832),
            "Berlin": (52.5200, 13.4050),
            "Madrid": (40.4168, -3.7038),
            "Rome": (41.9028, 12.4964),
            "Amsterdam": (52.3676, 4.9041),
            "Barcelona": (41.3851, 2.1734),
            "Los Angeles": (34.0522, -118.2437),
            "Chicago": (41.8781, -87.6298),
            "San Francisco": (37.7749, -122.4194),
            "Moscow": (55.7558, 37.6173),
            "Istanbul": (41.0082, 28.9784),
            "Bangkok": (13.7563, 100.5018),
            "Hong Kong": (22.3193, 114.1694),
            "Kuala Lumpur": (3.1390, 101.6869),
            "Melbourne": (-37.8136, 144.9631),
            "Vancouver": (49.2827, -123.1207),
            "Zurich": (47.3769, 8.5417),
            "Geneva": (46.2044, 6.1432),
            "Vienna": (48.2082, 16.3738),
            "Stockholm": (59.3293, 18.0686),
            "Copenhagen": (55.6761, 12.5683),
            "Oslo": (59.9139, 10.7522),
            "Helsinki": (60.1699, 24.9384),
            "Brussels": (50.8503, 4.3517),
            "Lisbon": (38.7223, -9.1393),
            "Athens": (37.9838, 23.7275),
            "Prague": (50.0755, 14.4378),
            "Warsaw": (52.2297, 21.0122),
            "Budapest": (47.4979, 19.0402),
            "Bucharest": (44.4268, 26.1025),
            "Dublin": (53.3498, -6.2603),
            "Edinburgh": (55.9533, -3.1883),
            "Manchester": (53.4808, -2.2426),
            "Glasgow": (55.8642, -4.2518),
            "Birmingham": (52.4862, -1.8904),
            "Milan": (45.4642, 9.1900),
            "Naples": (40.8518, 14.2681),
            "Munich": (48.1351, 11.5820),
            "Hamburg": (53.5511, 9.9937),
            "Frankfurt": (50.1109, 8.6821),
            "Cologne": (50.9375, 6.9603),
        }
        
        # Try to find coordinates
        if city in coords_map:
            return coords_map[city]
        
        # Default fallback coordinates (center of map)
        return (0.0, 0.0)


# Global instance
_data_loader = None


def get_data_loader() -> DataLoader:
    """Get or create the global data loader instance"""
    global _data_loader
    if _data_loader is None:
        _data_loader = DataLoader()
    return _data_loader
