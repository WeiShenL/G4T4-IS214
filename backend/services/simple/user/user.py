from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Supabase configuration
supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_KEY')
supabase: Client = create_client(supabase_url, supabase_key)

# Get user details by user_id
@app.route("/api/user/<string:user_id>", methods=['GET'])
def get_user(user_id):
    try:
        response = supabase.table('customer_profiles').select('*').eq('id', user_id).execute()
        
        if not response.data:
            return jsonify({
                "code": 404,
                "message": f"User not found with ID: {user_id}"
            }), 404
            
        return jsonify({
            "code": 200,
            "data": response.data[0]
        })
    except Exception as e:
        return jsonify({
            "code": 500,
            "message": f"An error occurred: {str(e)}"
        }), 500

if __name__ == '__main__':
    print("Starting user service...")
    app.run(host='0.0.0.0', port=5000, debug=True)  # Using port 5000