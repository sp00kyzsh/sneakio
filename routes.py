from flask import render_template, request, redirect, url_for, flash, jsonify
from app import app, db
from models import Sneaker, Sale, Listing
from forms import SneakerForm, SaleForm, ListingForm
from utils import calculate_analytics
from sneaker_database_api import sneaker_db_api
from realtime_pricing_api import realtime_pricing_api

from datetime import datetime
import logging
import json

@app.route('/')
def index():
    """Dashboard with key metrics"""
    analytics = calculate_analytics()
    recent_sales = Sale.query.order_by(Sale.created_at.desc()).limit(5).all()
    recent_sneakers = Sneaker.query.order_by(Sneaker.created_at.desc()).limit(5).all()
    
    return render_template('index.html', 
                         analytics=analytics,
                         recent_sales=recent_sales,
                         recent_sneakers=recent_sneakers)

@app.route('/inventory')
def inventory():
    """View all sneaker inventory"""
    search = request.args.get('search', '')
    condition_filter = request.args.get('condition', '')
    brand_filter = request.args.get('brand', '')
    view = request.args.get('view', 'table')  # Default to table view
    
    query = Sneaker.query
    
    if search:
        search_term = f"%{search.lower()}%"
        query = query.filter(
            db.or_(
                Sneaker.brand.ilike(search_term),
                Sneaker.model.ilike(search_term),
                Sneaker.colorway.ilike(search_term)
            )
        )
    
    if condition_filter:
        query = query.filter(Sneaker.condition == condition_filter)
    
    if brand_filter:
        query = query.filter(Sneaker.brand.ilike(f"%{brand_filter}%"))
    
    filtered_sneakers = query.all()
    
    # Get unique brands and conditions for filters
    all_sneakers = Sneaker.query.all()
    brands = sorted(list(set(s.brand for s in all_sneakers)))
    conditions = sorted(list(set(s.condition for s in all_sneakers)))
    
    # Get sold sneaker IDs for template
    sold_sneaker_ids = [s.sneaker_id for s in Sale.query.all()]
    
    return render_template('inventory.html', 
                         sneakers=filtered_sneakers,
                         brands=brands,
                         conditions=conditions,
                         search=search,
                         condition_filter=condition_filter,
                         brand_filter=brand_filter,
                         sold_sneaker_ids=sold_sneaker_ids,
                         view=view)

@app.route('/add_sneaker', methods=['GET', 'POST'])
def add_sneaker():
    """Add a new sneaker to inventory"""
    form = SneakerForm()
    
    if form.validate_on_submit():
        try:
            sneaker = Sneaker(
                sku=form.sku.data,
                brand=form.brand.data,
                model=form.model.data,
                size=form.size.data,
                category=form.category.data,
                colorway=form.colorway.data,
                retail_price=float(form.retail_price.data) if form.retail_price.data else None,
                release_date=form.release_date.data.isoformat() if form.release_date.data else None,
                purchase_price=float(form.purchase_price.data),
                purchase_date=form.purchase_date.data.isoformat(),
                condition=form.condition.data,
                description=form.description.data,
                notes=form.notes.data,
                listing_price=float(form.listing_price.data) if form.listing_price.data else 0.0,
                image_url=request.form.get('image_url')  # Will be populated via API lookup
            )
            
            db.session.add(sneaker)
            db.session.commit()
            
            flash('Sneaker added successfully!', 'success')
            return redirect(url_for('inventory'))
            
        except ValueError as e:
            flash(f'Error adding sneaker: {str(e)}', 'error')
            db.session.rollback()
        except Exception as e:
            logging.error(f"Error adding sneaker: {str(e)}")
            flash('An error occurred while adding the sneaker.', 'error')
            db.session.rollback()
    
    return render_template('add_sneaker.html', form=form)

@app.route('/edit_sneaker/<int:sneaker_id>', methods=['GET', 'POST'])
def edit_sneaker(sneaker_id):
    """Edit an existing sneaker"""
    sneaker = Sneaker.query.get_or_404(sneaker_id)
    
    form = SneakerForm()
    
    if form.validate_on_submit():
        try:
            sneaker.sku = form.sku.data
            sneaker.brand = form.brand.data
            sneaker.model = form.model.data
            sneaker.size = form.size.data
            sneaker.category = form.category.data
            sneaker.colorway = form.colorway.data
            sneaker.retail_price = float(form.retail_price.data) if form.retail_price.data else None
            sneaker.release_date = form.release_date.data.isoformat() if form.release_date.data else None
            sneaker.purchase_price = float(form.purchase_price.data)
            sneaker.purchase_date = form.purchase_date.data.isoformat()
            sneaker.condition = form.condition.data
            sneaker.description = form.description.data
            sneaker.notes = form.notes.data
            sneaker.listing_price = float(form.listing_price.data) if form.listing_price.data else 0.0
            sneaker.image_url = request.form.get('image_url') or sneaker.image_url
            
            db.session.commit()
            flash('Sneaker updated successfully!', 'success')
            return redirect(url_for('inventory'))
            
        except ValueError as e:
            flash(f'Error updating sneaker: {str(e)}', 'error')
            db.session.rollback()
        except Exception as e:
            logging.error(f"Error updating sneaker: {str(e)}")
            flash('An error occurred while updating the sneaker.', 'error')
            db.session.rollback()
    else:
        # Pre-populate form with existing data
        from datetime import datetime
        if sneaker.purchase_date:
            try:
                purchase_date = datetime.fromisoformat(sneaker.purchase_date.replace('Z', '+00:00'))
                form.purchase_date.data = purchase_date.date()
            except:
                pass
        form.sku.data = sneaker.sku
        form.brand.data = sneaker.brand
        form.model.data = sneaker.model
        form.size.data = sneaker.size
        form.category.data = sneaker.category if hasattr(sneaker, 'category') and sneaker.category else "Men's"
        form.colorway.data = sneaker.colorway
        form.retail_price.data = float(sneaker.retail_price) if sneaker.retail_price else None
        if sneaker.release_date:
            try:
                release_date = datetime.fromisoformat(sneaker.release_date.replace('Z', '+00:00'))
                form.release_date.data = release_date.date()
            except:
                form.release_date.data = None
        else:
            form.release_date.data = None
        form.purchase_price.data = float(sneaker.purchase_price)
        form.condition.data = sneaker.condition
        form.description.data = sneaker.description
        form.notes.data = sneaker.notes
        form.listing_price.data = float(sneaker.listing_price)
    
    # Check if sneaker is sold
    is_sold = Sale.query.filter_by(sneaker_id=sneaker.id).first() is not None
    return render_template('edit_sneaker.html', form=form, sneaker=sneaker, is_sold=is_sold)

@app.route('/duplicate_sneaker/<int:sneaker_id>')
def duplicate_sneaker(sneaker_id):
    """Duplicate an existing sneaker"""
    original = Sneaker.query.get_or_404(sneaker_id)
    
    try:
        # Add import at the top if needed
        from datetime import datetime
        
        duplicate = Sneaker(
            sku=f"{original.sku}-COPY" if original.sku else None,
            brand=original.brand,
            model=original.model,
            size=original.size,
            category=original.category if hasattr(original, 'category') and original.category else "Men's",
            colorway=original.colorway,
            retail_price=original.retail_price if hasattr(original, 'retail_price') else None,
            release_date=original.release_date if hasattr(original, 'release_date') else None,
            purchase_price=original.purchase_price,
            purchase_date=datetime.now().isoformat(),
            condition=original.condition,
            notes=original.notes if original.notes else "",
            listing_price=original.listing_price
        )
        
        db.session.add(duplicate)
        db.session.commit()
        
        flash('Sneaker duplicated successfully!', 'success')
        return redirect(url_for('edit_sneaker', sneaker_id=duplicate.id))
        
    except Exception as e:
        logging.error(f"Error duplicating sneaker: {str(e)}")
        flash('An error occurred while duplicating the sneaker.', 'error')
        db.session.rollback()
        return redirect(url_for('inventory'))

@app.route('/view_sneaker/<int:sneaker_id>')
def view_sneaker(sneaker_id):
    """View detailed information about a specific sneaker"""
    sneaker = Sneaker.query.get_or_404(sneaker_id)
    
    # Check if sneaker is sold
    is_sold = bool(sneaker.sales)
    sale_record = sneaker.sales[0] if sneaker.sales else None
    
    return render_template('view_sneaker.html', 
                         sneaker=sneaker,
                         is_sold=is_sold,
                         sale_record=sale_record)

@app.route('/delete_sneaker/<int:sneaker_id>')
def delete_sneaker(sneaker_id):
    """Delete a sneaker from inventory"""
    sneaker = Sneaker.query.get_or_404(sneaker_id)
    
    try:
        # Delete associated sales first
        if sneaker.sales:
            for sale in sneaker.sales:
                db.session.delete(sale)
        
        # Delete the sneaker
        db.session.delete(sneaker)
        db.session.commit()
        flash('Sneaker and associated sales deleted successfully!', 'success')
    except Exception as e:
        logging.error(f"Error deleting sneaker: {str(e)}")
        flash('An error occurred while deleting the sneaker.', 'error')
        db.session.rollback()
    
    return redirect(url_for('inventory'))

@app.route('/delete_sale/<int:sale_id>')
def delete_sale(sale_id):
    """Delete a sale record"""
    sale = Sale.query.get_or_404(sale_id)
    
    try:
        db.session.delete(sale)
        db.session.commit()
        flash('Sale record deleted successfully! The sneaker is now available again.', 'success')
    except Exception as e:
        logging.error(f"Error deleting sale: {str(e)}")
        flash('An error occurred while deleting the sale record.', 'error')
        db.session.rollback()
    
    return redirect(url_for('sales_list'))

@app.route('/sales')
def sales_list():
    """View all sales"""
    platform_filter = request.args.get('platform', '')
    
    query = Sale.query
    
    if platform_filter:
        query = query.filter(Sale.platform == platform_filter)
    
    filtered_sales = query.order_by(Sale.created_at.desc()).all()
    
    # Get unique platforms for filter
    all_sales = Sale.query.all()
    platforms = sorted(list(set(s.platform for s in all_sales if s.platform)))
    
    # Prepare sales with profit calculation
    sales_with_sneakers = []
    for sale in filtered_sales:
        if sale.sneaker:
            sales_with_sneakers.append({
                'sale': sale,
                'sneaker': sale.sneaker,
                'profit': sale.calculate_profit()
            })
    
    return render_template('sales.html', 
                         sales_with_sneakers=sales_with_sneakers,
                         platforms=platforms,
                         platform_filter=platform_filter)

@app.route('/add_sale', methods=['GET', 'POST'])
def add_sale():
    """Record a new sale"""
    # Get available sneakers (not sold)
    sold_sneaker_ids = [s.sneaker_id for s in Sale.query.all()]
    if sold_sneaker_ids:
        available_sneakers = Sneaker.query.filter(~Sneaker.id.in_(sold_sneaker_ids)).all()
    else:
        available_sneakers = Sneaker.query.all()
    
    if not available_sneakers:
        flash('No available sneakers to sell.', 'error')
        return redirect(url_for('inventory'))
    
    form = SaleForm()
    form.sneaker_id.choices = [(s.id, f"{s.brand} {s.model} - {s.colorway} (Size {s.size})") 
                               for s in available_sneakers]
    
    if form.validate_on_submit():
        try:
            sale = Sale(
                sneaker_id=int(form.sneaker_id.data),
                sale_price=float(form.sale_price.data),
                sale_date=form.sale_date.data.isoformat(),
                buyer_info=form.buyer_info.data,
                platform=form.platform.data,
                tracking_number=form.tracking_number.data,
                fees=float(form.fees.data) if form.fees.data else 0.0,
                shipping_cost=float(form.shipping_cost.data) if form.shipping_cost.data else 0.0
            )
            
            db.session.add(sale)
            db.session.commit()
            
            flash('Sale recorded successfully!', 'success')
            return redirect(url_for('sales_list'))
            
        except ValueError as e:
            flash(f'Error recording sale: {str(e)}', 'error')
            db.session.rollback()
        except Exception as e:
            logging.error(f"Error recording sale: {str(e)}")
            flash('An error occurred while recording the sale.', 'error')
            db.session.rollback()
    
    return render_template('add_sale.html', form=form)

@app.route('/analytics')
def analytics():
    """View analytics and profit tracking"""
    analytics_data = calculate_analytics()
    
    # Prepare data for charts
    monthly_profits = analytics_data.get('monthly_profits', [])
    brand_performance = analytics_data.get('brand_performance', [])
    
    return render_template('analytics.html', 
                         analytics=analytics_data,
                         monthly_profits=monthly_profits,
                         brand_performance=brand_performance)


@app.route('/api/analytics')
def api_analytics():
    """API endpoint for analytics data"""
    analytics_data = calculate_analytics()
    return jsonify(analytics_data)

@app.route('/api/lookup-sku', methods=['POST'])
def lookup_sku():
    """API endpoint to lookup sneaker data by SKU using The Sneaker Database"""
    try:
        data = request.get_json()
        sku = data.get('sku', '').strip()
        
        if not sku:
            return jsonify({'error': 'SKU is required'}), 400
        
        # Lookup sneaker data from The Sneaker Database API
        sneaker_data = sneaker_db_api.lookup_by_sku(sku)
        
        if sneaker_data:
            # Format the response for the frontend
            response = {
                'success': True,
                'data': {
                    'brand': sneaker_data.get('brand', ''),
                    'model': sneaker_data.get('model', ''),
                    'colorway': sneaker_data.get('colorway', ''),
                    'retail_price': sneaker_data.get('retail_price'),
                    'release_date': sneaker_data.get('release_date'),
                    'image_url': sneaker_data.get('image_url'),
                    'category': sneaker_data.get('category', "Men's"),
                    'description': sneaker_data.get('description', ''),
                    'estimated_market_value': sneaker_data.get('estimated_market_value')
                }
            }
            return jsonify(response)
        else:
            return jsonify({
                'success': False,
                'error': 'No sneaker found with that SKU'
            }), 404
            
    except Exception as e:
        logging.error(f"Error in SKU lookup: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'An error occurred while looking up the SKU'
        }), 500

# Listing Management Routes
@app.route('/sneaker/<int:sneaker_id>/listings')
def sneaker_listings(sneaker_id):
    """View all listings for a specific sneaker"""
    sneaker = Sneaker.query.get_or_404(sneaker_id)
    listings = Listing.query.filter_by(sneaker_id=sneaker_id).order_by(Listing.date_listed.desc()).all()
    
    return render_template('sneaker_listings.html', sneaker=sneaker, listings=listings)

@app.route('/sneaker/<int:sneaker_id>/add_listing', methods=['GET', 'POST'])
def add_listing(sneaker_id):
    """Add a new listing for a sneaker"""
    sneaker = Sneaker.query.get_or_404(sneaker_id)
    form = ListingForm()
    
    if form.validate_on_submit():
        try:
            listing = Listing(
                sneaker_id=sneaker_id,
                platform=form.platform.data,
                listing_url=form.listing_url.data,
                listing_price=float(form.listing_price.data),
                listing_status=form.listing_status.data,
                date_listed=form.date_listed.data,
                notes=form.notes.data
            )
            
            db.session.add(listing)
            db.session.commit()
            
            flash(f'Listing added successfully on {form.platform.data}!', 'success')
            return redirect(url_for('sneaker_listings', sneaker_id=sneaker_id))
            
        except Exception as e:
            logging.error(f"Error adding listing: {str(e)}")
            flash('An error occurred while adding the listing.', 'error')
            db.session.rollback()
    
    return render_template('add_listing.html', form=form, sneaker=sneaker)

@app.route('/listing/<int:listing_id>/edit', methods=['GET', 'POST'])
def edit_listing(listing_id):
    """Edit an existing listing"""
    listing = Listing.query.get_or_404(listing_id)
    form = ListingForm()
    
    if form.validate_on_submit():
        try:
            listing.platform = form.platform.data
            listing.listing_url = form.listing_url.data
            listing.listing_price = float(form.listing_price.data)
            listing.listing_status = form.listing_status.data
            listing.date_listed = form.date_listed.data
            listing.notes = form.notes.data
            listing.date_updated = datetime.now().date()
            
            db.session.commit()
            flash('Listing updated successfully!', 'success')
            return redirect(url_for('sneaker_listings', sneaker_id=listing.sneaker_id))
            
        except Exception as e:
            logging.error(f"Error updating listing: {str(e)}")
            flash('An error occurred while updating the listing.', 'error')
            db.session.rollback()
    else:
        # Pre-populate form with existing data
        form.platform.data = listing.platform
        form.listing_url.data = listing.listing_url
        form.listing_price.data = float(listing.listing_price)
        form.listing_status.data = listing.listing_status
        if listing.date_listed:
            form.date_listed.data = listing.date_listed
        form.notes.data = listing.notes
    
    return render_template('edit_listing.html', form=form, listing=listing)

@app.route('/listing/<int:listing_id>/delete')
def delete_listing(listing_id):
    """Delete a listing"""
    listing = Listing.query.get_or_404(listing_id)
    sneaker_id = listing.sneaker_id
    
    try:
        db.session.delete(listing)
        db.session.commit()
        flash('Listing deleted successfully!', 'success')
    except Exception as e:
        logging.error(f"Error deleting listing: {str(e)}")
        flash('An error occurred while deleting the listing.', 'error')
        db.session.rollback()
    
    return redirect(url_for('sneaker_listings', sneaker_id=sneaker_id))

@app.route('/listings')
def all_listings():
    """View all listings across all sneakers"""
    status_filter = request.args.get('status', '')
    platform_filter = request.args.get('platform', '')
    
    query = Listing.query.join(Sneaker)
    
    if status_filter:
        query = query.filter(Listing.listing_status == status_filter)
    
    if platform_filter:
        query = query.filter(Listing.platform == platform_filter)
    
    listings = query.order_by(Listing.date_listed.desc()).all()
    
    # Get unique platforms and statuses for filters
    all_listings_query = Listing.query.all()
    platforms = sorted(list(set(l.platform for l in all_listings_query)))
    statuses = sorted(list(set(l.listing_status for l in all_listings_query)))
    
    return render_template('all_listings.html', 
                         listings=listings,
                         platforms=platforms,
                         statuses=statuses,
                         status_filter=status_filter,
                         platform_filter=platform_filter)

# Real-time Pricing API Routes
@app.route('/api/pricing/lookup', methods=['POST'])
def get_realtime_pricing():
    """
    API endpoint to get real-time pricing data for a sneaker
    """
    try:
        data = request.get_json()
        
        # Extract sneaker details from request
        brand = data.get('brand', '').strip()
        model = data.get('model', '').strip()
        colorway = data.get('colorway', '').strip()
        sku = data.get('sku', '').strip()
        size = data.get('size', '').strip()
        
        if not brand or not model:
            return jsonify({
                'success': False,
                'error': 'Brand and model are required'
            }), 400
        
        # Get pricing data from multiple sources
        pricing_data = realtime_pricing_api.get_sneaker_prices(
            brand=brand,
            model=model,
            colorway=colorway if colorway else None,
            sku=sku if sku else None,
            size=size if size else None
        )
        
        if pricing_data:
            return jsonify({
                'success': True,
                'data': pricing_data
            })
        else:
            return jsonify({
                'success': False,
                'error': 'No pricing data found for this sneaker'
            }), 404
            
    except Exception as e:
        logging.error(f"Error in pricing lookup: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'An error occurred while fetching pricing data'
        }), 500

@app.route('/api/pricing/search', methods=['POST'])
def search_sneaker_prices():
    """
    API endpoint to search for sneakers by query and get pricing
    """
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        
        if not query:
            return jsonify({
                'success': False,
                'error': 'Search query is required'
            }), 400
        
        # Search for sneakers with pricing
        results = realtime_pricing_api.search_sneakers_by_query(query, limit=5)
        
        if results:
            return jsonify({
                'success': True,
                'data': results
            })
        else:
            return jsonify({
                'success': False,
                'error': 'No sneakers found matching your search'
            }), 404
            
    except Exception as e:
        logging.error(f"Error in pricing search: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'An error occurred while searching for sneakers'
        }), 500



