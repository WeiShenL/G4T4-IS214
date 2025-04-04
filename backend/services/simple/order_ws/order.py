from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
import stripe
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

# stripe api
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
print(f"Stripe API configured with key: {stripe.api_key[:5]}...")
webhook_secret = os.getenv('STRIPE_WEBHOOK_SECRET')
print(f"Webhook secret configured: {webhook_secret[:5]}...")

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

# STRIPE INTEGRATION - Process a refund
@app.route("/api/stripe/refund", methods=['POST'])
def process_refund():
    try:
        data = request.json
        payment_id = data.get('payment_id')
        amount = data.get('amount')  # Optional, if not provided will refund full amount
        
        if not payment_id:
            return jsonify({
                "code": 400,
                "message": "Payment ID is required"
            }), 400
        
        # Process the refund through Stripe
        refund_params = {
            "payment_intent": payment_id,
        }
        
        # Add amount if provided
        if amount:
            refund_params["amount"] = int(amount)
        
        print(f"Processing refund for payment intent: {payment_id}")
        
        refund = stripe.Refund.create(**refund_params)
        
        print(f"Refund processed: {refund.id}")
        
         # refund is successful, delete the associated order
        try:
            # delete the order with the given payment_id
            delete_response = supabase.table('orders').delete().eq('payment_id', payment_id).execute()
            
            if delete_response.data:
                print(f"Order with payment_id {payment_id} deleted successfully")
            else:
                print(f"No order found with payment_id: {payment_id}")
        except Exception as delete_error:
            print(f"Error deleting order: {str(delete_error)}")
        
        return jsonify({
            "code": 200,
            "refund": {
                "id": refund.id,
                "amount": refund.amount,
                "status": refund.status
            }
        })
    
    except Exception as e:
        print(f"Error processing refund: {str(e)}")
        return jsonify({
            "code": 500,
            "message": f"An error occurred: {str(e)}"
        }), 500

# STRIPE INTEGRATION - Create a checkout session
@app.route("/api/stripe/create-checkout-session", methods=['POST'])
def create_checkout_session():
    try:
        data = request.json
        
        # Extract order details
        order_details = data.get('orderDetails')
        customer_id = data.get('customerId')
        success_url = data.get('successUrl')
        cancel_url = data.get('cancelUrl')
        
        # Validate required parameters
        if not all([order_details, customer_id, success_url, cancel_url]):
            return jsonify({
                "code": 400,
                "message": "Missing required parameters"
            }), 400
        
        # Format line items for Stripe
        line_items = [{
            'price_data': {
                'currency': order_details.get('currency', 'usd'),
                'product_data': {
                    'name': order_details.get('itemName', 'Food Order'),
                    'description': f"From {order_details.get('restaurantName', 'Restaurant')}",
                },
                'unit_amount': int(order_details.get('amount') / order_details.get('quantity')),  # in cents
            },
            'quantity': order_details.get('quantity', 1),
        }]
        
        # Add metadata to the session
        metadata = {
            'restaurantId': str(order_details.get('restaurantId')),
            'restaurantName': order_details.get('restaurantName'),
            'userId': customer_id
        }
        
        print(f"Creating Stripe checkout session with line items: {line_items}")
        
        # Create Stripe checkout session
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=line_items,
            mode='payment',
            success_url=success_url,
            cancel_url=cancel_url,
            metadata=metadata
        )
        
        print(f"Checkout session created: {session.id}")
        
        return jsonify({
            "code": 200,
            "sessionId": session.id,
            "url": session.url
        })
    
    except Exception as e:
        print(f"Error creating checkout session: {str(e)}")
        return jsonify({
            "code": 500,
            "message": f"An error occurred: {str(e)}"
        }), 500

# STRIPE INTEGRATION - Verify payment
@app.route("/api/stripe/verify-payment/<string:session_id>", methods=['GET'])
def verify_payment(session_id):
    try:
        print(f"Verifying payment for session: {session_id}")
        
        # Retrieve the session
        session = stripe.checkout.Session.retrieve(session_id)
        
        # Check if payment was successful
        if session.payment_status != 'paid':
            return jsonify({
                "code": 400,
                "message": "Payment not completed"
            }), 400
        
        # Get the payment intent
        payment_intent = stripe.PaymentIntent.retrieve(session.payment_intent)
        
        print(f"Payment verified: {payment_intent.id} with status {payment_intent.status}")
        
        return jsonify({
            "code": 200,
            "paymentIntent": {
                "id": payment_intent.id,
                "status": payment_intent.status,
                "amount": payment_intent.amount
            }
        })
    
    except Exception as e:
        print(f"Error verifying payment: {str(e)}")
        return jsonify({
            "code": 500,
            "message": f"An error occurred: {str(e)}"
        }), 500

if __name__ == '__main__':
    print(f"Starting order service on port 5004")
    app.run(host='0.0.0.0', port=5004, debug=True)