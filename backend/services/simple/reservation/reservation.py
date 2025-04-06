<<<<<<< Updated upstream
#TODO: remove reallocation patch method
#TODO: count total reservations for that particular restaurant

=======
>>>>>>> Stashed changes
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client, Client
import random

load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_KEY')
supabase: Client = create_client(supabase_url, supabase_key)

# Retrieve all reservations (not in use?)
@app.route("/api/reservations", methods=['GET'])
def get_all_reservations():
    try:
        response = supabase.table('reservation').select('*').execute()
        reservation_list = response.data
        
        if reservation_list:
            return jsonify({
                "code": 200,
                "data": {
                    "reservations": reservation_list
                }
            })
        return jsonify({
            "code": 404,
            "message": "No reservations found."
        }), 404
    except Exception as e:
        return jsonify({
            "code": 500,
            "message": f"An error occurred: {str(e)}"
        }), 500

# Retrieve reservation using id
@app.route("/api/reservations/<int:reservation_id>", methods=['GET'])
def get_reservation(reservation_id):
    try:
        response = supabase.table('reservation').select('*').eq('reservation_id', reservation_id).execute()
        reservation = response.data[0] if response.data else None
        
        if reservation:
            return jsonify({
                "code": 200,
                "data": reservation
            })
        return jsonify({
            "code": 404,
            "message": "Reservation not found."
        }), 404
    except Exception as e:
        return jsonify({
            "code": 500,
            "message": f"An error occurred: {str(e)}"
        }), 500

# Create a new reservation
@app.route("/api/reservations", methods=['POST'])
def create_reservation():
    try:
        data = request.json
        required_fields = ['restaurant_id', 'user_id', 'count', 'status', 'time']
        
        for field in required_fields:
            if field not in data:
                return jsonify({
                    "code": 400,
                    "message": f"Missing required field: {field}"
                }), 400
                
        # Auto-assign table number if not provided
        table_no = data.get('table_no')
        if table_no is None:
            # Assign a random table between 1-50
            table_no = random.randint(1, 50)
        
        # Create a new reservation
        new_reservation = {
            "restaurant_id": data['restaurant_id'],
            "user_id": data['user_id'],
            "table_no": table_no,  
            "status": data['status'],
            "count": data['count'],
            "price": data.get('price', 0),
            "time": data.get('time', datetime.now().isoformat()),
            "order_id": data.get('order_id'),
            "payment_id": data.get('payment_id') 
        }
        
        response = supabase.table('reservation').insert(new_reservation).execute()
        
        if response.data:
            return jsonify({
                "code": 201,
                "message": "Reservation created successfully",
                "data": response.data[0]
            }), 201
        else:
            return jsonify({
                "code": 500,
                "message": "Failed to create reservation"
            }), 500
    
    except Exception as e:
        return jsonify({
            "code": 500,
            "message": f"An error occurred: {str(e)}"
        }), 500

# Get reservations by user_id
@app.route("/api/reservations/user/<string:user_id>", methods=['GET'])
def get_user_reservations(user_id):
    try:
        response = supabase.table('reservation').select('*').eq('user_id', user_id).execute()
        reservations = response.data
        
        if reservations:
            return jsonify({
                "code": 200,
                "data": {
                    "reservations": reservations
                }
            })
        return jsonify({
            "code": 404,
            "message": f"No reservations found for user: {user_id}"
        }), 404
    except Exception as e:
        return jsonify({
            "code": 500,
            "message": f"An error occurred: {str(e)}"
        }), 500

<<<<<<< Updated upstream
@app.route('/api/reservation/cancel/<int:reservation_id>', methods=['PATCH'])
def cancel_reservation(reservation_id):
=======
# Delete reservation row when cancellation
@app.route('/api/reservation/cancel/<int:reservation_id>', methods=['DELETE'])
def delete_reservation(reservation_id):
>>>>>>> Stashed changes
    try:
        # Fetch the existing reservation
        response = supabase.table('reservation').select('*').eq('reservation_id', reservation_id).execute()
        
        if not response.data:
            return jsonify({"error": "Reservation not found"}), 404
        
        reservation = response.data[0]
        
        # Store important data before updating
        refund_amount = reservation.get('price', 0)
        table_no = reservation.get('table_no')
        user_id = reservation.get('user_id')
        payment_id = reservation.get('payment_id')
        order_id = reservation.get('order_id')  # Make sure to include order_id

        
        # Prepare update data to clear the reservation
        update_data = {
            "user_id": None,
            "status": "empty",
            "count": None,
            "price": None,
            "time": None,
            "order_id": None,
            "payment_id": None  
        }
        
        # Update the reservation
        update_response = supabase.table('reservation').update(update_data).eq('reservation_id', reservation_id).execute()
        
        if not update_response.data:
            return jsonify({"error": "Failed to update reservation"}), 500
        
        return jsonify({
            "reservation_id": reservation_id,
            "user_id": user_id,
            "table_no": table_no,
            "refund_amount": refund_amount,
            "payment_id": payment_id,
            "order_id": order_id  

        }), 200
    
    except Exception as e:
        return jsonify({
            "error": f"An error occurred: {str(e)}"
        }), 500

<<<<<<< Updated upstream
# ks method
@app.route('/reservation/reallocate/<int:reservation_id>', methods=['PATCH'])
def update_reservation(reservation_id):
=======
# Confirm booking (new route for accept_booking.py)
@app.route('/reservation/reallocate_confirm_booking/<int:reservation_id>', methods=['PATCH'])
def reallocate_confirm_booking(reservation_id):
>>>>>>> Stashed changes
    try:
        data = request.get_json()

        # Validate required fields
        required_fields = ["new_reservation_id", "status", "count", "price", "order_id", "payment_id"]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400

        # Prepare update data
        update_data = {
            "reservation_id": data["new_reservation_id"],  # Update with the new reservation ID
            "status": data["status"],
            "count": data["count"],
            "price": data["price"],
            "order_id": data["order_id"],
            "payment_id": data["payment_id"]
        }

        # Fetch the existing reservation to ensure it exists
        existing_response = supabase.table('reservation').select('*').eq('reservation_id', reservation_id).execute()

        if not existing_response.data:
            return jsonify({"error": "Reservation not found"}), 404

        # Perform the update using the old reservation ID
        update_response = supabase.table('reservation').update(update_data).eq('reservation_id', reservation_id).execute()

        if not update_response.data:
            return jsonify({"error": "Failed to update reservation"}), 500

        # Fetch the updated reservation to return
        updated_response = supabase.table('reservation').select('*').eq('reservation_id', data["new_reservation_id"]).execute()

        return jsonify({
            "reservation_id": updated_response.data[0].get("reservation_id"),
            "user_id": updated_response.data[0].get("user_id"),
            "table_no": updated_response.data[0].get("table_no"),
            "status": updated_response.data[0].get("status"),
            "count": updated_response.data[0].get("count"),
            "price": updated_response.data[0].get("price"),
            "order_id": updated_response.data[0].get("order_id"),
            "payment_id": updated_response.data[0].get("payment_id")
        }), 200

    except Exception as e:
        return jsonify({
            "code": 500,
            "error": f"An error occurred: {str(e)}"
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)