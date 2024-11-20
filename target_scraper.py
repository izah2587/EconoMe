import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
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
    # Scroll down in small increments
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollBy(0, 1000);")  # Scroll down by 1000 pixels
        time.sleep(1)  # Wait for new content to load
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break  # If the height is the same, we've reached the bottom
        last_height = new_height

# Function to click the 'Next Page' button
def click_next_page(driver):
    try:
        # Locate the "Next Page" button by its data-test attribute or aria-label
        next_button = driver.find_element(By.CSS_SELECTOR, 'button[aria-label="next page"]')
        ActionChains(driver).move_to_element(next_button).click().perform()
        time.sleep(3)  # Wait for the next page to load
        return True
    except:
        print("No next page button found or end of pages reached.")
        return False

# Keep track of the product data
product_data = []
seen_links = set()  # Set to keep track of product links to prevent duplicates

# Start time for limiting the scraping process to one minute
start_time = time.time()

# Loop to scrape pages until no more pages are available or 1 minute passes
while True:
    # Stop the loop after one minute
    if time.time() - start_time > 60:  # 60 seconds
        break
    
    # Find all product card elements on the current page
    products = driver.find_elements(By.CSS_SELECTOR, 'div[data-test="@web/ProductCard/body"]')

    # Extract data from the products on the current page
    for product in products:
        # Extract product link (if available)
        try:
            link = product.find_element(By.CSS_SELECTOR, 'a[data-test="product-title"]')
            link_href = link.get_attribute('href') if link else 'No link available'
        except:
            link_href = 'No link available'

        # Skip this product if we've already added it based on the link
        if link_href in seen_links:
            continue  # Skip this product if already added
        seen_links.add(link_href)

        # Extract product name (if available)
        try:
            name = product.find_element(By.CSS_SELECTOR, 'a[data-test="product-title"]')
            product_name = name.text if name else 'No name available'
            product_name = product_name.split(' -')[0]
        except:
            product_name = 'No name available'

        try:
            # Extract price (if available)
            price = product.find_element(By.CSS_SELECTOR, 'span[data-test="current-price"]')
            price_text = price.text if price else 'No price available'
        except:
            price_text = 'No price available'

        # Append the extracted product data to the list
        product_data.append({
            'name': product_name,
            'price': price_text,
            'url': link_href
        })

    # Gradually scroll the page to the bottom
    gradual_scroll_page(driver)

    # Try to click the next page and load more products
    if not click_next_page(driver):
        break  # Stop the loop if there is no next page

# Write the collected product data to a CSV file
csv_filename = 'scraped_products.csv'

# Define the CSV fieldnames
fieldnames = ['name', 'price', 'url']

# Open the CSV file in write mode and write the data
with open(csv_filename, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    
    # Write the header (field names)
    writer.writeheader()
    
    # Write the product data rows
    for product in product_data:
        writer.writerow(product)

# Print a confirmation message
print(f"Scraped data has been saved to {csv_filename}")

# Close the driver
driver.quit()
