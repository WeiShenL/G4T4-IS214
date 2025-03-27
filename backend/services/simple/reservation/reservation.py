from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

app = Flask(__name__)

CORS(app, resources={r"/*": {"origins": "*"}})

supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_KEY')
supabase: Client = create_client(supabase_url, supabase_key)

# retrieve all reservations (not in use?)
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

# retrieve reservation using id
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

# create a new reservation  (yet to implement)
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

app = Flask(__name__)

CORS(app, resources={r"/*": {"origins": "*"}})

supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_KEY')
supabase: Client = create_client(supabase_url, supabase_key)

# retrieve all reservations
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

# retrieve reservation using id
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

# create a new reservation
@app.route("/api/reservations", methods=['POST'])
def create_reservation():
    try:
        data = request.json
        required_fields = ['restaurant_id', 'user_id', 'count', 'status']
        
        for field in required_fields:
            if field not in data:
                return jsonify({
                    "code": 400,
                    "message": f"Missing required field: {field}"
                }), 400
        
        # create a new reservation
        new_reservation = {
            "restaurant_id": data['restaurant_id'],
            "user_id": data['user_id'],
            "table_no": data.get('table_no'),  
            "status": data['status'],
            "count": data['count'],
            "price": data.get('price', 0),
            "time": data.get('time', datetime.now().isoformat())
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

# get reservations by user_id
@app.route("/api/reservations/user/<string:user_id>", methods=['GET'])
def get_user_reservations(user_id):
    try:
        # supabase uuid
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

        
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)