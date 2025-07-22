# Sneakio - Sneaker Reselling Management Platform

A comprehensive sneaker reselling business management platform that provides streamlined inventory tracking, sales management, and real-time pricing data for sneaker entrepreneurs.

![Sneakio Dashboard](https://img.shields.io/badge/Status-Production%20Ready-brightgreen)

## Features

### 🏷️ Complete Inventory Management
- **Modern Dashboard**: Vertical sidebar navigation with clean, professional design
- **Dual View Options**: Switch between grid and table views for inventory
- **Advanced Filtering**: Search by brand, model, colorway, condition, and more
- **SKU Integration**: Direct StockX research links for market analysis
- **Category Classification**: Men's, Women's, and Children's sizing support

### 💰 Real-time Pricing Integration
- **StockX API Integration**: Live market pricing data with confidence scoring
- **Interactive Price Lookup**: One-click market price updates in forms
- **Multi-source Price Aggregation**: Comprehensive pricing from multiple platforms
- **Dynamic Demo System**: Realistic fallback pricing based on sneaker characteristics

### 📊 Multi-Platform Listing Management
- **Platform Support**: StockX, GOAT, eBay, Facebook, Instagram, Local sales
- **Status Tracking**: Active, Paused, Sold, Expired listing states
- **Profit Calculations**: Real-time profit analysis per platform
- **Direct URLs**: Quick access to platform listings
- **Global Dashboard**: Centralized view of all listings with filtering

### 📈 Sales & Analytics
- **Transaction Recording**: Complete sales history with profit tracking
- **Performance Metrics**: ROI analysis, days-to-sale tracking
- **Brand Performance**: Analysis by brand, model, and market trends
- **Visual Analytics**: Chart.js integration for data visualization

### 🎨 Modern UI/UX
- **Light/Dark Mode**: Complete theme switching with persistence
- **Responsive Design**: Mobile-first approach with Bootstrap 5
- **Glassmorphism Effects**: Modern visual design with backdrop blur
- **Purple Gradient Scheme**: Professional color palette throughout
- **Inter Typography**: Clean, modern font choices

## Technology Stack

### Backend
- **Flask**: Python web framework
- **PostgreSQL**: Robust database with SQLAlchemy ORM
- **Gunicorn**: Production WSGI server
- **WTForms**: Form validation and handling

### Frontend
- **Bootstrap 5**: Responsive UI framework with dark theme
- **Vanilla JavaScript**: Enhanced interactions and theme management
- **Font Awesome**: Modern iconography
- **Chart.js**: Data visualization and analytics

### APIs & Integration
- **StockX Pricing Data API**: Real-time sneaker market pricing
- **The Sneaker Database API**: Product information and images
- **Multi-platform Integration**: Direct links to major reselling platforms

## Installation

### Prerequisites
- Python 3.8+
- PostgreSQL database
- API keys for pricing services (optional for demo mode)

### Setup
1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/sneakio.git
   cd sneakio
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set environment variables**
   ```bash
   export DATABASE_URL="postgresql://username:password@localhost/sneakio"
   export SESSION_SECRET="your-secret-key-here"
   export RAPIDAPI_KEY="your-rapidapi-key" # Optional
   ```

4. **Initialize the database**
   ```bash
   python -c "from app import app, db; app.app_context().push(); db.create_all()"
   ```

5. **Run the application**
   ```bash
   gunicorn --bind 0.0.0.0:5000 --reload main:app
   ```

## Usage

### Getting Started
1. **Add Sneakers**: Use the SKU lookup feature to automatically populate sneaker data
2. **Set Listing Prices**: Utilize real-time pricing data for competitive pricing
3. **Track Sales**: Record transactions across multiple platforms
4. **Monitor Performance**: Use analytics to optimize your reselling strategy

### Key Workflows
- **Inventory Management**: Add → Price → List → Track → Sell
- **Market Research**: SKU Lookup → Price Analysis → Competitive Positioning
- **Multi-platform Selling**: Create listings across platforms with centralized tracking

## API Configuration

### StockX Pricing Data API
For live pricing data, configure the premium StockX API:
- **Subscription**: Premium tier required
- **Endpoints**: Product search, pricing data, SKU lookup
- **Features**: Real-time asks/bids, sales volume, size-specific pricing

### Fallback Systems
- **Demo Mode**: Realistic pricing based on brand/model characteristics
- **Graceful Degradation**: Continues operation without API access
- **Error Handling**: Comprehensive fallback strategies

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- **Bootstrap Team**: For the excellent UI framework
- **StockX**: For providing comprehensive sneaker market data
- **Flask Community**: For the robust web framework
- **Font Awesome**: For the beautiful icon library

## Contact

For questions, suggestions, or support, please open an issue on GitHub.

---

**Built with ❤️ for the sneaker reselling community**