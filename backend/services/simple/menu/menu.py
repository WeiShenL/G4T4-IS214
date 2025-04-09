from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

app = Flask(__name__)

CORS(app, resources={r"/*": {"origins": "*"}})

# Database connection
supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_KEY')
supabase: Client = create_client(supabase_url, supabase_key)

# retrieve menu items for a specific restaurant
@app.route("/api/menu/<int:restaurant_id>", methods=['GET'])
def get_restaurant_menu(restaurant_id):
    try:
        response = supabase.table('menu').select('*').eq('restaurant_id', restaurant_id).execute()
        menu_items = response.data
        
        if menu_items:
            return jsonify({
                "code": 200,
                "data": {
                    "menu_items": menu_items
                }
            })
        return jsonify({
            "code": 404,
            "message": f"No menu items found for restaurant ID: {restaurant_id}"
        }), 404
    except Exception as e:
        return jsonify({
            "code": 500,
            "message": f"An error occurred: {str(e)}"
        }), 500

# get a specific menu item by ID
@app.route("/api/menu/item/<int:menu_id>", methods=['GET'])
def get_menu_item(menu_id):
    try:
        response = supabase.table('menu').select('*').eq('menu_id', menu_id).execute()
        menu_item = response.data[0] if response.data else None
        
        if menu_item:
            return jsonify({
                "code": 200,
                "data": menu_item
            })
        return jsonify({
            "code": 404,
            "message": f"Menu item not found with ID: {menu_id}"
        }), 404
    except Exception as e:
        return jsonify({
            "code": 500,
            "message": f"An error occurred: {str(e)}"
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5003))
    app.run(host='0.0.0.0', port=port, debug=True)