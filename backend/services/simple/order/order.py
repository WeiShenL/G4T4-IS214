from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
import json
from supabase import create_client, Client
from datetime import datetime

load_dotenv()

app = Flask(__name__)

CORS(app, resources={r"/*": {"origins": "*"}})

# supabase api
supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_KEY')
supabase: Client = create_client(supabase_url, supabase_key)

# create a new order with Stripe payment ID
@app.route("/api/orders", methods=['POST'])
def create_order():
    try:
        data = request.json
        required_fields = ['user_id', 'restaurant_id', 'item_name', 'quantity', 'order_price', 'payment_id']
        
        for field in required_fields:
            if field not in data:
                return jsonify({
                    "code": 400,
                    "message": f"Missing required field: {field}"
                }), 400
        
        # Insert order into the database
        new_order = {
            "user_id": data['user_id'],
            "restaurant_id": data['restaurant_id'],
            "item_name": data['item_name'],
            "quantity": data['quantity'],
            "order_price": data['order_price'],
            "payment_id": data['payment_id'],
            "created_at": datetime.now().isoformat(),
            "order_type": data.get('order_type') 
        }
        
        response = supabase.table('orders').insert(new_order).execute()
        
        if response.data:
            return jsonify({
                "code": 201,
                "message": "Order created successfully",
                "data": response.data[0]
            }), 201
        else:
            return jsonify({
                "code": 500,
                "message": "Failed to create order"
            }), 500
    
    except Exception as e:
        return jsonify({
            "code": 500,
            "message": f"An error occurred: {str(e)}"
        }), 500

# get all orders for a specific user (not used for now) --> order history page? idk
@app.route("/api/orders/user/<string:user_id>", methods=['GET'])
def get_user_orders(user_id):
    try:
        response = supabase.table('orders').select('*').eq('user_id', user_id).order('created_at', desc=True).execute()
        orders = response.data
        
        if orders:
            return jsonify({
                "code": 200,
                "data": {
                    "orders": orders
                }
            })
        return jsonify({
            "code": 404,
            "message": f"No orders found for user: {user_id}"
        }), 404
    except Exception as e:
        return jsonify({
            "code": 500,
            "message": f"An error occurred: {str(e)}"
        }), 500

# Delete an order by payment_id
@app.route("/api/orders/payment/<string:payment_id>", methods=['DELETE'])
def delete_order_by_payment(payment_id):
    try:
        if not payment_id:
            return jsonify({
                "code": 400,
                "message": "Payment ID is required"
            }), 400
            
        # Delete the order with the given payment_id
        delete_response = supabase.table('orders').delete().eq('payment_id', payment_id).execute()
        
        if delete_response.data:
            return jsonify({
                "code": 200,
                "message": f"Order with payment_id {payment_id} deleted successfully"
            })
        else:
            return jsonify({
                "code": 404,
                "message": f"No order found with payment_id: {payment_id}"
            }), 404
            
    except Exception as e:
        return jsonify({
            "code": 500,
            "message": f"An error occurred: {str(e)}"
        }), 500

if __name__ == '__main__':
    print(f"Starting order service on port 5004")
    app.run(host='0.0.0.0', port=5004, debug=True)