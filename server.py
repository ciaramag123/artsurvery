from flask import Flask, jsonify, request, send_from_directory, render_template, send_file
import os
import json
import random


# Initialize Flask app and set template folder
app = Flask(__name__, template_folder="templates")

# Image directories
IMAGE_DIRS = {
    "Crawford Gallery": os.path.join(app.root_path, "static/images/crawford_gal_images"),
    "National Gallery": os.path.join(app.root_path, "static/images/national_gal_image"),
    "Model Gallery": os.path.join(app.root_path, "static/images/model_images"),
}

# Responses directory
RESPONSES_DIR = os.path.join(app.root_path, "static/responses")
os.makedirs(RESPONSES_DIR, exist_ok=True)  # Ensure the folder exists


# Function to get random images from a directory
def get_images(directory, num=2):
    """Returns a list of randomly selected image file names from a given directory."""
    try:
        images = [img for img in os.listdir(directory) if img.lower().endswith(('.png', '.jpg', '.jpeg'))]
        return random.sample(images, min(len(images), num))  # Select 2 random images
    except FileNotFoundError:
        return []

# Route to serve the main survey page
@app.route('/')
def survey_page():
    """Serves the main survey HTML page."""
    return render_template("front.html")

# Route to get random images
@app.route('/get-images', methods=['GET'])
def get_all_images():
    """Returns a selection of images with hidden category data as JSON."""
    all_images = []
    for category, path in IMAGE_DIRS.items():
        images = get_images(path)
        for img in images:
            all_images.append({"filename": img, "hidden": category})  # Include the category for internal use
    random.shuffle(all_images)  # Shuffle to prevent bias
    return jsonify(all_images)

# Route to serve images dynamically
@app.route('/images/<category>/<filename>')
def serve_image(category, filename):
    """Serves images dynamically."""
    directory = IMAGE_DIRS.get(category.replace("%20", " "))  # Handle spaces in URL
    if directory:
        return send_from_directory(directory, filename)
    return jsonify({"error": "Category not found"}), 404

# Route to submit the survey
@app.route('/submit-survey', methods=['POST'])
def submit_survey():
    """Receives and saves survey responses."""
    try:
        data = request.json
        print(f"Received data: {data}")  # Debugging print
        
        # Check if data is empty or malformed
        if not data:
            return jsonify({"error": "No data received"}), 400
        
        # Save responses to a JSON file
        file_path = "survey_responses.json"  # Ensure this file path matches your setup
        with open(file_path, "a") as f:
            json.dump(data, f)
            f.write("\n")  # New line for each response
        
        print(f"Data saved to: {file_path}")
        return jsonify({"message": "Survey submitted successfully!"})
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": str(e)}), 500


# Route to fetch counties for the dropdown
@app.route('/get-counties', methods=['GET'])
def get_counties():
    """Returns a list of counties for the dropdown."""
    counties = [
        "Dublin", "Cork", "Galway", "Limerick", "Waterford", "Kilkenny", "Wexford", "Mayo",
        "Kerry", "Donegal", "Longford", "Louth", "Westmeath", "Meath", "Roscommon",
        "Sligo", "Carlow", "Clare", "Offaly", "Tipperary", "Leitrim", "Cavan", "Monaghan"
    ]
    return jsonify(counties)

# Route to view survey responses
@app.route('/view-responses', methods=['GET'])
def view_responses():
    """Displays the survey responses saved in the JSON file."""
    try:
        # Check if the file exists
        if not os.path.exists("survey_responses.json"):
            return jsonify({"message": "No responses found."}), 404
        
        # Read the responses from the file
        with open("survey_responses.json", "r") as f:
            responses = f.readlines()
        
        # Parse the responses as JSON objects
        parsed_responses = [json.loads(response) for response in responses]
        return jsonify(parsed_responses)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    



# Run Flask
if __name__ == '__main__':
    app.run(debug=True)
