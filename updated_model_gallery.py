import requests
from bs4 import BeautifulSoup
import sqlite3

# URL for The Niland Collection page at The Model Gallery
url = "https://www.themodel.ie/art-and-artists/the-niland-collection/"
painting_details = []

# Set up SQLite3 database connection
conn = sqlite3.connect('model_gallery_paintings.db')
cursor = conn.cursor()

# Creating a paintings table if it doesn't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS paintings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        artist TEXT,
        link TEXT UNIQUE,
        details TEXT
    )
''')
conn.commit()

# Keep track of visited pages
visited_pages = set()

# Scrape info from each page
while True:
    print(f"Fetching page {url}...")
    if url in visited_pages:
        print("Already visited this page.")
        break
    visited_pages.add(url)
    
    try:
        # GET request to the webpage
        response = requests.get(url)
        response.raise_for_status()  # Ensure we got a successful response

        # Parse details
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract artwork list items
        artworks_section = soup.find_all('li', class_='artwork')
        if not artworks_section:
            # if none found assume reached the last page
            break
        
        for artwork in artworks_section:
            # Extract the title
            abbr_tag = artwork.find('abbr', title=True)
            title = abbr_tag['title'] if abbr_tag else "No Title"

            # Extract the link
            link_tag = artwork.find('a', href=True)
            link = link_tag['href'] if link_tag else "No Link"

            # Extract the artist
            artist_tag = artwork.find('a', rel='tag')
            artist = artist_tag.get_text(strip=True) if artist_tag else "Unknown Artist"

            # If a valid link exists go to artwork's page to extract more details
            if link != "No Link":
                try:
                    artwork_response = requests.get(link)
                    artwork_response.raise_for_status()

                    # Parse the page content
                    artwork_soup = BeautifulSoup(artwork_response.content, 'html.parser')

                    # Extract details
                    details_div = artwork_soup.find('div', class_='post-content')
                    if details_div:
                        # Collect text
                        details_paragraphs = details_div.find_all('p')
                        details_text = "\n".join([p.get_text(strip=True) for p in details_paragraphs if p.get_text(strip=True)])
                    else:
                        details_text = "No Details"
                except requests.exceptions.RequestException as e:
                    details_text = "Error fetching details"
            else:
                details_text = "No Link Provided"

            # Insert data into SQLite database
            cursor.execute('''
                INSERT OR IGNORE INTO paintings (title, artist, link, details)
                VALUES (?, ?, ?, ?)
            ''', (title, artist, link, details_text))
            conn.commit()

        # Get the link to the next page
        pagination = soup.find('ul', class_='pagination')
        next_page_link = None

        if pagination:
            current_page_item = pagination.find('li', class_='active')
            if current_page_item:
                next_page_item = current_page_item.find_next_sibling('li')
                if next_page_item:
                    next_page_link = next_page_item.find('a', href=True)

        if next_page_link and 'href' in next_page_link.attrs:
            next_page_url = next_page_link['href']
            if next_page_url in visited_pages:
                # If the next page URL has already been visited, break the loop
                break
            url = next_page_url
        else:
            # If there's no next page link, finished
            break

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        break

# Close the database connection
conn.close()

print("Scraping complete and data saved to database.")
