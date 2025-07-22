# Sneakio - Sneaker Reselling Management Application

## Overview

Sneakio is a Flask-based web application designed to help sneaker resellers manage their inventory, track sales, and analyze their business performance. The application provides a comprehensive dashboard for managing sneaker collections, recording sales transactions, and generating business insights.

**Current Status**: Fully functional with complete API integration, multi-platform listing management, real-time pricing, and modern vertical sidebar layout (July 21, 2025)
- All core features implemented and tested
- **Complete Sneaker Database API integration** with real-time SKU lookup functionality
- **Real-time Pricing API integration** with StockX Pricing Data and Market Analytics API
- **Interactive pricing lookup** in both add/edit sneaker forms with confidence scoring and source attribution
- **Market price auto-population** with one-click listing price updates from current market data
- **Dynamic demo pricing system** that generates realistic, sneaker-specific prices based on brand, model, and colorway characteristics
- **Auto-population of sneaker data** including images, prices, release dates, categories, and descriptions
- **Product image and description display** in forms and individual sneaker view pages
- **HTML entity decoding** for clean description text display
- **Multi-platform listing management system** with comprehensive tracking across StockX, GOAT, eBay, Facebook, Instagram, and more
- **Platform-specific pricing and status tracking** with direct listing URLs and profit calculations
- **Integrated listing management** in sneaker detail pages with quick actions
- **Global listings dashboard** with filtering by platform and status
- Complete modern design overhaul with Inter typography and gradient elements
- **Vertical sidebar navigation** replacing horizontal navbar for modern dashboard feel
- Glassmorphism effects with backdrop blur and contemporary styling
- Enhanced card designs with hover animations and modern metric cards
- Professional purple gradient color scheme throughout
- 4-column inventory grid layout with proper responsive breakpoints
- Fixed dropdown visibility issues for improved usability across themes
- **Fully functional light/dark mode toggle** with theme persistence and sidebar-optimized styling
- Clean, streamlined forms with SKU lookup integration
- Category field for Men's, Women's, and Children's sizing classification
- Comprehensive sneaker data tracking with API enhancement
- Duplicate sneaker functionality for efficient inventory management
- Individual sneaker view pages with detailed information and financial summaries
- **Production-ready with authentic data integration and complete listing workflow**

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Template Engine**: Jinja2 templates with Bootstrap 5 (dark theme)
- **Typography**: Inter font family for modern, professional appearance
- **Styling**: Modern CSS with glassmorphism effects, gradient elements, and backdrop blur
- **Design System**: Purple gradient color scheme with contemporary visual hierarchy
- **JavaScript**: Vanilla JavaScript with enhanced theme toggle and form interactions
- **Icons**: Font Awesome with updated modern iconography
- **Charts**: Chart.js for data visualization in analytics
- **Responsive Design**: 4-column inventory grid with proper mobile optimization

### Backend Architecture
- **Framework**: Flask (Python web framework)
- **Structure**: Modular design with separate files for routes, models, forms, and utilities
- **Session Management**: Flask sessions with configurable secret key
- **Logging**: Python logging module for debugging

### Data Storage Solutions
- **Primary Storage**: PostgreSQL database with SQLAlchemy ORM
- **Data Models**: SQLAlchemy models (Sneaker, Sale) with database relationships
- **ID Management**: Auto-incrementing primary keys with foreign key relationships

## Key Components

### Models (models.py)
- **Sneaker Class**: Represents sneaker inventory items with comprehensive attributes including:
  - Basic info: SKU, brand, model, size, colorway, condition, description
  - Category classification: Men's, Women's, or Children's sizing
  - Pricing data: retail price, purchase price, listing price
  - Date tracking: release date, purchase date, created/updated timestamps
  - **Listings relationship**: One-to-many relationship with platform listings
- **Sale Class**: Represents completed sales transactions with sale price, platform, fees, and profit calculations
- **Listing Class**: Represents platform-specific listings with comprehensive tracking including:
  - Platform identification: StockX, GOAT, eBay, Facebook, Instagram, Local, etc.
  - Pricing and status: listing price, status (Active/Paused/Sold/Expired), profit calculations
  - URL management: Direct links to platform listings for easy access
  - Date tracking: listing date, last updated date, created/updated timestamps
  - Platform icons: Dynamic icon mapping for visual platform identification
- **Data Methods**: Built-in serialization and update methods for data manipulation
- **SKU Integration**: Optional SKU field with StockX research link functionality

### Forms (forms.py)
- **SneakerForm**: WTForms-based form for adding/editing sneaker inventory with fields for:
  - Product details: brand, model, colorway, size, category, condition, description
  - Pricing: retail price (optional), purchase price (required), listing price (optional)
  - Dates: release date (optional), purchase date (required)
  - Additional: SKU (optional), notes (optional)
- **SaleForm**: Form for recording sales transactions with validation
- **ListingForm**: Form for managing platform listings with comprehensive fields for:
  - Platform selection: Multi-platform dropdown with popular selling platforms
  - Pricing and status: listing price, status tracking (Active/Paused/Sold/Expired)
  - URL management: Optional direct listing URL for platform access
  - Date tracking: listing date with automatic today default
  - Notes: Optional platform-specific notes and details
- **Validation**: Comprehensive field validation including required fields, number ranges, and length constraints

### Routes (routes.py)
- **Dashboard**: Main overview with key metrics and recent activity
- **Inventory Management**: CRUD operations for sneaker collection with dual view options (grid/table)
- **Individual Sneaker View**: Detailed view page with complete sneaker information, financial summaries, sale history, and integrated listings management
- **Sales Tracking**: Recording and viewing sales transactions
- **Platform Listings Management**: Complete CRUD operations for multi-platform listings including:
  - Individual sneaker listings view with platform-specific details
  - Add/edit/delete listing functionality with form validation
  - Global listings dashboard with advanced filtering by platform and status
  - Direct platform URL integration for easy listing access
  - Real-time profit calculations and status tracking
- **Analytics**: Business performance metrics and insights
- **Search/Filter**: Advanced filtering capabilities for inventory, sales, and listings
- **Duplication**: Clone existing sneakers for efficient similar item entry
- **External Research**: Direct StockX market research integration via SKU links

### Utilities (utils.py)
- **Data Retrieval**: Helper functions for finding sneakers and sales by ID
- **Analytics Engine**: Comprehensive profit/loss calculations, ROI metrics, and performance analysis
- **Business Logic**: Profit calculations, days-to-sale tracking, brand performance analysis

### API Integration

#### The Sneaker Database API (sneaker_database_api.py)
- **Production-ready API client** with comprehensive error handling and failover strategies
- **SKU Lookup**: Automated sneaker data retrieval using style codes and product identifiers
- **Data Enrichment**: Automatic population of brand, model, colorway, pricing, and release information
- **Image Integration**: Direct product image URLs for visual inventory management
- **Error Resilience**: Robust exception handling with graceful degradation for API failures
- **Response Caching**: Optimized API calls with intelligent retry logic and timeout management

#### Real-time Pricing API (realtime_pricing_api.py)
- **StockX Integration**: Primary integration with StockX Pricing Data and Market Analytics API
- **Multi-source Price Aggregation**: Attempts to fetch current market pricing from multiple platforms
- **Size-specific Pricing**: Detailed pricing breakdown by shoe size when available
- **Advanced Market Data**: Includes lowest ask, highest bid, last sale prices, and annual highs/lows
- **Confidence Scoring**: Data reliability indicators based on source count and price consistency
- **Interactive Integration**: Real-time lookup buttons in both add/edit sneaker forms
- **Market Price Auto-population**: One-click updates to listing prices from current market data
- **Dynamic Demo Mode**: Realistic sneaker-specific fallback data based on brand, model, and colorway factors
- **Source Attribution**: Clear labeling of data sources for transparency and verification
- **API Routes**: RESTful endpoints at `/api/pricing/lookup` and `/api/pricing/search`

## API Configuration Requirements

### StockX Pricing Data API
The application is configured to use the premium StockX Pricing Data and Market Analytics API:
- **API Host**: `stockx-pricing-data-and-market-analytics.p.rapidapi.com`
- **Required Subscription**: Premium subscription level for access
- **Endpoints Used**: 
  - `/search` - Product search functionality
  - `/product/{id}` - Detailed product pricing data
  - `/product/sku` - SKU-based product lookup
- **Features**: Real-time lowest ask prices, highest bids, sales volume, and size-specific pricing

## Data Flow

1. **Inventory Management**: Users add sneakers → stored in PostgreSQL → displayed in grid/table inventory views
2. **Sales Recording**: Users record sales → linked to existing sneaker inventory via foreign keys → profit calculations performed
3. **Analytics Generation**: System processes sales and inventory data from database → generates metrics → displays in dashboard and analytics views
4. **Search/Filter**: User input → filtered database queries → updated views with preserved view preferences
5. **View Switching**: Users toggle between grid and table views → preserves current filters and search state

## External Dependencies

### Python Packages
- **Flask**: Core web framework
- **Flask-WTF**: Form handling and CSRF protection
- **WTForms**: Form validation and rendering

### Frontend Libraries
- **Bootstrap 5**: UI framework with dark theme
- **Font Awesome**: Icon library
- **Chart.js**: Data visualization
- **Bootstrap JavaScript**: Interactive components

### Development Dependencies
- **Python logging**: Application debugging
- **Flask development server**: Local development environment

## Deployment Strategy

### Current Setup
- **Development Mode**: Flask development server with debug enabled
- **Host Configuration**: Configured for 0.0.0.0:5000 for broad accessibility
- **Environment Variables**: SESSION_SECRET for production security

### Production Considerations
- **Data Persistence**: Current in-memory storage needs database integration
- **Security**: Environment-based secret key management
- **Scalability**: Architecture supports easy migration to persistent database
- **Database Migration Path**: Models designed for easy ORM integration (Drizzle/SQLAlchemy compatible)

### Deployment Requirements
- **Python 3.x** environment
- **Flask** and dependencies installed
- **Static file serving** for CSS/JS assets
- **Environment variable** configuration for production secrets

The application is designed with a clean separation of concerns, making it easy to extend functionality, add new features, or migrate to a more robust database solution when needed.