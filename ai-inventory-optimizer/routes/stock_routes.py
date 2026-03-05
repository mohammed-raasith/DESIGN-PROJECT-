from flask import Blueprint, render_template, request, jsonify
from app import db
from db.models import Stock, Sales, Supplier, Alert
from ml.predict_service import train_demand_model, predict_demand, calculate_rop_roq
from datetime import datetime

stock_bp = Blueprint('stock', __name__)

@stock_bp.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@stock_bp.route('/stock')
def stock_view():
    return render_template('stock.html')

@stock_bp.route('/predictions')
def predictions_view():
    return render_template('predictions.html')

@stock_bp.route('/expiry')
def expiry_view():
    return render_template('expiry.html')

@stock_bp.route('/suppliers')
def suppliers_view():
    return render_template('suppliers.html')

# API Routes
@stock_bp.route('/api/stock/update', methods=['POST'])
def update_stock():
    data = request.json
    try:
        item = Stock.query.filter_by(item_name=data['item_name']).first()
        if not item:
            item = Stock(
                item_name=data['item_name'],
                current_stock=data.get('current_stock', 0),
                lead_time=data.get('lead_time', 1),
                safety_stock=data.get('safety_stock', 0)
            )
            if 'expiry_date' in data and data['expiry_date']:
                item.expiry_date = datetime.strptime(data['expiry_date'], '%Y-%m-%d').date()
            db.session.add(item)
        else:
            item.current_stock = data.get('current_stock', item.current_stock)
            # update other fields as necessary
            
        db.session.commit()
        return jsonify({'message': 'Stock updated successfully', 'id': item.id}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@stock_bp.route('/api/sales/upload', methods=['POST'])
def upload_sales():
    data = request.json # Expecting a list of sales records
    try:
        for record in data:
            sale = Sales(
                item_id=record['item_id'],
                date=datetime.strptime(record['date'], '%Y-%m-%d').date(),
                quantity_sold=record['quantity_sold']
            )
            db.session.add(sale)
        db.session.commit()
        return jsonify({'message': 'Sales data uploaded successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@stock_bp.route('/api/predict/<int:item_id>', methods=['GET'])
def get_prediction(item_id):
    # Fetch sales data for the item
    sales = Sales.query.filter_by(item_id=item_id).all()
    sales_data = [{'date': s.date, 'quantity_sold': s.quantity_sold} for s in sales]
    
    if len(sales_data) < 2:
        return jsonify({'error': 'Not enough data to predict'}), 400
        
    model, start_date = train_demand_model(sales_data)
    average_daily, total_predicted = predict_demand(model, start_date, days_ahead=7)
    
    item = Stock.query.get(item_id)
    rop, roq = calculate_rop_roq(average_daily, item.lead_time, item.safety_stock, days_ahead=7)
    
    return jsonify({
        'item_id': item_id,
        'predicted_demand_next_7_days': round(total_predicted, 2),
        'average_daily_demand': round(average_daily, 2),
        'recommended_rop': rop,
        'recommended_roq': roq
    }), 200
