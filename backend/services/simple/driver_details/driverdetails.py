#!/usr/bin/env python3

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
from supabase import create_client, Client
from uuid import UUID
import requests


load_dotenv()

app = Flask(__name__)

CORS(app, resources={r"/*": {"origins": "*"}})

supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_KEY')
supabase: Client = create_client(supabase_url, supabase_key)



@app.route("/driverdetails/<uuid:driver_id>", methods=['GET'])
def get_driver_details_by_id(driver_id):
    """
    Retrieve driver details for a specific driver_id from Supabase.
    If no record exists, create one with default values.
    """
    try:
        # Step 1: Convert driver_id to string (required for Supabase queries)
        driver_id_str = str(driver_id)

        # Step 2: Check if the driver exists in the database
        response = supabase.table("driverdetails").select("*").eq("driver_id", driver_id_str).execute()
        driver_detail = response.data

        if driver_detail:
            # Return existing driver details
            return jsonify(
                {
                    "code": 200,
                    "data": driver_detail[0]
                }
            )

        # Step 3: Create a new record if the driver doesn't exist
        print(f"No driver found for driver_id: {driver_id}. Creating a new record.")

        new_driver_detail = {
            "driver_id": driver_id_str,  # Ensure UUID is converted to string
            "live_location": None,       # Default value
            "availability": True,        # Default value
            "total_deliveries": 0,       # Default value for new column
            "total_earnings": 0.00       # Default value for new column
        }

        # Attempt to insert the new record
        create_response = supabase.table("driverdetails").insert(new_driver_detail).execute()

        # Log the insertion result
        print(f"Insertion result: {create_response}")

        # Return the newly created driver details
        return jsonify(
            {
                "code": 201,
                "message": "Driver details created successfully.",
                "data": create_response.data[0]
            }
        ), 201

    except Exception as e:
        print(f"Error fetching/creating driver details: {str(e)}")
        return jsonify(
            {
                "code": 500,
                "message": f"An error occurred while fetching/creating driver details: {str(e)}"
            }
        ), 500
    

@app.route("/driverdetails/<uuid:driver_id>", methods=['PATCH'])
def update_driver_availability(driver_id):
    """
    Update driver availability for a specific driver_id.
    No pre-check for driver existence is performed.
    """
    try:
        # Step 1: Convert driver_id to string (required for Supabase queries)
        driver_id_str = str(driver_id)

        # Step 2: Parse the request body
        data = request.json
        availability = data.get("availability")

        if availability is None:
            return jsonify(
                {
                    "code": 400,
                    "message": "Missing 'availability' field in request body."
                }
            ), 400

        # Step 3: Attempt to update the driver's availability
        update_response = supabase.table("driverdetails").update({"availability": availability}).eq("driver_id", driver_id_str).execute()

        # Step 4: Check if the update was successful
        if not update_response.data:
            return jsonify(
                {
                    "code": 404,
                    "message": f"Driver with ID {driver_id_str} not found or no rows updated."
                }
            ), 404

        # Step 5: Return success response
        return jsonify(
            {
                "code": 200,
                "message": "Driver availability updated successfully.",
                "data": update_response.data[0]
            }
        ), 200

    except Exception as e:
        print(f"Error updating driver availability: {str(e)}")
        return jsonify(
            {
                "code": 500,
                "message": f"An error occurred while updating driver availability: {str(e)}"
            }
        ), 500


@app.route("/driverdetails/<uuid:driver_id>/complete-delivery", methods=['PATCH'])
def update_delivery_completion(driver_id):
    """
    Update driver's total deliveries and earnings when a delivery is completed.
    Adds 1 to total_deliveries and $5.00 to total_earnings.
    """
    try:
        # Convert driver_id to string (required for Supabase queries)
        driver_id_str = str(driver_id)
        
        # Default earning per delivery
        earnings_per_delivery = 5.00
        
        # Step 1: Get current delivery stats
        response = supabase.table("driverdetails").select("total_deliveries, total_earnings").eq("driver_id", driver_id_str).execute()
        
        if not response.data:
            return jsonify(
                {
                    "code": 404,
                    "message": f"Driver with ID {driver_id_str} not found."
                }
            ), 404
            
        # Get current values
        current_stats = response.data[0]
        current_deliveries = current_stats.get("total_deliveries", 0)
        current_earnings = current_stats.get("total_earnings", 0.00)
        
        # Calculate new values
        new_deliveries = current_deliveries + 1
        new_earnings = float(current_earnings) + earnings_per_delivery
        
        # Step 2: Update the driver's stats
        update_data = {
            "total_deliveries": new_deliveries,
            "total_earnings": new_earnings
        }
        
        update_response = supabase.table("driverdetails").update(update_data).eq("driver_id", driver_id_str).execute()
        
        # Step 3: Return success response
        return jsonify(
            {
                "code": 200,
                "message": "Driver delivery stats updated successfully.",
                "data": {
                    "total_deliveries": new_deliveries,
                    "total_earnings": new_earnings
                }
            }
        ), 200

    except Exception as e:
        print(f"Error updating driver delivery stats: {str(e)}")
        return jsonify(
            {
                "code": 500,
                "message": f"An error occurred while updating driver delivery stats: {str(e)}"
            }
        ), 500
    
# update live location
@app.route("/proxy-geolocation/<uuid:driver_id>", methods=['POST'])
def proxy_geolocation(driver_id):
    """
    Proxy requests to Google Geolocation API to avoid CORS issues
    """
    try:
        
        url = f"https://www.googleapis.com/geolocation/v1/geolocate?key=AIzaSyA_-ROgMNf8_3OYskUQklbbbH4XIl8WaRk"
        
        # Forward the request to Google - which requires POST
        response = requests.post(url, json={"considerIp": True})
        
        if response.ok:
            location_data = response.json()
            
            # Now update your driver's location with the result
            driver_id_str = str(driver_id)
            location_str = f"{location_data['location']['lat']},{location_data['location']['lng']}"
            
            # Update driver location in your database
            update_response = supabase.table("driverdetails").update({
                "live_location": location_str
            }).eq("driver_id", driver_id_str).execute()
            
            return jsonify({
                "code": 200,
                "message": "Driver location updated successfully.",
                "data": {
                    "location": location_data['location'],
                    "accuracy": location_data.get('accuracy')
                }
            }), 200
        else:
            return jsonify({
                "code": response.status_code,
                "message": "Error from Google Geolocation API"
            }), response.status_code
    
    except Exception as e:
        print(f"Error in geolocation proxy: {str(e)}")
        return jsonify({
            "code": 500,
            "message": f"An error occurred: {str(e)}"
        }), 500



# Main entry point
if __name__ == '__main__':
    print("Starting Flask app for driver details management...")
    app.run(host='0.0.0.0', port=5012, debug=True)