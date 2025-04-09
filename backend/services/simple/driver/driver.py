from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Supabase configuration
supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_KEY')
supabase: Client = create_client(supabase_url, supabase_key)

# Get driver by ID
@app.route("/driver/<string:driver_id>", methods=['GET'])
def get_driver(driver_id):
    try:
        # Query the driver_profiles table using the provided driver_id
        response = supabase.table('driver_profiles').select('*').eq('id', driver_id).execute()
        
        # Check if any data was returned
        if not response.data:
            return jsonify({
                "code": 404,
                "message": f"Driver not found with ID: {driver_id}"
            }), 404
        
        # Return the driver's profile
        return jsonify({
            "code": 200,
            "data": response.data[0]
        })
    
    except Exception as e:
        # Handle any errors that occur during the query
        return jsonify({
            "code": 500,
            "message": f"An error occurred: {str(e)}"
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5011))
    print(f"Starting driver service on port {port}...")
    app.run(host='0.0.0.0', port=port, debug=True)