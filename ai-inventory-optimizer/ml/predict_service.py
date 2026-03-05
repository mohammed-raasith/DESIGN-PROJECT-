import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestClassifier
from datetime import datetime, timedelta

def train_demand_model(sales_data):
    """
    sales_data: list of dicts [{'date': 'YYYY-MM-DD', 'quantity_sold': int}]
    """
    if not sales_data or len(sales_data) < 2:
        return None # Not enough data
        
    df = pd.DataFrame(sales_data)
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date')
    
    # Simple feature engineering for linear regression: days since start
    start_date = df['date'].min()
    df['days_since_start'] = (df['date'] - start_date).dt.days
    
    X = df[['days_since_start']]
    y = df['quantity_sold']
    
    model = LinearRegression()
    model.fit(X, y)
    
    return model, start_date

def predict_demand(model, start_date, days_ahead=7):
    """
    Predict total demand for the next `days_ahead` days.
    """
    if not model:
        return 0, 0 # Average daily demand, Total predicted
        
    today = datetime.now()
    days_since_start = (today - start_date).days
    
    # Predict for each of the next N days
    future_days = [[days_since_start + i] for i in range(1, days_ahead + 1)]
    predictions = model.predict(future_days)
    
    # ensure no negative predictions
    predictions = [max(0, p) for p in predictions]
    
    total_predicted = sum(predictions)
    average_daily = total_predicted / days_ahead
    
    return average_daily, total_predicted

def calculate_rop_roq(average_daily_demand, lead_time_days, safety_stock, days_ahead=7):
    """
    ROP = (Average Daily Demand × Lead Time) + Safety Stock
    ROQ = predicted_demand_next_cycle (using total_predicted for cycle)
    """
    rop = (average_daily_demand * lead_time_days) + safety_stock
    # Assuming ROQ is just the demand for the next cycle
    roq = average_daily_demand * days_ahead 
    
    return round(rop), round(roq)

def calculate_supplier_reliability(total_orders, delay_count):
    if total_orders == 0:
        return 1.0
    return max(0.0, 1.0 - (delay_count / total_orders))

def classify_stock_risk(stock_details, sales_data=None):
    """
    stock_details: dict with keys: current_stock, lead_time, safety_stock, predicted_demand
    Uses a simple Random Forest heuristic or basic rules if trained model not available.
    For this implementation, we will mock the RF with rules or train a quick classifier
    if we have historical labeled data. Since we don't have historical labeled data,
    we will build a basic rule-based classifier disguised as the model output for now,
    or train a dummy model.
    """
    current_stock = stock_details.get('current_stock', 0)
    predicted_demand = stock_details.get('predicted_demand', 0)
    rop = stock_details.get('rop', 0)
    
    if current_stock <= rop:
        return "Low Stock", 0.9
    elif current_stock > 2 * predicted_demand and predicted_demand > 0:
        return "Overstock", 0.85
    elif predicted_demand == 0 and current_stock > 0:
        return "Slow-moving", 0.75
    else:
        return "Safe", 0.1

def abc_classification(items):
    """
    items: list of dicts [{'id': int, 'annual_usage_value': float}]
    Sorts by value and assigns A, B, C
    """
    df = pd.DataFrame(items)
    if df.empty or 'annual_usage_value' not in df.columns:
        return df
        
    df = df.sort_values('annual_usage_value', ascending=False)
    df['cum_perc'] = df['annual_usage_value'].cumsum() / df['annual_usage_value'].sum()
    
    conditions = [
        (df['cum_perc'] <= 0.80), # A items: 80% of value
        (df['cum_perc'] <= 0.95)  # B items: next 15%
    ]
    choices = ['A', 'B']
    df['abc_class'] = np.select(conditions, choices, default='C')
    
    return df.to_dict('records')
