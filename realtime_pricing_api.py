"""
Real-time Sneaker Pricing API integration module
Provides functions to fetch real-time pricing data from multiple sources
"""
import requests
import logging
import os
from typing import Dict, List, Optional, Union
import json
from datetime import datetime

logger = logging.getLogger(__name__)

class RealtimePricingAPI:
    """
    Client for real-time sneaker pricing APIs
    Integrates with multiple pricing sources for comprehensive market data
    """
    
    def __init__(self):
        self.rapidapi_key = os.environ.get("RAPIDAPI_KEY")
        self.session = requests.Session()
        
        if self.rapidapi_key:
            self.session.headers.update({
                'X-RapidAPI-Key': self.rapidapi_key,
                'Accept': 'application/json'
            })
        else:
            logger.warning("No RAPIDAPI_KEY found in environment")
    
    def get_sneaker_prices(self, brand: str, model: str, colorway: str = None, 
                          sku: str = None, size: str = None) -> Optional[Dict]:
        """
        Get real-time pricing data for a sneaker across multiple platforms
        
        Args:
            brand: Sneaker brand (e.g., "Nike", "Adidas")
            model: Sneaker model (e.g., "Air Jordan 1", "Yeezy Boost 350")
            colorway: Sneaker colorway (optional)
            sku: SKU/Style code (optional)
            size: Shoe size (optional)
            
        Returns:
            Dictionary containing pricing data from various sources
        """
        pricing_data = {
            'brand': brand,
            'model': model,
            'colorway': colorway,
            'sku': sku,
            'size': size,
            'last_updated': datetime.utcnow().isoformat(),
            'sources': {},
            'summary': {}
        }
        
        # Try multiple API sources
        try:
            # 1. Try Sneaker Database - StockX API
            stockx_data = self._get_stockx_pricing(brand, model, colorway, sku, size)
            if stockx_data:
                pricing_data['sources']['stockx'] = stockx_data
            
            # 2. Try alternative pricing API
            alt_data = self._get_alternative_pricing(brand, model, colorway, sku, size)
            if alt_data:
                pricing_data['sources']['alternative'] = alt_data
            
            # 3. Generate summary from available data
            pricing_data['summary'] = self._generate_pricing_summary(pricing_data['sources'])
            
            # If no sources found, provide demo data to demonstrate functionality
            if not pricing_data['sources']:
                logger.info("No API sources available, providing demo data")
                return self._create_demo_response(brand, model, colorway, sku, size)
            
            return pricing_data
            
        except Exception as e:
            logger.error(f"Error fetching pricing data: {e}")
            return None
    
    def _get_stockx_pricing(self, brand: str, model: str, colorway: str = None, 
                           sku: str = None, size: str = None) -> Optional[Dict]:
        """
        Get pricing data from StockX Pricing Data and Market Analytics API
        """
        try:
            # Use the new StockX API
            self.session.headers.update({
                'X-RapidAPI-Host': 'stockx-pricing-data-and-market-analytics.p.rapidapi.com'
            })
            
            # Build search query - this API supports multiple search methods
            search_query = f"{brand} {model}"
            if colorway:
                search_query += f" {colorway}"
            
            # Try the search endpoint first
            url = "https://stockx-pricing-data-and-market-analytics.p.rapidapi.com/search"
            params = {
                'query': search_query,
                'limit': 10
            }
            
            logger.info(f"Searching StockX pricing for: {search_query}")
            response = self.session.get(url, params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                if data and isinstance(data, dict):
                    # Check if we have results
                    results = data.get('results', data.get('data', []))
                    if isinstance(results, list) and len(results) > 0:
                        # Get the first match
                        first_result = results[0]
                        
                        # Try to get detailed pricing for this product
                        product_id = first_result.get('id', first_result.get('uuid', first_result.get('productId')))
                        if product_id:
                            pricing_data = self._get_stockx_product_details(product_id, size)
                            if pricing_data:
                                return pricing_data
                        
                        # Fallback to basic result formatting
                        return self._format_stockx_search_result(first_result, size)
                    elif isinstance(data, dict) and data.get('name'):
                        # Single product result
                        return self._format_stockx_search_result(data, size)
            else:
                logger.warning(f"StockX search API returned status {response.status_code}")
                
            # If search doesn't work, try direct product lookup if we have SKU
            if sku:
                return self._get_stockx_by_sku(sku, size)
                
        except Exception as e:
            logger.error(f"Error fetching StockX pricing: {e}")
        
        return None
    
    def _get_stockx_product_details(self, product_id: str, size: str = None) -> Optional[Dict]:
        """
        Get detailed pricing for a specific StockX product
        """
        try:
            url = f"https://stockx-pricing-data-and-market-analytics.p.rapidapi.com/product/{product_id}"
            
            params = {}
            if size:
                params['size'] = size
            
            logger.info(f"Getting StockX product details for: {product_id}")
            response = self.session.get(url, params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                if data:
                    return self._format_stockx_product_data(data, size)
            else:
                logger.warning(f"StockX product API returned status {response.status_code}")
                
        except Exception as e:
            logger.error(f"Error fetching StockX product details: {e}")
        
        return None
    
    def _get_stockx_by_sku(self, sku: str, size: str = None) -> Optional[Dict]:
        """
        Get StockX pricing by SKU
        """
        try:
            url = "https://stockx-pricing-data-and-market-analytics.p.rapidapi.com/product/sku"
            params = {
                'sku': sku
            }
            
            if size:
                params['size'] = size
            
            logger.info(f"Getting StockX pricing by SKU: {sku}")
            response = self.session.get(url, params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                if data:
                    return self._format_stockx_product_data(data, size)
            else:
                logger.warning(f"StockX SKU API returned status {response.status_code}")
                
        except Exception as e:
            logger.error(f"Error fetching StockX pricing by SKU: {e}")
        
        return None
    
    def _get_alternative_pricing(self, brand: str, model: str, colorway: str = None, 
                                sku: str = None, size: str = None) -> Optional[Dict]:
        """
        Get pricing data from alternative API sources
        """
        try:
            # Try the Database Sneakers API
            self.session.headers.update({
                'X-RapidAPI-Host': 'database-sneakers.p.rapidapi.com'
            })
            
            url = "https://database-sneakers.p.rapidapi.com/sneakers"
            
            # Build search query
            query_parts = [brand, model]
            if colorway:
                query_parts.append(colorway)
            
            search_query = " ".join(query_parts)
            
            params = {
                'query': search_query,
                'limit': '10'
            }
            
            logger.info(f"Searching alternative pricing for: {search_query}")
            response = self.session.get(url, params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                if data and len(data) > 0:
                    return self._format_alternative_data(data[0], size)
            else:
                logger.warning(f"Alternative API returned status {response.status_code}")
                
        except Exception as e:
            logger.error(f"Error fetching alternative pricing: {e}")
        
        return None
    
    def _format_realtime_data(self, raw_data: Dict, size: str = None) -> Dict:
        """
        Format real-time pricing API response data
        """
        try:
            formatted = {
                'platform': 'Real-time API',
                'product_id': raw_data.get('id'),
                'name': raw_data.get('name', raw_data.get('title')),
                'brand': raw_data.get('brand'),
                'retail_price': self._parse_price(raw_data.get('retail_price', raw_data.get('retailPrice'))),
                'market_price': self._parse_price(raw_data.get('current_price', raw_data.get('lowestAsk', raw_data.get('price')))),
                'image_url': self._extract_image_url(raw_data),
                'release_date': raw_data.get('release_date', raw_data.get('releaseDate')),
                'sku': raw_data.get('sku', raw_data.get('styleId')),
                'colorway': raw_data.get('colorway'),
                'sizes_available': [],
                'price_by_size': {}
            }
            
            # Extract size-specific pricing if available
            if 'sizes' in raw_data and isinstance(raw_data['sizes'], (list, dict)):
                size_data = raw_data['sizes']
                if isinstance(size_data, list):
                    for size_info in size_data:
                        if isinstance(size_info, dict):
                            size_val = size_info.get('size', size_info.get('US', ''))
                            price_val = size_info.get('price', size_info.get('lowestAsk', 0))
                            
                            if size_val and price_val:
                                formatted['sizes_available'].append(str(size_val))
                                formatted['price_by_size'][str(size_val)] = self._parse_price(price_val)
                elif isinstance(size_data, dict):
                    for size_val, price_val in size_data.items():
                        if price_val:
                            formatted['sizes_available'].append(str(size_val))
                            formatted['price_by_size'][str(size_val)] = self._parse_price(price_val)
            
            # If specific size requested, get that price
            if size and size in formatted['price_by_size']:
                formatted['size_specific_price'] = formatted['price_by_size'][size]
            
            return formatted
            
        except Exception as e:
            logger.error(f"Error formatting real-time data: {e}")
            return {'platform': 'Real-time API', 'error': str(e)}
    
    def _format_stockx_search_result(self, raw_data: Dict, size: str = None) -> Dict:
        """
        Format StockX search result data
        """
        try:
            formatted = {
                'platform': 'StockX',
                'product_id': raw_data.get('id', raw_data.get('uuid', raw_data.get('productId'))),
                'name': raw_data.get('name', raw_data.get('title')),
                'brand': raw_data.get('brand'),
                'retail_price': self._parse_price(raw_data.get('retailPrice', raw_data.get('retail_price'))),
                'market_price': self._parse_price(raw_data.get('lowestAsk', raw_data.get('current_price', raw_data.get('lastSale')))),
                'image_url': self._extract_image_url(raw_data),
                'sku': raw_data.get('styleId', raw_data.get('sku')),
                'colorway': raw_data.get('colorway'),
                'sizes_available': [],
                'price_by_size': {}
            }
            
            # Extract size-specific pricing if available
            if 'market' in raw_data and isinstance(raw_data['market'], dict):
                market_data = raw_data['market']
                if 'lowestAskBySize' in market_data:
                    for size_data in market_data['lowestAskBySize']:
                        if isinstance(size_data, dict):
                            size_val = size_data.get('size', '')
                            price_val = size_data.get('lowestAsk', 0)
                            
                            if size_val and price_val:
                                formatted['sizes_available'].append(str(size_val))
                                formatted['price_by_size'][str(size_val)] = self._parse_price(price_val)
            
            # If specific size requested, get that price
            if size and size in formatted['price_by_size']:
                formatted['size_specific_price'] = formatted['price_by_size'][size]
                formatted['market_price'] = formatted['price_by_size'][size]
            
            return formatted
            
        except Exception as e:
            logger.error(f"Error formatting StockX search result: {e}")
            return {'platform': 'StockX', 'error': str(e)}
    
    def _format_stockx_product_data(self, raw_data: Dict, size: str = None) -> Dict:
        """
        Format detailed StockX product data
        """
        try:
            formatted = {
                'platform': 'StockX',
                'product_id': raw_data.get('id', raw_data.get('uuid')),
                'name': raw_data.get('title', raw_data.get('name')),
                'brand': raw_data.get('brand'),
                'retail_price': self._parse_price(raw_data.get('retailPrice')),
                'market_price': self._parse_price(raw_data.get('market', {}).get('lowestAsk', raw_data.get('lowestAsk'))),
                'last_sale': self._parse_price(raw_data.get('market', {}).get('lastSale', raw_data.get('lastSale'))),
                'highest_bid': self._parse_price(raw_data.get('market', {}).get('highestBid', raw_data.get('highestBid'))),
                'image_url': self._extract_image_url(raw_data),
                'sku': raw_data.get('styleId'),
                'colorway': raw_data.get('colorway'),
                'release_date': raw_data.get('releaseDate'),
                'sizes_available': [],
                'price_by_size': {},
                'sales_data': {
                    'total_sales': raw_data.get('market', {}).get('numberOfCustomers', 0),
                    'price_premium': raw_data.get('market', {}).get('pricePremium', 0),
                    'annual_high': self._parse_price(raw_data.get('market', {}).get('annualHigh')),
                    'annual_low': self._parse_price(raw_data.get('market', {}).get('annualLow'))
                }
            }
            
            # Extract detailed size pricing
            market_data = raw_data.get('market', {})
            if 'lowestAskBySize' in market_data:
                for size_data in market_data['lowestAskBySize']:
                    if isinstance(size_data, dict):
                        size_val = size_data.get('size', '')
                        lowest_ask = size_data.get('lowestAsk', 0)
                        
                        if size_val and lowest_ask:
                            formatted['sizes_available'].append(str(size_val))
                            formatted['price_by_size'][str(size_val)] = self._parse_price(lowest_ask)
            
            # If specific size requested, prioritize that price
            if size and size in formatted['price_by_size']:
                formatted['size_specific_price'] = formatted['price_by_size'][size]
                formatted['market_price'] = formatted['price_by_size'][size]
            
            # Use last sale as market price if no lowest ask
            if not formatted['market_price'] and formatted.get('last_sale'):
                formatted['market_price'] = formatted['last_sale']
            
            return formatted
            
        except Exception as e:
            logger.error(f"Error formatting StockX product data: {e}")
            return {'platform': 'StockX', 'error': str(e)}
    
    def _format_stockx_data(self, raw_data: Dict, size: str = None) -> Dict:
        """
        Format StockX API response data
        """
        try:
            formatted = {
                'platform': 'StockX',
                'product_id': raw_data.get('id'),
                'name': raw_data.get('name'),
                'brand': raw_data.get('brand'),
                'retail_price': self._parse_price(raw_data.get('retailPrice')),
                'market_price': self._parse_price(raw_data.get('estimatedMarketValue')),
                'image_url': self._extract_image_url(raw_data),
                'release_date': raw_data.get('releaseDate'),
                'sku': raw_data.get('sku'),
                'colorway': raw_data.get('colorway'),
                'sizes_available': [],
                'price_by_size': {}
            }
            
            # Extract size-specific pricing if available
            if 'sizes' in raw_data and isinstance(raw_data['sizes'], list):
                for size_info in raw_data['sizes']:
                    if isinstance(size_info, dict):
                        size_val = size_info.get('size', size_info.get('US', ''))
                        price_val = size_info.get('price', size_info.get('lowestAsk', 0))
                        
                        if size_val and price_val:
                            formatted['sizes_available'].append(str(size_val))
                            formatted['price_by_size'][str(size_val)] = self._parse_price(price_val)
            
            # If specific size requested, get that price
            if size and size in formatted['price_by_size']:
                formatted['size_specific_price'] = formatted['price_by_size'][size]
            
            return formatted
            
        except Exception as e:
            logger.error(f"Error formatting StockX data: {e}")
            return {'platform': 'StockX', 'error': str(e)}
    
    def _format_alternative_data(self, raw_data: Dict, size: str = None) -> Dict:
        """
        Format alternative API response data
        """
        try:
            formatted = {
                'platform': 'Alternative',
                'product_id': raw_data.get('id'),
                'name': raw_data.get('name', raw_data.get('title')),
                'brand': raw_data.get('brand'),
                'retail_price': self._parse_price(raw_data.get('retail_price', raw_data.get('retailPrice'))),
                'market_price': self._parse_price(raw_data.get('price', raw_data.get('currentPrice'))),
                'image_url': self._extract_image_url(raw_data),
                'sku': raw_data.get('sku', raw_data.get('style_id')),
                'colorway': raw_data.get('colorway')
            }
            
            return formatted
            
        except Exception as e:
            logger.error(f"Error formatting alternative data: {e}")
            return {'platform': 'Alternative', 'error': str(e)}
    
    def _generate_pricing_summary(self, sources: Dict) -> Dict:
        """
        Generate pricing summary from multiple sources
        """
        summary = {
            'retail_price': None,
            'current_market_price': None,
            'price_range': {'min': None, 'max': None},
            'sources_count': len(sources),
            'confidence': 'low'
        }
        
        prices = []
        retail_prices = []
        
        for source_name, source_data in sources.items():
            if isinstance(source_data, dict) and 'error' not in source_data:
                # Collect market prices
                market_price = source_data.get('market_price')
                size_price = source_data.get('size_specific_price')
                
                if market_price:
                    prices.append(market_price)
                elif size_price:
                    prices.append(size_price)
                
                # Collect retail prices
                retail_price = source_data.get('retail_price')
                if retail_price:
                    retail_prices.append(retail_price)
        
        # Calculate summary values
        if prices:
            summary['current_market_price'] = sum(prices) / len(prices)  # Average
            summary['price_range']['min'] = min(prices)
            summary['price_range']['max'] = max(prices)
            
            # Set confidence based on number of sources and price consistency
            if len(prices) >= 2:
                price_variance = max(prices) - min(prices)
                if price_variance <= summary['current_market_price'] * 0.1:  # Within 10%
                    summary['confidence'] = 'high'
                else:
                    summary['confidence'] = 'medium'
            else:
                summary['confidence'] = 'medium'
        
        if retail_prices:
            summary['retail_price'] = sum(retail_prices) / len(retail_prices)
        
        return summary
    
    def _parse_price(self, price) -> Optional[float]:
        """Parse price from various formats"""
        if price is None:
            return None
        
        try:
            if isinstance(price, (int, float)):
                return float(price)
            elif isinstance(price, str):
                # Remove currency symbols and convert
                clean_price = price.replace('$', '').replace(',', '').replace('€', '').replace('£', '').strip()
                return float(clean_price) if clean_price else None
        except (ValueError, TypeError):
            pass
        
        return None
    
    def _extract_image_url(self, data: Dict) -> Optional[str]:
        """Extract image URL from API response"""
        image_fields = [
            'image_url', 'imageUrl', 'image', 'thumbnail', 'picture_url',
            'mainPictureUrl', 'pictureUrl'
        ]
        
        for field in image_fields:
            if field in data and data[field]:
                image_val = data[field]
                
                # Handle nested image objects
                if isinstance(image_val, dict):
                    for quality in ['original', 'large', 'medium', 'small', 'thumbnail']:
                        if quality in image_val and image_val[quality]:
                            url = image_val[quality]
                            if isinstance(url, str) and url.startswith(('http://', 'https://')):
                                return url
                
                # Handle direct URL strings
                elif isinstance(image_val, str) and image_val.startswith(('http://', 'https://')):
                    return image_val
        
        return None
    
    def search_sneakers_by_query(self, query: str, limit: int = 5) -> Optional[List[Dict]]:
        """
        Search for sneakers by query string and return pricing data
        
        Args:
            query: Search query (e.g., "Jordan 1 Bred", "Yeezy 350 v2")
            limit: Maximum number of results
            
        Returns:
            List of sneakers with pricing data
        """
        try:
            # Parse the query to extract components
            query_parts = query.strip().split()
            if len(query_parts) < 2:
                return None
            
            # Assume first part is brand, rest is model/colorway
            brand = query_parts[0]
            model_colorway = " ".join(query_parts[1:])
            
            # Get pricing data
            pricing_data = self.get_sneaker_prices(brand, model_colorway)
            
            if pricing_data:
                return [pricing_data]
            
        except Exception as e:
            logger.error(f"Error searching sneakers: {e}")
        
        return None
    
    def _create_demo_response(self, brand: str, model: str, colorway: str = None, 
                             sku: str = None, size: str = None) -> Dict:
        """
        Create a dynamic demonstration response when APIs are unavailable
        This shows users how the feature works with realistic, sneaker-specific demo data
        """
        # Generate realistic pricing based on sneaker characteristics
        retail_price, market_price = self._generate_realistic_pricing(brand, model, colorway, sku)
        
        # Calculate price range with some variance
        price_variance = market_price * 0.15  # 15% variance
        min_price = max(retail_price, market_price - price_variance)
        max_price = market_price + price_variance
        
        # Determine confidence based on sneaker popularity
        confidence = self._estimate_confidence(brand, model, colorway)
        
        return {
            'brand': brand,
            'model': model,
            'colorway': colorway,
            'sku': sku,
            'size': size,
            'last_updated': datetime.utcnow().isoformat(),
            'sources': {
                'demo': {
                    'platform': 'DEMO DATA',
                    'name': f"{brand} {model}" + (f" {colorway}" if colorway else ""),
                    'brand': brand,
                    'retail_price': retail_price,
                    'market_price': market_price,
                    'note': 'This is demonstration data showing how real-time pricing works'
                }
            },
            'summary': {
                'retail_price': retail_price,
                'current_market_price': market_price,
                'price_range': {'min': round(min_price, 2), 'max': round(max_price, 2)},
                'sources_count': 1,
                'confidence': confidence,
                'note': 'DEMO DATA - Enable API access for real pricing'
            },
            'is_demo': True
        }
    
    def _generate_realistic_pricing(self, brand: str, model: str, colorway: str = None, sku: str = None) -> tuple:
        """
        Generate realistic pricing based on sneaker characteristics
        """
        brand_lower = brand.lower()
        model_lower = model.lower()
        colorway_lower = colorway.lower() if colorway else ""
        
        # Base retail prices by brand
        brand_retail_mapping = {
            'nike': 140,
            'jordan': 170,
            'adidas': 130,
            'yeezy': 220,
            'new balance': 130,
            'asics': 120,
            'puma': 110,
            'vans': 70,
            'converse': 70,
            'reebok': 100
        }
        
        # Model multipliers for popular/limited models
        model_multipliers = {
            # Nike models
            'air jordan 1': 1.2,
            'air jordan 4': 1.3,
            'air jordan 11': 1.4,
            'dunk': 1.1,
            'air force 1': 0.9,
            'air max': 1.0,
            'blazer': 1.0,
            'lebron': 1.1,
            
            # Adidas models
            'yeezy 350': 2.0,
            'yeezy 700': 2.2,
            'ultraboost': 1.0,
            'stan smith': 0.8,
            'nmd': 0.9,
            
            # Other brands
            'chuck taylor': 0.7,
            'old skool': 0.8,
            '990': 1.5,
            '550': 1.3
        }
        
        # Colorway multipliers for hype colorways
        colorway_multipliers = {
            'bred': 1.3,
            'chicago': 1.4,
            'royal': 1.2,
            'off white': 2.5,
            'travis scott': 3.0,
            'fragment': 2.0,
            'union': 1.8,
            'dior': 5.0,
            'black toe': 1.2,
            'shadow': 1.1,
            'mocha': 1.5,
            'obsidian': 1.3
        }
        
        # Determine base retail price
        retail_price = 140  # Default
        for brand_key, price in brand_retail_mapping.items():
            if brand_key in brand_lower:
                retail_price = price
                break
        
        # Apply model multiplier
        model_multiplier = 1.0
        for model_key, multiplier in model_multipliers.items():
            if model_key in model_lower:
                model_multiplier = multiplier
                break
        
        # Apply colorway multiplier
        colorway_multiplier = 1.0
        for colorway_key, multiplier in colorway_multipliers.items():
            if colorway_key in colorway_lower:
                colorway_multiplier = multiplier
                break
        
        # Calculate final prices
        final_retail = round(retail_price * model_multiplier)
        
        # Market price is usually 1.2-3x retail for regular releases, more for hype
        base_market_multiplier = 1.5  # Conservative multiplier
        market_price = round(final_retail * base_market_multiplier * colorway_multiplier)
        
        # Add some randomness to make it feel more realistic
        import hashlib
        sneaker_hash = hashlib.md5(f"{brand}{model}{colorway}".encode()).hexdigest()
        price_variation = int(sneaker_hash[:2], 16) % 40 - 20  # -20 to +20
        market_price += price_variation
        
        # Ensure market price is at least retail
        market_price = max(market_price, final_retail)
        
        return float(final_retail), float(market_price)
    
    def _estimate_confidence(self, brand: str, model: str, colorway: str = None) -> str:
        """
        Estimate confidence level based on sneaker popularity and data availability
        """
        brand_lower = brand.lower()
        model_lower = model.lower()
        colorway_lower = colorway.lower() if colorway else ""
        
        # High confidence brands/models
        high_confidence_indicators = [
            'air jordan', 'dunk', 'yeezy', 'off white', 'travis scott'
        ]
        
        # Medium confidence brands/models
        medium_confidence_indicators = [
            'nike', 'adidas', 'air max', 'ultraboost', 'air force'
        ]
        
        search_text = f"{brand_lower} {model_lower} {colorway_lower}"
        
        for indicator in high_confidence_indicators:
            if indicator in search_text:
                return 'high'
        
        for indicator in medium_confidence_indicators:
            if indicator in search_text:
                return 'medium'
        
        return 'low'

# Create a global instance
realtime_pricing_api = RealtimePricingAPI()