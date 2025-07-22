# How to Upload Sneakio to GitHub

Your Sneakio project is ready for GitHub! Here are the files you need to upload:

## Core Application Files
- `app.py` - Flask application setup
- `main.py` - Entry point for the application
- `models.py` - Database models (Sneaker, Sale, Listing)
- `routes.py` - All web routes and controllers  
- `forms.py` - WTForms for data validation
- `utils.py` - Helper functions and business logic

## API Integration
- `realtime_pricing_api.py` - StockX pricing integration
- `sneaker_database_api.py` - Sneaker data lookup

## Frontend Assets
- `static/css/custom.css` - All custom styling
- `static/js/` - JavaScript files (theme, sidebar, etc.)
- `templates/` - All HTML templates

## Configuration
- `pyproject.toml` - Python dependencies
- `uv.lock` - Lock file for dependencies
- `.replit` - Replit configuration (optional)

## Documentation  
- `README.md` - Comprehensive project documentation
- `replit.md` - Technical architecture details
- `.gitignore` - Git ignore patterns

## Upload Steps:
1. Go to https://github.com/sp00kyzsh/sneakio
2. Upload all files from your Replit project
3. Use commit message: "Initial commit: Complete Sneakio sneaker reselling management platform"

Your project includes:
✓ Modern vertical sidebar navigation
✓ Real-time StockX pricing integration  
✓ Multi-platform listing management
✓ Complete inventory tracking system
✓ Sales analytics and reporting
✓ Light/dark theme support
✓ Mobile-responsive design
✓ Production-ready Flask application