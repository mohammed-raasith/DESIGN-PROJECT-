from datetime import datetime
from app import db

class Stock(db.Model):
    __tablename__ = 'stock_table'
    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(100), nullable=False)
    current_stock = db.Column(db.Integer, default=0)
    lead_time = db.Column(db.Integer, default=1) # in days
    safety_stock = db.Column(db.Integer, default=0)
    expiry_date = db.Column(db.Date, nullable=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey('supplier_table.supplier_id'), nullable=True)
    
    # Relationship
    supplier = db.relationship('Supplier', backref='items')

class Sales(db.Model):
    __tablename__ = 'sales_table'
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('stock_table.id'), nullable=False)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    quantity_sold = db.Column(db.Integer, nullable=False)
    
    # Relationship
    item = db.relationship('Stock', backref='sales_records')

class Supplier(db.Model):
    __tablename__ = 'supplier_table'
    supplier_id = db.Column(db.Integer, primary_key=True)
    supplier_name = db.Column(db.String(100), nullable=False)
    average_lead_time = db.Column(db.Float, default=1.0)
    delay_count = db.Column(db.Integer, default=0)
    total_orders = db.Column(db.Integer, default=0) # For reliability score

class Alert(db.Model):
    __tablename__ = 'alerts_table'
    id = db.Column(db.Integer, primary_key=True)
    alert_type = db.Column(db.String(50), nullable=False) # e.g. Low Stock, Expiry
    item_id = db.Column(db.Integer, db.ForeignKey('stock_table.id'), nullable=True)
    severity = db.Column(db.String(20), nullable=False) # GREEN, ORANGE, RED
    message = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    item = db.relationship('Stock', backref='alerts')

class PurchaseOrder(db.Model):
    __tablename__ = 'purchase_orders'
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('stock_table.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    supplier_id = db.Column(db.Integer, db.ForeignKey('supplier_table.supplier_id'), nullable=True)
    status = db.Column(db.String(50), default='Pending') # Pending, Approved, Completed
    order_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    item = db.relationship('Stock', backref='purchase_orders')
    supplier = db.relationship('Supplier', backref='purchase_orders')
