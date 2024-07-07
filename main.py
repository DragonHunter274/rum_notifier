import os
import requests
import re
import time
from apprise import Apprise

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
    print(apprise_urls)
    if apprise_urls:
        for url in apprise_urls.split(','):
            apobj.add(url.strip())
    
    message = f"Rum ist die naechsten {days_left} Tage bei {name} fuer {price}EUR im Angebot!"
    apobj.notify(
        body=message,
        title=""
    )

# Main function
def main(api_url, check_interval=3600):
    notified_products = set()
    
    while True:
        data = fetch_data(api_url)
        
        for item in data:
            if item['status'] == 'im angebot':
                price, days_left = parse_raw_data(item['raw'])
                product_identifier = (item['name'], price, days_left)
                
                if price and days_left and product_identifier not in notified_products:
                    send_notification(item['name'], price, days_left)
                    notified_products.add(product_identifier)
        
        # Wait for the next check
        time.sleep(check_interval)

# URL of your API
api_url = 'https://rum.dh274.com'

# Run the main function
if __name__ == '__main__':
    main(api_url)

