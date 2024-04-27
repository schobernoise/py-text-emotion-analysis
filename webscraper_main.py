import argparse
import csv
import os
import random
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from selenium import webdriver

# from selenium.webdriver.chrome.options import Options
from selenium.webdriver.firefox.options import Options
from datetime import datetime


# from PIL import Image
# from Screenshot import Screenshot_clipping
import string

current_datetime = datetime.now().strftime("%d%m%y-%H%M%S")


def scrape_url(url, visited_urls, save_html=False, save_screenshot=False):
    try:
        # Send a GET request to the URL
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for non-200 status codes
        # Parse the HTML content
        soup = BeautifulSoup(response.content, "html.parser")

        # Extract all links from the page
        links = soup.find_all("a", href=True)

        # Remove visited URLs from the links
        links = [link["href"] for link in links if link["href"] not in visited_urls]

        # Filter links to accept only those with "https://" prefix
        links = [
            link
            for link in links
            if link.startswith("https://")
            and not link.startswith("https://twitter.com")
        ]

        if not links:
            print("No new valid links found on this page.")
            return None

        # Choose a random link from the extracted links
        random_link = random.choice(links)

        # Convert relative links to absolute links
        random_link = urljoin(url, random_link)

        # Save HTML if save_html flag is True
        if save_html:
            save_html_file(response.content, url)

        # Save screenshot if save_screenshot flag is True
        if save_screenshot:
            save_screenshot_file(url)

        return random_link
    except Exception as e:
        print(f"Error occurred while scraping URL: {url}. Error: {e}")
        return None


def save_html_file(content, url):
    # Extract the domain from the URL to use as filename
    domain = url.split("//")[-1].split("/")[0]
    filename = f"{domain}.html"
    # Create a directory to save HTML files if it doesn't exist
    if not os.path.exists("html"):
        os.makedirs("html")
    # Save the HTML content to a file inside the "html" directory
    with open(os.path.join("html", current_datetime, filename), "wb") as file:
        file.write(content)


def save_screenshot_file(url):
    try:
        # Set up Selenium options
        options = Options()
        options.add_argument(
            "--headless"
        )  # Run Chrome in headless mode (without opening browser window)
        # options.add_argument(
        #     "--disable-gpu"
        # )  # Disable GPU acceleration to prevent errors on some systems
        # Initialize Chrome WebDriver
        driver = webdriver.Firefox(options=options)

        # Set window size (required for headless mode)
        # driver.set_window_size(width=1920, height=1080)
        # Load the URL and take a screenshot
        driver.get(url)
        page_width = driver.execute_script("return document.body.offsetWidth")
        page_height = driver.execute_script("return document.body.scrollHeight")
        screenshot_filename = f"{url.replace('https://', '').replace('www', '').replace('/', '_').replace('http://', '').replace('.', '_')}.png"
        driver.set_window_size(page_width, page_height)
        print(
            os.path.join(
                "screenshots", str(current_datetime), screenshot_filename
            ).replace("\\", "/")
        )
        # Save the screenshot
        try:
            driver.save_screenshot(
                os.path.join(
                    "screenshots", str(current_datetime), screenshot_filename
                ).replace("\\", "/")
            )
            # driver.save_screenshot(
            #     f"D:/DEV/Mengele Zoo/py-text-emotion-analysis/screenshots/{current_datetime}/{screenshot_filename}"
            # )
        except:
            print("Didn't save screenshot")
        # Close the WebDriver
        print(f"Screenshot saved for URL: {url}")
        driver.quit()
    except Exception as e:
        print(f"Error occurred while saving screenshot for URL: {url}. Error: {e}")
        pass


def generate_random_url(retries=3):
    for _ in range(retries):
        try:
            # Fetch a random word using random-word-api
            response = requests.get("https://random-word-api.herokuapp.com/word")
            response.raise_for_status()  # Raise an exception for non-200 status codes
            random_word = response.json()[
                0
            ]  # Extract the random word from the response

            # Perform a Qwant search using the random word
            headers = {
                "User-Agent": "Mozilla/5.0 (Linux; Android 10; HD1913) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.105 Mobile Safari/537.36 EdgA/46.1.2.5140"
            }
            params = {"q": random_word, "t": "web"}
            html = requests.get(
                "https://www.qwant.com/", params=params, headers=headers, timeout=20
            )
            soup = BeautifulSoup(html.text, "html.parser")

            # Extract search results
            search_results = soup.find_all("a", class_="external")

            # If there are search results, choose a random URL from them
            if search_results:
                random_search_result = random.choice(search_results)
                random_url = random_search_result.get("href")
                return random_url
            else:
                print("No search results found. Retrying with a new random word...")
        except Exception as e:
            print(f"Error occurred while generating random URL: {e}")
            print("Retrying...")
    print("Max retries reached, unable to generate random URL.")
    return None


def crawl(start_url, limit, save_html=False, save_screenshot=False):
    visited_urls = set()
    visited_urls.add(start_url)

    while True:
        csv_filename = f"crawled_urls_{current_datetime}.csv"
        if os.path.exists(os.path.join("csv", csv_filename)):
            version_number += 1
        else:
            break

    # Create a CSV file for logging crawled URLs
    with open(os.path.join("csv", csv_filename), "w", newline="") as csvfile:
        fieldnames = ["URL"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for _ in range(limit):
            # Scrape the current URL
            next_url = scrape_url(start_url, visited_urls, save_html, save_screenshot)
            if next_url:
                # Write the crawled URL to the CSV file
                writer.writerow({"URL": start_url})
                # Print the crawled URL
                print(f"Crawled URL: {start_url}")
                # Update the start_url for the next iteration
                start_url = next_url
                # Add the crawled URL to the visited_urls set
                visited_urls.add(start_url)
            else:
                print("No new links found on this page, trying to find a random URL.")
                # Try to find a random URL by guessing
                random_url = generate_random_url()
                while random_url in visited_urls:
                    random_url = generate_random_url()
                next_url = scrape_url(
                    random_url, visited_urls, save_html, save_screenshot
                )
                if next_url:
                    # Write the crawled URL to the CSV file
                    writer.writerow({"URL": random_url})
                    # Print the crawled URL
                    print(f"Crawled URL: {random_url}")
                    # Update the start_url for the next iteration
                    start_url = next_url
                    # Add the crawled URL to the visited_urls set
                    visited_urls.add(start_url)
                else:
                    print("Failed to find a random URL, generating a new one.")
                    pass

        version_number += 1


def main():
    parser = argparse.ArgumentParser(description="Web scraper CLI tool")
    parser.add_argument(
        "--auto-crawl",
        action="store_true",
        help="Ignore provided URL and auto-generate URL",
    )
    parser.add_argument("url", nargs="?", default=None, help="URL to start scraping")
    parser.add_argument(
        "--limit",
        type=int,
        default=5,
        help="Limit for how often the scraping loop should run",
    )
    parser.add_argument(
        "--save-html", action="store_true", help="Save HTML version of the site"
    )
    parser.add_argument(
        "--save-screenshot",
        action="store_true",
        help="Save screenshot of every crawled URL",
    )
    args = parser.parse_args()

    if args.auto_crawl:
        start_url = generate_random_url()
    else:
        start_url = args.url

    if start_url is None:
        print("No URL provided. Use --auto-crawl or provide a URL.")
        return

    crawl(start_url, args.limit, args.save_html, args.save_screenshot)


if __name__ == "__main__":
    main()
