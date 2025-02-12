import sqlite3
import pandas as pd

# Paths to your existing SQLite databases
databases = {
    "Crawford": "/Users/ciaramaguire/Documents/databases/crawfordpaintings_copy.db",
    "ModelGallery": "/Users/ciaramaguire/Documents/databases/model_gallery_paintings_copy.db",
    "NationalGallery": "/Users/ciaramaguire/Documents/databases/national_gallery_paintings.db",
}

# Paths to your survey data CSVs
csv_files = {
    "SurveyResponses": "/Users/ciaramaguire/Downloads/survey_response.csv",
    "ArtworkRanking": "/Users/ciaramaguire/Downloads/artwork_ranking.csv",
}

# Load painting details from a specific database
def load_painting_data(db_path, table_name="paintings"):
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
    conn.close()
    return df

# Load survey data
def load_survey_data(csv_files):
    survey_responses = pd.read_csv(csv_files["SurveyResponses"])
    artwork_ranking = pd.read_csv(csv_files["ArtworkRanking"])
    return survey_responses, artwork_ranking

def combine_painting_data(databases):
    # Load data from each gallery database
    crawford_data = load_painting_data(databases["Crawford"])
    model_data = load_painting_data(databases["ModelGallery"])
    national_data = load_painting_data(databases["NationalGallery"])
    
    # Add a source column to identify which gallery the data came from
    crawford_data["Gallery"] = "Crawford Gallery"
    model_data["Gallery"] = "Model Gallery"
    national_data["Gallery"] = "National Gallery"
    
    # Rename Catalogue_Number for consistency
    if "catalogue_number" in crawford_data.columns:
        crawford_data.rename(columns={"catalogue_number": "Catalogue_Number"}, inplace=True)
    if "id" in model_data.columns:  # Assuming `id` is used as Catalogue_Number in Model
        model_data.rename(columns={"id": "Catalogue_Number"}, inplace=True)
    if "Object Number" in national_data.columns:  # Assuming National Gallery uses this column
        national_data.rename(columns={"Object Number": "Catalogue_Number"}, inplace=True)

    # Combine all data
    all_painting_data = pd.concat([crawford_data, model_data, national_data], ignore_index=True)

    # Debug: Check column names
    print("All Painting Data Columns:", all_painting_data.columns)

    return all_painting_data


# Merge survey data with painting details
def merge_data(all_painting_data, survey_responses, artwork_ranking):
    # Normalize the column for merging
    all_painting_data["Catalogue_Number"] = all_painting_data["Catalogue_Number"].astype(str)
    artwork_ranking["filename"] = artwork_ranking["filename"].astype(str)
    
    # Merge artwork ranking with painting details
    merged_data = pd.merge(artwork_ranking, all_painting_data, left_on="filename", right_on="Catalogue_Number", how="left")
    
    # Add survey responses (link using survey_id)
    final_data = pd.merge(merged_data, survey_responses, left_on="survey_id", right_on="id", how="left")
    
    return final_data

# Save to CSV for further analysis
def save_data(final_data, output_path):
    final_data.to_csv(output_path, index=False)
    print(f"Combined data saved to '{output_path}'")

# Main function
def main():
    # Load painting details from databases
    all_painting_data = combine_painting_data(databases)
    
    # Load survey data
    survey_responses, artwork_ranking = load_survey_data(csv_files)
    
    # Merge all data
    final_data = merge_data(all_painting_data, survey_responses, artwork_ranking)
    
    # Save combined data for analysis
    output_path = "/Users/ciaramaguire/Documents/databases/combined_survey_analysis.csv"
    save_data(final_data, output_path)

# Run the script
if __name__ == "__main__":
    main()
