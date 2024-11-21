import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from datetime import datetime
import time

# Set up the Selenium WebDriver (this will automatically manage the ChromeDriver)
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

# URL used for scraping (we can change the keyword from produce to search up other items etc)
url = "https://www.target.com/s?searchTerm=produce&tref=typeahead%7Cterm%7Cproduce%7C%7C%7Chistory"

# Open the page
driver.get(url)

# Give the page some time to load initially
driver.implicitly_wait(10)

# Function to scroll gradually down the page
def gradual_scroll_page(driver):
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollBy(0, 1000);")  # Scroll down by 1000 pixels
        time.sleep(1)  # Wait for new content to load
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

# Function to click the 'Next Page' button
def click_next_page(driver):
    try:
        next_button = driver.find_element(By.CSS_SELECTOR, 'button[aria-label="next page"]')
        ActionChains(driver).move_to_element(next_button).click().perform()
        time.sleep(3)
        return True
    except:
        print("No next page button found or end of pages reached.")
        return False

# Keep track of the product data
product_data = []
seen_links = set()

# Start time for limiting the scraping process to one minute
start_time = time.time()

# Loop to scrape pages until no more pages are available or 1 minute passes
while True:
    if time.time() - start_time > 60:
        break
    
    # Find all product card elements on the current page
    products = driver.find_elements(By.CSS_SELECTOR, 'div[data-test="@web/ProductCard/body"]')

    # Extract data from the products on the current page
    for product in products:
        try:
            link = product.find_element(By.CSS_SELECTOR, 'a[data-test="product-title"]')
            link_href = link.get_attribute('href') if link else 'No link available'
        except:
            link_href = 'No link available'

        if link_href in seen_links:
            continue
        seen_links.add(link_href)

        try:
            name = product.find_element(By.CSS_SELECTOR, 'a[data-test="product-title"]')
            product_name = name.text if name else 'No name available'
            product_name = product_name.split(' -')[0]
        except:
            product_name = 'No name available'

        try:
            price = product.find_element(By.CSS_SELECTOR, 'span[data-test="current-price"]')
            price_text = price.text if price else 'No price available'
        except:
            price_text = 'No price available'

        # Add store name and last checked timestamp
        store_name = "Target"  # Static since we know we're scraping Target
        last_checked_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Append product data to the list
        product_data.append({
            'id': len(product_data) + 1,  # Auto-increment ID
            'store_name': store_name,
            'product_name': product_name,
            'url': link_href,
            'price': price_text,
            'last_checked_at': last_checked_at
        })

    gradual_scroll_page(driver)

    if not click_next_page(driver):
        break

# Write the collected product data to a CSV file
csv_filename = 'scraped_products.csv'

# Define the CSV fieldnames
fieldnames = ['id', 'store_name', 'product_name', 'url', 'price', 'last_checked_at']

# Write the data to a CSV file
with open(csv_filename, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writeheader()
    for product in product_data:
        writer.writerow(product)

print(f"Scraped data has been saved to {csv_filename}")

# Close the driver
driver.quit()
