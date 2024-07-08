import os
import requests
import re
import time
import pickle
import time
from apprise import Apprise

# File to persist notified products
PERSISTENCE_FILE = '/config/notified_products.pkl'

# Function to fetch data from the API
def fetch_data(api_url):
    response = requests.get(api_url)
    return response.json()

# Function to parse raw data for sale details
def parse_raw_data(raw):
    sale_match = re.search(r'(\d+,\d{2}) €', raw)
    duration_match = re.search(r'noch (\d+) Tag', raw)
    
    if sale_match and duration_match:
        sale_price = sale_match.group(1)
        days_left = duration_match.group(1)
        return sale_price, days_left
    return None, None

# Function to send notification using Apprise
def send_notification(name, price, days_left):
    apobj = Apprise()
    # Add notification service URLs from the environment variable
    apprise_urls = os.getenv('APPRISE_URLS')
    if apprise_urls:
        for url in apprise_urls.split(','):
            apobj.add(url.strip())
    
    title = "" 
    body = f"Rum ist die nächsten {days_left} Tage bei {name} für {price}€ im Angebot!" 

    apobj.notify(
        body=body,
        title=title
    )

# Function to load notified products from a file
def load_notified_products(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'rb') as file:
            return pickle.load(file)
    return set()

# Function to save notified products to a file
def save_notified_products(notified_products, file_path):
    with open(file_path, 'wb') as file:
        pickle.dump(notified_products, file)

# Main function
def main(check_interval=3600):
    api_url = os.getenv('API_URL')
    if not api_url:
        raise ValueError("API_URL environment variable is not set")
    notified_products = load_notified_products(PERSISTENCE_FILE)
    
    while True:
        data = fetch_data(api_url)
        current_sales = set()
        
        for item in data:
            if item['status'] == 'im angebot' and item['name'] in ["Aldi Süd", "Hit", "Kaufland", "Lidl", "Metro", "Netto Marken-Discount", "Norma", "Penny", "Rewe", "Tegut", "V-Markt"]:
                price, days_left = parse_raw_data(item['raw'])
                product_identifier = (item['name'], price)
                current_sales.add(product_identifier)
                
                if price and days_left and product_identifier not in notified_products:
                    send_notification(item['name'], price, days_left)
                    notified_products.add(product_identifier)
        
        # Remove products from notified_products if their sale has ended
        notified_products = notified_products.intersection(current_sales)
        save_notified_products(notified_products, PERSISTENCE_FILE)
        
        # Wait for the next check
        time.sleep(check_interval)


# Run the main function
if __name__ == '__main__':
    main()

