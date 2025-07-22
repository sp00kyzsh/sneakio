"""
The Sneaker Database API integration module
Provides functions to lookup sneaker data by SKU and other parameters
"""
import requests
import logging
import os
import html
from typing import Dict, List, Optional, Union

logger = logging.getLogger(__name__)

class SneakerDatabaseAPI:
    """
    Client for The Sneaker Database API via RapidAPI
    """
    
    BASE_URL = "https://the-sneaker-database.p.rapidapi.com"
    
    def __init__(self):
        self.api_key = os.environ.get("SNEAKER_DATABASE_API_KEY")
        self.session = requests.Session()
        
        if self.api_key:
            self.session.headers.update({
                'X-RapidAPI-Key': self.api_key,
                'X-RapidAPI-Host': 'the-sneaker-database.p.rapidapi.com',
                'Accept': 'application/json'
            })
        else:
            logger.warning("No SNEAKER_DATABASE_API_KEY found in environment")
    
    def search_sneakers(self, query: str = None, sku: str = None, brand: str = None, 
                       limit: int = 10, **kwargs) -> Optional[List[Dict]]:
        """
        Search for sneakers using various parameters
        
        Args:
            query: Search query string
            sku: SKU/Style code to search for
            brand: Brand name to filter by
            limit: Maximum number of results (default: 10)
            **kwargs: Additional query parameters
            
        Returns:
            List of sneaker data dictionaries or None if error
        """
        try:
            # Check if API key is available
            if not self.api_key:
                logger.error("No API key available for Sneaker Database")
                return None
            
            url = f"{self.BASE_URL}/sneakers"
            # Ensure limit is within API requirements (10-100)
            limit = max(10, min(100, limit))
            params = {"limit": limit}
            
            # The RapidAPI version uses different parameter names
            if query:
                params["name"] = query
            if sku:
                params["sku"] = sku
            if brand:
                params["brand"] = brand
            
            # Add any additional parameters
            params.update(kwargs)
            
            logger.info(f"Searching sneakers with params: {params}")
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Handle the RapidAPI response structure
            if isinstance(data, dict) and 'results' in data:
                return data['results']
            elif isinstance(data, list):
                return data
            else:
                logger.warning(f"Unexpected response format: {type(data)}")
                return []
                
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            return None
        except Exception as e:
            logger.error(f"Error searching sneakers: {e}")
            return None
    
    def get_sneaker_by_id(self, sneaker_id: str) -> Optional[Dict]:
        """
        Get detailed sneaker information by ID
        
        Args:
            sneaker_id: The sneaker ID from the database
            
        Returns:
            Sneaker data dictionary or None if error
        """
        try:
            url = f"{self.BASE_URL}/sneakers/{sneaker_id}"
            
            logger.info(f"Getting sneaker by ID: {sneaker_id}")
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            return None
        except Exception as e:
            logger.error(f"Error getting sneaker by ID: {e}")
            return None
    
    def get_brands(self) -> Optional[List[str]]:
        """
        Get list of available brands
        
        Returns:
            List of brand names or None if error
        """
        try:
            url = f"{self.BASE_URL}/brands"
            
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Extract brand names from response
            if isinstance(data, list):
                return [brand.get('name', brand) if isinstance(brand, dict) else str(brand) for brand in data]
            elif isinstance(data, dict) and 'brands' in data:
                return [brand.get('name', brand) if isinstance(brand, dict) else str(brand) for brand in data['brands']]
            
            return []
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            return None
        except Exception as e:
            logger.error(f"Error getting brands: {e}")
            return None
    
    def lookup_by_sku(self, sku: str) -> Optional[Dict]:
        """
        Lookup sneaker data specifically by SKU/Style code
        
        Args:
            sku: The SKU/Style code to search for
            
        Returns:
            Best matching sneaker data or None if not found
        """
        if not sku or not sku.strip():
            return None
            
        sku = sku.strip()
        logger.info(f"Looking up sneaker by SKU: {sku}")
        
        # First try exact SKU match
        results = self.search_sneakers(sku=sku, limit=5)
        
        if results and len(results) > 0:
            return self._format_sneaker_data(results[0])
        
        # If no exact match, try as part of name/query
        results = self.search_sneakers(query=sku, limit=5)
        
        if results and len(results) > 0:
            # Look for SKU in the results
            for result in results:
                if self._sku_matches(sku, result):
                    return self._format_sneaker_data(result)
            
            # If no SKU match found, return the first result
            return self._format_sneaker_data(results[0])
        
        return None
    
    def _sku_matches(self, search_sku: str, sneaker_data: Dict) -> bool:
        """
        Check if the SKU matches any SKU-related fields in sneaker data
        """
        search_sku = search_sku.upper().replace('-', '').replace(' ', '')
        
        # Check various possible SKU field names
        sku_fields = ['sku', 'styleId', 'style_id', 'productId', 'product_id', 'code']
        
        for field in sku_fields:
            if field in sneaker_data and sneaker_data[field]:
                data_sku = str(sneaker_data[field]).upper().replace('-', '').replace(' ', '')
                if search_sku in data_sku or data_sku in search_sku:
                    return True
        
        return False
    
    def _format_sneaker_data(self, raw_data: Dict) -> Dict:
        """
        Format raw API response into standardized sneaker data
        
        Args:
            raw_data: Raw response from API
            
        Returns:
            Formatted sneaker data dictionary
        """
        try:
            # Map the RapidAPI response fields to our standard format
            formatted = {
                'id': raw_data.get('id'),
                'sku': raw_data.get('sku'),
                'brand': raw_data.get('brand'),
                'model': raw_data.get('name'),
                'colorway': raw_data.get('colorway'),
                'retail_price': self._parse_price(raw_data.get('retailPrice')),
                'release_date': self._parse_date(raw_data.get('releaseDate')),
                'image_url': self._get_image_url(raw_data),
                'category': self._parse_category(raw_data.get('gender')),
                'description': html.unescape(raw_data.get('story', '')) if raw_data.get('story') else None,
                'links': raw_data.get('links', {}),
                'estimated_market_value': self._parse_price(raw_data.get('estimatedMarketValue')),
                'silhouette': raw_data.get('silhouette'),
                'release_year': raw_data.get('releaseYear')
            }
            
            # Remove None values
            formatted = {k: v for k, v in formatted.items() if v is not None}
            
            return formatted
            
        except Exception as e:
            logger.error(f"Error formatting sneaker data: {e}")
            return raw_data
    
    def _get_image_url(self, data: Dict) -> Optional[str]:
        """Extract image URL from RapidAPI response format"""
        # The RapidAPI response has a specific image object structure
        image_obj = data.get('image', {})
        
        if isinstance(image_obj, dict):
            # Try to get the best quality image
            # Priority: original > small > thumbnail
            for quality in ['original', 'small', 'thumbnail']:
                if quality in image_obj and image_obj[quality]:
                    url = image_obj[quality]
                    if isinstance(url, str) and url.startswith(('http://', 'https://')):
                        return url
        
        # Fallback to other possible image fields
        image_fields = ['imageUrl', 'image_url', 'thumbnail', 'mainPictureUrl', 'pictureUrl']
        for field in image_fields:
            if field in data and data[field]:
                image_url = data[field]
                if isinstance(image_url, str) and image_url.startswith(('http://', 'https://')):
                    return image_url
        
        return None
    
    def _parse_price(self, price) -> Optional[float]:
        """Parse price from various formats"""
        if price is None:
            return None
        
        try:
            if isinstance(price, (int, float)):
                return float(price)
            elif isinstance(price, str):
                # Remove currency symbols and convert
                clean_price = price.replace('$', '').replace(',', '').strip()
                return float(clean_price) if clean_price else None
        except (ValueError, TypeError):
            pass
        
        return None
    
    def _parse_date(self, date_str) -> Optional[str]:
        """Parse date from various formats"""
        if not date_str:
            return None
        
        try:
            if isinstance(date_str, str):
                # Handle ISO date format (YYYY-MM-DDTHH:MM:SS)
                if 'T' in date_str:
                    return date_str.split('T')[0]
                # Handle space-separated date format (YYYY-MM-DD HH:MM:SS.mmm)
                elif ' ' in date_str:
                    return date_str.split(' ')[0]
                # Return as-is if already in YYYY-MM-DD format
                elif len(date_str) == 10 and date_str.count('-') == 2:
                    return date_str
                # For other formats, try to extract just the date part
                else:
                    # Try to match YYYY-MM-DD pattern at the beginning
                    import re
                    match = re.match(r'(\d{4}-\d{2}-\d{2})', date_str)
                    if match:
                        return match.group(1)
                    return date_str
        except Exception:
            pass
        
        return str(date_str) if date_str else None
    
    def _parse_category(self, gender) -> str:
        """Parse category from gender field"""
        if not gender:
            return "Men's"
        
        gender = str(gender).lower()
        if 'women' in gender or 'female' in gender:
            return "Women's"
        elif 'child' in gender or 'kid' in gender or 'youth' in gender:
            return "Children's"
        else:
            return "Men's"

# Create a global instance
sneaker_db_api = SneakerDatabaseAPI()