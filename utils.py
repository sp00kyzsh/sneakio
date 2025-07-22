from typing import Dict
from datetime import datetime
from collections import defaultdict
from models import Sneaker, Sale

def calculate_analytics() -> Dict:
    """Calculate comprehensive analytics"""
    sneakers = Sneaker.query.all()
    sales = Sale.query.all()
    
    analytics = {
        'total_sneakers': len(sneakers),
        'total_sales': len(sales),
        'available_inventory': len(sneakers) - len(sales),
        'total_invested': 0.0,
        'total_revenue': 0.0,
        'total_profit': 0.0,
        'total_fees': 0.0,
        'average_profit_per_sale': 0.0,
        'average_days_to_sale': 0.0,
        'monthly_profits': [],
        'brand_performance': [],
        'recent_activity': []
    }
    
    if not sneakers:
        return analytics
    
    # Calculate totals
    analytics['total_invested'] = sum(float(s.purchase_price) for s in sneakers)
    
    if sales:
        analytics['total_revenue'] = sum(float(s.sale_price) for s in sales)
        analytics['total_fees'] = sum(float(s.fees) + float(s.shipping_cost) for s in sales)
        
        # Calculate profits
        profits = []
        days_to_sale = []
        
        for sale in sales:
            if sale.sneaker:
                profit = sale.calculate_profit()
                profits.append(profit)
                days = sale.calculate_days_to_sale()
                if days > 0:
                    days_to_sale.append(days)
        
        analytics['total_profit'] = sum(profits)
        analytics['average_profit_per_sale'] = sum(profits) / len(profits) if profits else 0
        analytics['average_days_to_sale'] = sum(days_to_sale) / len(days_to_sale) if days_to_sale else 0
    
    # Monthly profit analysis
    monthly_data = defaultdict(float)
    for sale in sales:
        try:
            sale_date = datetime.fromisoformat(sale.sale_date.replace('Z', '+00:00'))
            month_key = sale_date.strftime('%Y-%m')
            if sale.sneaker:
                profit = sale.calculate_profit()
                monthly_data[month_key] += profit
        except:
            continue
    
    analytics['monthly_profits'] = [
        {'month': month, 'profit': profit}
        for month, profit in sorted(monthly_data.items())
    ]
    
    # Brand performance analysis
    brand_data = defaultdict(lambda: {'sales': 0, 'profit': 0.0, 'revenue': 0.0})
    for sale in sales:
        if sale.sneaker:
            brand = sale.sneaker.brand
            brand_data[brand]['sales'] += 1
            brand_data[brand]['revenue'] += float(sale.sale_price)
            brand_data[brand]['profit'] += sale.calculate_profit()
    
    analytics['brand_performance'] = [
        {
            'brand': brand,
            'sales': data['sales'],
            'revenue': data['revenue'],
            'profit': data['profit'],
            'avg_profit': data['profit'] / data['sales'] if data['sales'] > 0 else 0
        }
        for brand, data in brand_data.items()
    ]
    
    # Sort by profit
    analytics['brand_performance'].sort(key=lambda x: x['profit'], reverse=True)
    
    return analytics

def format_currency(amount: float) -> str:
    """Format amount as currency"""
    return f"${amount:,.2f}"

def format_percentage(value: float) -> str:
    """Format value as percentage"""
    return f"{value:.1f}%"
