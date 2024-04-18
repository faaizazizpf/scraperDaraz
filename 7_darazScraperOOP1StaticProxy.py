from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json
import pandas as pd
import os
from urllib.parse import urlparse, unquote
from random import randint
from time import sleep

class DarazScraper:
    def __init__(self, driver_path, urls, proxy=None, screenshot_dir=None, output_dir=None):
        self.driver_path = driver_path
        self.urls = urls
        self.proxy = proxy
        self.screenshot_dir = screenshot_dir
        self.output_dir = output_dir if output_dir else os.getcwd()
        self.driver = None

    def init_webdriver(self):
        chrome_options = webdriver.ChromeOptions()
        # chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920x1080')
        if self.proxy:
            chrome_options.add_argument(f'--proxy-server={self.proxy}')

        webdriver_service = Service(self.driver_path)
        self.driver = webdriver.Chrome(service=webdriver_service, options=chrome_options)

    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from time import sleep
    from random import randint

    def scrape_sites(self):
        for url in self.urls:
            page_number = 1
            consecutive_failures = 0
            while True:
                paginated_url = f"{url}?page={page_number}"
                sleep(randint(3, 33))
                self.driver.get(paginated_url)
                # self.driver.get("https://whatismyipaddress.com/")
                # sleep(randint(32, 33))

                try:
                    # Assuming presence_of_element_located is a way to ensure the page has fully loaded.
                    element_present = EC.presence_of_element_located(
                        (By.XPATH, '//*[@id="topActionHeader"]/div[1]/div[2]/div/div[1]'))
                    WebDriverWait(self.driver, 10).until(element_present)
                    html_content = self.driver.page_source
                    extracted_json = self.extract_js_object_from_html(html_content)

                    if not extracted_json or 'listItems' not in extracted_json.get('mods', {}):
                        print(f"No more data found on page {page_number} for {url}.")
                        self.take_screenshot(page_number)
                        consecutive_failures += 1
                    else:
                        # Process the page as normal
                        self.extract_data_and_write_to_excel(extracted_json, url, page_number)
                        consecutive_failures = 0  # Reset on successful data extraction

                except Exception as e:
                    print(f"Exception occurred while loading page {page_number} of {url}: {e}")
                    consecutive_failures += 1

                if consecutive_failures >= 3:
                    print(f"Moving to next URL after 3 consecutive failures on {url}.")
                    self.take_screenshot(page_number)
                    with open("downloaded_urls", "a") as file:  # 'a' mode for appending to the file
                        file.write(f"{url}\n")  # Append the URL and a note

                    break  # Exit the while loop to process next URL
                print(paginated_url)
                page_number += 1  # Attempt the next page

    def take_screenshot(self, page_number):
        screenshot_path = os.path.join(self.screenshot_dir, f"screenshot_{page_number}.png")
        self.driver.save_screenshot(screenshot_path)
        print(f"Saved screenshot as {screenshot_path}")

    def extract_js_object_from_html(self, html_content):
        start_phrase = "window.pageData="
        end_phrase = "}</script>"
        start_index = html_content.find(start_phrase)
        end_index = html_content.find(end_phrase, start_index)
        if start_index != -1 and end_index != -1:
            js_data = html_content[start_index + len(start_phrase):end_index + 1]
            return json.loads(js_data)
        else:
            print("The specified script section was not found.")
            return None

    def extract_data_and_write_to_excel(self, extracted_json, url, page_number):
        list_items = extracted_json.get('mods', {}).get('listItems', [])
        if list_items:
            extracted_data = [{
                'nid': item.get('nid', ''),
                'name': item.get('name', ''),
                'ratingScore': item.get('ratingScore', ''),
                'review': item.get('review', ''),
                'soldNum': item.get('soldInfo', {}).get('soldNum', '').replace(' Sold', ''),
                'priceShow': item.get('priceShow', ''),
            } for item in list_items]
            df = pd.DataFrame(extracted_data)

            # Parse the URL and extract a meaningful part for the filename
            parsed_url = urlparse(url)
            # Example: Extract the last part of the path and replace unwanted characters
            url_name = parsed_url.path.split('/')[-1] or parsed_url.path.replace('/', '_')
            url_name = unquote(url_name).replace('-', '_')

            if not url_name:  # Fallback in case URL does not have a path
                url_name = "unknown"

            filename = f"{url_name}_page_{page_number}.xlsx"
            # print(f"{url_name}_page_{page_number}")
            excel_path = os.path.join(self.output_dir, filename)
            df.to_excel(excel_path, index=False)
            print(f"Excel file for page {page_number} of {url} has been created at: {excel_path}")

    def quit_driver(self):
        self.driver.quit()


# Example usage
if __name__ == "__main__":
    urls_file = r'C:\Users\faaiz\darazScrape\scraping\approach2\urlsDaraz'
    with open(urls_file, 'r') as file:
        urls = file.read().splitlines()

    # print("Using Selenium in headless mode")
    proxy_address = "http://203.166.138.176:48905"
    screenshot_dir = r'C:\Users\faaiz\darazScrape\scraping\approach2'
    output_dir = r'C:\Users\faaiz\darazScrape\scraping\approach2'

    scraper = DarazScraper(driver_path=r'C:\Users\faaiz\darazScrape\scraping\chromedriver.exe',
                           urls=urls,
                           proxy=proxy_address,
                           screenshot_dir=screenshot_dir,
                           output_dir=output_dir
                           )
    scraper.init_webdriver()
    scraper.scrape_sites()
    scraper.quit_driver()
