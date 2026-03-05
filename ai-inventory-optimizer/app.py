import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    CORS(app)
    
    # Configure Database
    basedir = os.path.abspath(os.path.dirname(__name__))
    db_path = os.path.join(basedir, 'db')
    os.makedirs(db_path, exist_ok=True)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(db_path, 'inventory.db')}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    
    with app.app_context():
        # Import models here to ensure they are registered with SQLAlchemy
        from db import models
        db.create_all()
        
    # Register Blueprints
    from routes.stock_routes import stock_bp
    from routes.alert_routes import alert_bp
    app.register_blueprint(stock_bp)
    app.register_blueprint(alert_bp)
    
    @app.route('/')
    def index():
        return "Next-Gen Automated Material Inventory Optimization System is running."
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)
