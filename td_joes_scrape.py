from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import csv
from datetime import datetime
import time

# Set up Chrome WebDriver using WebDriver Manager
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)

# Define the list of items to search for
items_to_search = ["orange", "apple", "banana", "tomato", "potato", "onion", "garlic"]

# CSV file setup
csv_filename = "trader_joes_products.csv"
fields = ["id", "store_name", "product_name", "url", "price", "last_checked_at"]

# Open the CSV file in write mode
with open(csv_filename, mode='w', newline='', encoding='utf-8') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=fields)
    writer.writeheader()  # Write header row

    id_counter = 1  # Initialize ID counter
    
    for item in items_to_search:
        # Open Trader Joe's search URL with the specific section for products
        url = f"https://www.traderjoes.com/home/search?q={item}&section=products&global=yes"
        driver.get(url)

        # Wait for the page content to load
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, 'SearchResultCard_searchResultCard__3V-_h'))
            )
        except Exception as e:
            print(f"Timeout or error occurred while loading results for '{item}': {e}")
            continue  # Skip to the next item if there's an issue
        
        # Get the page source after JavaScript loads
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # Find all article tags containing product info
        search_results = soup.find_all("article", class_="SearchResultCard_searchResultCard__3V-_h")

        # If there are results, extract details
        if search_results:
            print(f"Found {len(search_results)} results for '{item}':")
            
            for result in search_results:
                # Extract the product name
                title_tag = result.find("a", class_="Link_link__1AZfr SearchResultCard_searchResultCard__titleLink__2nz6x")
                product_name = title_tag.text.strip() if title_tag else "No title found"
                
                # Extract the product link
                product_link = f"https://www.traderjoes.com{title_tag['href']}" if title_tag else "No link found"
                
                # Extract the price
                price_tag = result.find("span", class_="ProductPrice_productPrice__price__3-50j")
                product_price = price_tag.text.strip() if price_tag else "No price found"
                
                # Get the current timestamp
                last_checked_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                # Write the extracted data to the CSV file
                writer.writerow({
                    "id": id_counter,
                    "store_name": "Trader Joe's",
                    "product_name": product_name,
                    "url": product_link,
                    "price": product_price,
                    "last_checked_at": last_checked_at
                })
                
                # Increment the ID counter
                id_counter += 1
                
                # Print feedback to console for tracking
                print(f"Added '{product_name}' to CSV.")
                print("-" * 40)
        else:
            print(f"No results found for '{item}' in the 'Products' section on Trader Joe's.")

# Close the browser when done
driver.quit()

print(f"Scraping complete. Data saved to '{csv_filename}'.")
