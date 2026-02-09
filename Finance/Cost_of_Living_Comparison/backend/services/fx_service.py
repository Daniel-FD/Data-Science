import os
import logging
import requests
from typing import Dict, Optional
from cachetools import TTLCache

logger = logging.getLogger(__name__)


class FXService:
    """
    Service for fetching foreign exchange rates
    For MVP, using mock rates. Replace with actual API when needed.
    """
    
    def __init__(self):
        self.api_key = os.getenv("FX_API_KEY", "")
        self.base_url = "https://api.exchangerate-api.com/v4/latest/"
        # Cache with 1 hour TTL
        self.cache = TTLCache(maxsize=100, ttl=3600)
        self._initialize_mock_rates()
    
    def _initialize_mock_rates(self):
        """Initialize mock exchange rates (base: USD)"""
        self.mock_rates = {
            "USD": 1.0,
            "EUR": 0.92,
            "GBP": 0.79,
            "JPY": 149.50,
            "CAD": 1.36,
            "AUD": 1.54,
            "CHF": 0.88,
            "CNY": 7.24,
            "INR": 83.12,
            "MXN": 17.05,
            "BRL": 4.98,
            "SGD": 1.35,
            "HKD": 7.83,
            "KRW": 1305.50,
            "THB": 35.20,
            "AED": 3.67,
            "NZD": 1.65,
            "SEK": 10.68,
            "NOK": 10.52,
            "DKK": 6.86
        }
    
    def get_exchange_rate(self, from_currency: str, to_currency: str) -> float:
        """
        Get exchange rate from one currency to another
        
        Args:
            from_currency: Source currency code
            to_currency: Target currency code
        
        Returns:
            Exchange rate (to_currency per from_currency)
        """
        cache_key = f"{from_currency}_{to_currency}"
        
        # Check cache
        if cache_key in self.cache:
            logger.info(f"Cache hit for exchange rate: {cache_key}")
            return self.cache[cache_key]
        
        # For MVP, using mock data
        if from_currency == to_currency:
            return 1.0
        
        from_rate = self.mock_rates.get(from_currency, 1.0)
        to_rate = self.mock_rates.get(to_currency, 1.0)
        
        # Convert through USD
        rate = to_rate / from_rate
        
        self.cache[cache_key] = rate
        logger.info(f"Exchange rate {from_currency} -> {to_currency}: {rate}")
        
        return rate
    
    def convert_amount(self, amount: float, from_currency: str, to_currency: str) -> float:
        """
        Convert amount from one currency to another
        
        Args:
            amount: Amount in source currency
            from_currency: Source currency code
            to_currency: Target currency code
        
        Returns:
            Converted amount in target currency
        """
        rate = self.get_exchange_rate(from_currency, to_currency)
        return amount * rate
    
    def get_all_rates(self, base_currency: str = "USD") -> Dict[str, float]:
        """Get all exchange rates for a base currency"""
        return {
            currency: self.get_exchange_rate(base_currency, currency)
            for currency in self.mock_rates.keys()
        }
    
    def _fetch_from_api(self, base_currency: str) -> Optional[Dict]:
        """
        Fetch exchange rates from API (placeholder for actual implementation)
        
        To implement with a real API:
        1. Sign up for API (e.g., exchangerate-api.com, fixer.io)
        2. Make API request
        3. Parse and cache response
        """
        # TODO: Implement actual API call
        # Example:
        # try:
        #     url = f"{self.base_url}{base_currency}"
        #     response = requests.get(url, timeout=5)
        #     response.raise_for_status()
        #     return response.json()
        # except requests.RequestException as e:
        #     logger.error(f"Error fetching exchange rates: {e}")
        #     return None
        pass
