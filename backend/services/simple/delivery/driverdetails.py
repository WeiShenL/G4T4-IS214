#!/usr/bin/env python3

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
from supabase import create_client, Client
from uuid import UUID

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
            "availability": True         # Default value
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

# Main entry point
if __name__ == '__main__':
    print("Starting Flask app for driver details management...")
    app.run(host='0.0.0.0', port=5008, debug=True)