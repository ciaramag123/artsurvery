import json
from flask import Flask, jsonify, request, send_from_directory, render_template
from flask_sqlalchemy import SQLAlchemy
import os
import random

# Initialize Flask app and set template folder
app = Flask(__name__, template_folder="templates")

# Configure the database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///responses.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Define the database model for survey responses
class SurveyResponse(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    county = db.Column(db.String(100), nullable=False)

class ArtworkRanking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    survey_id = db.Column(db.Integer, db.ForeignKey('survey_response.id'), nullable=False)
    rank = db.Column(db.Integer, nullable=False)
    museum = db.Column(db.String(100), nullable=False)
    filename = db.Column(db.String(100), nullable=False)

    survey = db.relationship('SurveyResponse', backref=db.backref('rankings', lazy=True))


# Create the database tables
with app.app_context():
    print(f"Database path: {db.engine.url.database}")  # Debug: Verify the database path
    db.create_all()

# Image directories
IMAGE_DIRS = {
    "Crawford Gallery": os.path.join(app.root_path, "static/images/crawford_gal_images"),
    "National Gallery": os.path.join(app.root_path, "static/images/national_gal_image"),
    "Model Gallery": os.path.join(app.root_path, "static/images/model_images"),
}

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

@app.route('/submit-survey', methods=['POST'])
def submit_survey():
    try:
        data = request.json
        print("Received Data:", data)  # Debug: Print incoming data

        if not data or "county" not in data or "rankings" not in data:
            return jsonify({"error": "Invalid data format"}), 400

        # Add SurveyResponse entry
        survey_response = SurveyResponse(county=data["county"])
        print(f"Adding SurveyResponse for county: {data['county']}")
        db.session.add(survey_response)
        db.session.commit()

        # Add ArtworkRanking entries
        for ranking in data["rankings"]:
            print(f"Processing ranking: {ranking}")
            if not ranking.get("rank") or not ranking.get("museum") or not ranking.get("filename"):
                return jsonify({"error": "Incomplete ranking data."}), 400

            artwork_ranking = ArtworkRanking(
                survey_id=survey_response.id,
                rank=int(ranking["rank"]),  # Convert rank to integer
                museum=ranking["museum"],
                filename=ranking["filename"],
            )
            db.session.add(artwork_ranking)

        db.session.commit()
        print("Survey submitted successfully!")

        return jsonify({"message": "Survey submitted successfully!"})
    except Exception as e:
        print(f"Error during submission: {e}")
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
    """Displays the survey responses saved in the database."""
    try:
        # Fetch all survey responses
        responses = SurveyResponse.query.all()
        result = []

        for response in responses:
            rankings = ArtworkRanking.query.filter_by(survey_id=response.id).all()
            rankings_list = [
                {
                    "rank": ranking.rank,
                    "museum": ranking.museum,
                    "filename": ranking.filename
                }
                for ranking in rankings
            ]
            result.append({
                "county": response.county,
                "rankings": rankings_list
            })

        print("Responses fetched:", result)  # Debug: Log responses
        return jsonify(result)
    except Exception as e:
        print(f"Error fetching responses: {e}")
        return jsonify({"error": str(e)}), 500


# Run Flask
if __name__ == '__main__':
    app.run(debug=True)
