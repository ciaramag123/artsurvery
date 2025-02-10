import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

# Load the dataset
file_path = '/Users/ciaramaguire/Desktop/k-cluster/Categorized_County_Data.csv'
data = pd.read_csv(file_path)

# Relevant columns for clustering
features = ['Population_Density', 'Education', 'Irish_Language', 'Unemployment', 'Population_by_Age_Sex', 'Salary']

# Apply weights to features (adjust these based on importance)
weights = {
    'Population_Density': 1.0, 
    'Education': 1.5,          
    'Irish_Language': 0.5, 
    'Unemployment': 1.5, 
    'Population_by_Age_Sex': 0.5, 
    'Salary': 2.0 
}

# Create a weighted feature DataFrame
weighted_features = data[features].copy()
for feature, weight in weights.items():
    weighted_features[feature] *= weight

# Standardize the features
scaler = StandardScaler()
scaled_features = scaler.fit_transform(weighted_features)

# Apply K-Means clustering
kmeans = KMeans(n_clusters=5, random_state=42)  # Adjust n_clusters as needed
data['Cluster'] = kmeans.fit_predict(scaled_features)

# Define cluster names based on Irish geodemographic characteristics
cluster_names = {
    0: "Affluent Commuter Counties",
    1: "Urban Economic Core",
    2: "Regional Hubs & University Cities",
    3: "Rural and Developing Counties",
    4: "Economically Challenged & Peripheral Counties"
}

# Assign names to the clusters
data['Cluster_Name'] = data['Cluster'].map(cluster_names)

# Save the updated dataset
output_path = '/Users/ciaramaguire/Desktop/k-cluster/categorised_counties.csv'
data.to_csv(output_path, index=False)

# Display results
print("Cluster Assignments with Categories:\n", data[['County', 'Cluster', 'Cluster_Name']])
print(f"Updated clustered data saved to: {output_path}")
