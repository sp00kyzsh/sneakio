from datetime import datetime
from typing import Dict
from app import db

class Sneaker(db.Model):
    __tablename__ = 'sneakers'
    
    id = db.Column(db.Integer, primary_key=True)
    sku = db.Column(db.String(50), nullable=True)
    brand = db.Column(db.String(100), nullable=False)
    model = db.Column(db.String(100), nullable=False)
    size = db.Column(db.String(20), nullable=False)
    category = db.Column(db.String(20), default="Men's")
    colorway = db.Column(db.String(100), nullable=False)
    retail_price = db.Column(db.Numeric(10, 2), nullable=True)
    release_date = db.Column(db.String(50), nullable=True)
    purchase_price = db.Column(db.Numeric(10, 2), nullable=False)
    purchase_date = db.Column(db.String(50), nullable=False)
    condition = db.Column(db.String(50), default="New")
    description = db.Column(db.Text, default="")
    notes = db.Column(db.Text, default="")
    listing_price = db.Column(db.Numeric(10, 2), default=0.0)
    image_url = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    sales = db.relationship('Sale', backref='sneaker', lazy=True)
    listings = db.relationship('Listing', backref='sneaker', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'sku': self.sku,
            'brand': self.brand,
            'model': self.model,
            'size': self.size,
            'category': self.category,
            'colorway': self.colorway,
            'retail_price': float(self.retail_price) if self.retail_price else None,
            'release_date': self.release_date,
            'purchase_price': float(self.purchase_price),
            'purchase_date': self.purchase_date,
            'condition': self.condition,
            'description': self.description,
            'notes': self.notes,
            'listing_price': float(self.listing_price),
            'image_url': self.image_url,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Sale(db.Model):
    __tablename__ = 'sales'
    
    id = db.Column(db.Integer, primary_key=True)
    sneaker_id = db.Column(db.Integer, db.ForeignKey('sneakers.id'), nullable=False)
    sale_price = db.Column(db.Numeric(10, 2), nullable=False)
    sale_date = db.Column(db.String(50), nullable=False)
    buyer_info = db.Column(db.String(200), default="")
    platform = db.Column(db.String(100), default="")
    tracking_number = db.Column(db.String(100), default="")
    fees = db.Column(db.Numeric(10, 2), default=0.0)
    shipping_cost = db.Column(db.Numeric(10, 2), default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def calculate_days_to_sale(self) -> int:
        """Calculate days between purchase and sale"""
        if self.sneaker:
            try:
                purchase_date = datetime.fromisoformat(self.sneaker.purchase_date.replace('Z', '+00:00'))
                sale_date = datetime.fromisoformat(self.sale_date.replace('Z', '+00:00'))
                return (sale_date - purchase_date).days
            except:
                return 0
        return 0
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'sneaker_id': self.sneaker_id,
            'sale_price': float(self.sale_price),
            'sale_date': self.sale_date,
            'buyer_info': self.buyer_info,
            'platform': self.platform,
            'tracking_number': self.tracking_number,
            'fees': float(self.fees),
            'shipping_cost': float(self.shipping_cost),
            'days_to_sale': self.calculate_days_to_sale(),
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def calculate_profit(self) -> float:
        """Calculate profit for this sale"""
        if self.sneaker:
            total_costs = float(self.sneaker.purchase_price) + float(self.fees) + float(self.shipping_cost)
            return float(self.sale_price) - total_costs
        return 0.0

class Listing(db.Model):
    __tablename__ = 'listings'
    
    id = db.Column(db.Integer, primary_key=True)
    sneaker_id = db.Column(db.Integer, db.ForeignKey('sneakers.id'), nullable=False)
    platform = db.Column(db.String(50), nullable=False)
    listing_url = db.Column(db.Text, nullable=True)
    listing_price = db.Column(db.Numeric(10, 2), nullable=False)
    listing_status = db.Column(db.String(20), default='Active')
    date_listed = db.Column(db.Date, nullable=False)
    date_updated = db.Column(db.Date, nullable=True)
    notes = db.Column(db.Text, default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'sneaker_id': self.sneaker_id,
            'platform': self.platform,
            'listing_url': self.listing_url,
            'listing_price': float(self.listing_price),
            'listing_status': self.listing_status,
            'date_listed': self.date_listed.isoformat() if self.date_listed else None,
            'date_updated': self.date_updated.isoformat() if self.date_updated else None,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def is_active(self) -> bool:
        """Check if listing is currently active"""
        return self.listing_status.lower() == 'active'
    
    def get_platform_icon(self) -> str:
        """Get icon class for platform"""
        platform_icons = {
            'StockX': 'fas fa-chart-line',
            'GOAT': 'fas fa-mountain',
            'eBay': 'fab fa-ebay',
            'Facebook': 'fab fa-facebook',
            'Instagram': 'fab fa-instagram',
            'Local': 'fas fa-map-marker-alt',
            'Grailed': 'fas fa-tshirt',
            'Vinted': 'fas fa-tags',
            'Depop': 'fas fa-shopping-bag',
            'Other': 'fas fa-globe'
        }
        return platform_icons.get(self.platform, 'fas fa-globe')
