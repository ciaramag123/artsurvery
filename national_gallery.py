import csv
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
# Set to True to run headless
options.headless = True  
# Disabled images
prefs = {"profile.managed_default_content_settings.images": 2}  
options.add_experimental_option("prefs", prefs)
driver = webdriver.Chrome(service=service, options=options)

# Open a new CSV to save data
csv_filename = 'national_gallery_paintings_details.csv'
with open(csv_filename, mode='w', newline='', encoding='utf-8') as outfile:
    writer = csv.writer(outfile)
    writer.writerow(['Title', 'Link', 'Date', 'Medium', 'Dimensions', 'Object Number', 'Credit Line'])  # Updated CSV header

    # Starting URL
    base_url = "http://onlinecollection.nationalgallery.ie/categories/classifications/Paintings"
    driver.get(base_url)

    # Set to hold paintings
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

                        # Write data to CSV
                        writer.writerow([title, link, date, medium, dimensions, object_number, credit_line])
                    except TimeoutException:
                        print(f"Timeout while loading details for: {title}")
                        continue
                    except Exception as e:
                        print(f"Error while extracting details for {title}: {e}")
                        continue
                    # Go back to the main list page
                    driver.back()

            # Find the next page button click it if its available
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

# Close the browser
driver.quit()
# Completion message
print(f"Finished. CVS file: {csv_filename}")
