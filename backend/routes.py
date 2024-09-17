from . import app
import os
import json
from flask import jsonify, request, make_response, abort, url_for  # noqa; F401

SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
json_url = os.path.join(SITE_ROOT, "data", "pictures.json")
data: list = json.load(open(json_url))

######################################################################
# RETURN HEALTH OF THE APP
######################################################################


@app.route("/health")
def health():
    return jsonify(dict(status="OK")), 200

######################################################################
# COUNT THE NUMBER OF PICTURES
######################################################################


@app.route("/count")
def count():
    """return length of data"""
    if data:
        return jsonify(length=len(data)), 200

    return {"message": "Internal server error"}, 500


######################################################################
# GET ALL PICTURES
######################################################################
@app.route("/picture", methods=["GET"])
def get_pictures():
    """Return a list of all picture URLs."""
    if data:
        return jsonify(data), 200
    return {"message": "Internal server error"}, 500

######################################################################
# GET A PICTURE
######################################################################
@app.route("/picture/<int:id>", methods=["GET"])
def get_picture_by_id(id):
    """Get a picture by its ID."""
    for picture in data:
        if picture.get('id') == id:
            return jsonify(picture), 200
    
    return jsonify({"message": "picture not found"}), 404



######################################################################
# CREATE A PICTURE
######################################################################
@app.route("/picture", methods=["POST"])
def create_picture():
    """Create a new picture or reject duplicates."""
    picture_data = request.json
    
    # Check if 'id' is present in the incoming data
    if 'id' not in picture_data:
        return jsonify({"message": "ID is required"}), 400
    
    picture_id = picture_data['id']
    
    # Check if a picture with the given ID already exists
    for picture in data:
        if picture.get('id') == picture_id:
            return jsonify({"Message": f"picture with id {picture_id} already present"}), 302
    
    # Append the new picture data to the list
    data.append(picture_data)
    
    # Return the created picture's ID
    return jsonify({"id": picture_id, "message": "Picture added successfully"}), 201

######################################################################
# UPDATE A PICTURE
######################################################################


@app.route("/picture/<int:id>", methods=["PUT"])
def update_picture(id):
    """Update an existing picture by ID."""
    # Extract the updated picture data from the request body
    updated_picture = request.json
    
    # Check if 'id' is present in the incoming data
    if 'id' not in updated_picture:
        return jsonify({"message": "ID is required"}), 400

    # Find the picture to update
    for i, picture in enumerate(data):
        if picture.get('id') == id:
            data[i] = updated_picture  # Update the picture data
            return jsonify({"id": id, "message": "Picture updated successfully"}), 200
    
    # If the picture is not found, return 404
    return jsonify({"message": "picture not found"}), 404


######################################################################
# DELETE A PICTURE
######################################################################
@app.route("/picture/<int:id>", methods=["DELETE"])
def delete_picture(id):
    """Delete a picture by its ID."""
    global data
    # Find the picture with the given ID
    picture_to_delete = next((pic for pic in data if pic.get('id') == id), None)

    if picture_to_delete:
        # Remove the picture from the list
        data = [pic for pic in data if pic.get('id') != id]
        # Save changes back to the file (if needed)
        with open(json_url, "w") as f:
            json.dump(data, f)
        return '', 204  # No Content
    else:
        return jsonify({"message": "picture not found"}), 404
