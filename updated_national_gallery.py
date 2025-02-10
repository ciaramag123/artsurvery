import sqlite3
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException
from bs4 import BeautifulSoup

# Setting up chrome driver with Selenium
service = Service(ChromeDriverManager().install())
# Run chrome in headless mode and disable image loading
options = Options()
options.headless = True  # Set to True to run headless
prefs = {"profile.managed_default_content_settings.images": 2}  # Disable images for faster scraping
options.add_experimental_option("prefs", prefs)
driver = webdriver.Chrome(service=service, options=options)

# Connect to SQLite database (or create it if it doesn't exist)
conn = sqlite3.connect('national_gallery_paintings.db')
cursor = conn.cursor()

# Create table if it doesn't exist
cursor.execute('''CREATE TABLE IF NOT EXISTS paintings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    link TEXT,
    date TEXT,
    medium TEXT,
    dimensions TEXT,
    object_number TEXT,
    credit_line TEXT
)''')

# Starting URL
base_url = "http://onlinecollection.nationalgallery.ie/categories/classifications/Paintings"
driver.get(base_url)

# Set to hold visited paintings links
visited_links = set()

while True:
    try:
        print(f"Fetching page {driver.current_url}")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'list-item-inner'))
        )
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        paintings = soup.find_all('div', class_='list-item-inner')

        for painting in paintings:
            a_tag = painting.find('h3').find('a')
            if a_tag:
                title = a_tag.get_text(strip=True)
                link = f"http://onlinecollection.nationalgallery.ie{a_tag['href']}"

                # Prevent revisiting links
                if link in visited_links:
                    continue
                visited_links.add(link)

                # Visit the link to extract detailed information
                driver.get(link)
                try:
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CLASS_NAME, 'detailFieldValue'))
                    )
                    # Parse page with BeautifulSoup
                    detail_soup = BeautifulSoup(driver.page_source, 'html.parser')

                    # Extract details
                    date = detail_soup.find('div', class_='displayDateField').find('span', class_='detailFieldValue').get_text(strip=True) if detail_soup.find('div', class_='displayDateField') else 'N/A'
                    medium = detail_soup.find('div', class_='mediumField').find('span', class_='detailFieldValue').get_text(strip=True) if detail_soup.find('div', class_='mediumField') else 'N/A'
                    dimensions = detail_soup.find('div', class_='dimensionsField').find('span', class_='detailFieldValue').get_text(strip=True) if detail_soup.find('div', class_='dimensionsField') else 'N/A'
                    object_number = detail_soup.find('div', class_='invnoField').find('span', class_='detailFieldValue').get_text(strip=True) if detail_soup.find('div', class_='invnoField') else 'N/A'
                    credit_line = detail_soup.find('div', class_='creditlineField').find('span', class_='detailFieldValue').get_text(strip=True) if detail_soup.find('div', class_='creditlineField') else 'N/A'

                    # Insert data into the database
                    cursor.execute('''INSERT INTO paintings (title, link, date, medium, dimensions, object_number, credit_line) 
                                      VALUES (?, ?, ?, ?, ?, ?, ?)''', 
                                      (title, link, date, medium, dimensions, object_number, credit_line))
                    conn.commit()  # Commit the changes to the database

                except TimeoutException:
                    print(f"Timeout while loading details for: {title}")
                    continue
                except Exception as e:
                    print(f"Error while extracting details for {title}: {e}")
                    continue
                # Go back to the main list page
                driver.back()

        # Find the next page button and click it if available
        try:
            next_button = driver.find_element(By.CSS_SELECTOR, "a.emuseum-pager-button.next-page-link")
            next_button.click()
        except NoSuchElementException:
            print("No more pages left to scrape.")
            break
    except TimeoutException:
        print("Page load timed out.")
        break
    except Exception as e:
        print(f"Error occurred: {e}")
        break

# Close the browser and the SQLite connection
driver.quit()
conn.close()

# Completion message
print("Scraping complete and data saved to the database.")
