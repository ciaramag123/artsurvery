# Note: The KML file ('doc.kml') was exported from Google My Maps: https://www.google.com/maps/d/edit?mid=1U1cTU-uLhIcGdmyjOrJPo1LflwJ0IvqS&ll=53.34192469950176%2C-6.264539660890964&z=16
#  It contains relevant details for the project, including Location, Discipline and Name.
import sqlite3
import xml.etree.ElementTree as ET

# Function to convert KML to SQLite database
def kml_to_database(kml_file, db_name):
    # Connect to SQLite database
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Create a table for storing the data
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS museums (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            address TEXT,
            website TEXT,
            email TEXT,
            discipline TEXT
        )
    ''')
    conn.commit()

    # Parse KML file
    tree = ET.parse(kml_file)
    root = tree.getroot()

    # Define KML namespace 
    namespace = {'kml': 'http://www.opengis.net/kml/2.2'}

    # Loop through each Placemark in the KML file
    for placemark in root.findall('.//kml:Placemark', namespace):
        name = placemark.find('kml:name', namespace)
        name = name.text if name is not None else 'No Name'

        # Extracting information from exteneded data
        address = website = email = discipline = 'No Data'
        for data in placemark.findall('.//kml:Data', namespace):
            data_name = data.get('name')
            value = data.find('kml:value', namespace)
            value = value.text if value is not None else 'No Data'
            if data_name == 'Address':
                address = value
            elif data_name == 'Website':
                website = value
            elif data_name == 'Email':
                email = value
            elif data_name == 'Discipline':
                discipline = value

        # Insert the data into the SQLite database
        cursor.execute('''
            INSERT INTO museums (name, address, website, email, discipline)
            VALUES (?, ?, ?, ?, ?)
        ''', (name, address, website, email, discipline))
        conn.commit()

    # Close the connection to the database
    conn.close()
    print("Successfully stored in database.")

kml_file = '/Users/ciaramaguire/Documents/Project_Final_Year/Geodemographics Museums/Irish Museums/doc.kml'  
db_name = 'museums.db'
kml_to_database(kml_file, db_name)
