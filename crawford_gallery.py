import sqlite3
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Initialize SQLite database
conn = sqlite3.connect("crawford_gallery_paintings.db")
cursor = conn.cursor()

# Create table if it doesn't exist
cursor.execute('''
CREATE TABLE IF NOT EXISTS Paintings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    material TEXT,
    dimensions TEXT,
    credit_line TEXT,
    classification TEXT,
    catalogue_number TEXT,
    location_status TEXT
)
''')
conn.commit()

# Initialize WebDriver
driver = webdriver.Chrome()
driver.get("https://mpcrawfordartgallery.zetcom.app/v?mode=online#!m/Object/628/lightbox/@default.lightbox.large")

# Select "All works in the collection"
try:
    dropdown_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CLASS_NAME, "v-filterselect-button"))
    )
    dropdown_button.click()
    print("Dropdown opened.")
    
    all_works_option = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//tr/td/span[contains(text(), 'All works in the collection')]"))
    )
    all_works_option.click()
    print("Selected 'All works in the collection'.")
    
    # Confirm selection
    selected_value = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "v-filterselect-input"))
    ).get_attribute("value")
    
    if "All works in the collection" in selected_value:
        print(f"Selection confirmed: {selected_value}")
    else:
        print(f"Selection failed: {selected_value}")
except Exception as e:
    print("Error selecting 'All works in the collection':", e)

# Click the "Detail" button twice
try:
    for _ in range(2):
        detail_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "ObjSwitchToCatalogViewLnk"))
        )
        detail_button.click()
        print("Clicked 'Detail' button.")
        time.sleep(2)  # Wait for page update
except Exception as e:
    print("Error clicking 'Detail' button:", e)

# Scrape painting details with pagination
current_page = 1
last_page = 3172

while current_page <= last_page:
    try:
        # Scrape painting details
        details = {
            "title": driver.find_element(By.CLASS_NAME, "objTitleDat").text,
            "material": driver.find_element(By.CLASS_NAME, "objMaterial.dataText").text,
            "dimensions": driver.find_element(By.CLASS_NAME, "objDim.dataText").text,
            "credit_line": driver.find_element(By.CLASS_NAME, "objCreditline.dataText").text,
            "classification": driver.find_element(By.CLASS_NAME, "objClassification.dataText").text,
            "catalogue_number": driver.find_element(By.CLASS_NAME, "objNr.dataText").text,
            "location_status": driver.find_element(By.CLASS_NAME, "objLocation.dataText").text
        }

        # Insert into SQLite database
        cursor.execute('''
        INSERT INTO Paintings (title, material, dimensions, credit_line, classification, catalogue_number, location_status)
        VALUES (:title, :material, :dimensions, :credit_line, :classification, :catalogue_number, :location_status)
        ''', details)
        conn.commit()
        print(f"Saved painting: {details['title']}")

    except Exception as e:
        print(f"Error scraping painting details on page {current_page}: {e}")

    # Click "Next" button
    try:
        next_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "smt-button-next-object"))
        )
        next_button.click()
        current_page += 1
        print(f"Moved to page {current_page}.")
        time.sleep(4)  # Wait for next painting to load
    except Exception as e:
        print("Error clicking 'Next' button:", e)
        break

# Close database and driver
conn.close()
driver.quit()
