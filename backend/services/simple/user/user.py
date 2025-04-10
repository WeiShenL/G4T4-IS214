from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
from supabase import create_client, Client
from datetime import datetime

load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Database connection
supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_KEY')
supabase: Client = create_client(supabase_url, supabase_key)

@app.route("/api/user/health", methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy",
        "service": "user-service",
        "timestamp": datetime.now().isoformat()
    }), 200
    
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
    port = int(os.environ.get('PORT', 5000))
    print(f"Starting user service on port {port}...")
    app.run(host='0.0.0.0', port=port, debug=True)