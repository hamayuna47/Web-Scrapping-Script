# print("Crawling and extraction completed.")
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import sys
import os
import re
import json
import time
from pymongo import MongoClient
import hashlib

# Function to generate SHA-256 hash
def generate_sha256(email, link):
    combined_string = f"{email}{link}"
    return hashlib.sha256(combined_string.encode()).hexdigest()

# Generate SHA-256 hash


# Check if sufficient arguments are provided
if len(sys.argv) < 3:
    print("Usage: process_link.py <email> <link>")
    sys.exit(1)

# Extract email and link from the arguments
recieved_email = sys.argv[1]
recieved_link = sys.argv[2]

# Initialize Selenium WebDriver
driver = webdriver.Chrome()

# Base URL of the website
base_url = recieved_link  # Replace with your starting URL
visited_links = set()
to_visit = [base_url]

# Output folder
output_folder = "output_data/"
os.makedirs(output_folder, exist_ok=True)

# Structure for storing all extracted data
all_extracted_data = {
    "pages": [],
    "contact_info": [],
    "company_overview": [],
    "service_info": [],
    "categories_and_subcategories": [],
    "customer_support_info": [],
    "legal_info": [],
    "news_and_updates": [],
    "upcoming_events": [],
    "portfolio": [],
    "employees_team": []
}

# MongoDB connection details
def connect_to_mongodb():
    client = MongoClient("mongodb+srv://hamayuna47:admin123@botnist.invud.mongodb.net/?retryWrites=true&w=majority&appName=botnist")
    db = client["botnistdata"]
    collection = db["data"]
    return collection



# Normalize a URL (remove fragments and resolve relative paths)
def normalize_url(url, base_url):
    parsed = urlparse(url)
    return urljoin(base_url, parsed.path)


# Save extracted data to a JSON and TXT file
def save_all_data():
    # Save to JSON
    json_path = os.path.join(output_folder, "all_data.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(all_extracted_data, f, indent=4, ensure_ascii=False)
    print(f"Data saved to JSON: {json_path}")

    # Save to TXT
    txt_path = os.path.join(output_folder, "all_data.txt")
    unique_lines = set()  # To avoid duplicate lines in the TXT file

    with open(txt_path, "w", encoding="utf-8") as f:
        for category, data in all_extracted_data.items():
            f.write(f"{category.upper()}:\n")
            f.write("=" * len(category) + "\n")
            if isinstance(data, list):
                for item in data:
                    if isinstance(item, dict):
                        # For dictionary items, write key-value pairs
                        for key, value in item.items():
                            line = f"{key}: {value}"
                            if line not in unique_lines:
                                f.write(f"{line}\n")
                                unique_lines.add(line)
                    else:
                        # For plain text items, ensure no duplicates
                        if item not in unique_lines:
                            f.write(f"{item}\n")
                            unique_lines.add(item)
            elif isinstance(data, str):
                # Write string content, line by line
                for line in data.splitlines():
                    line = line.strip()
                    if line and line not in unique_lines:
                        f.write(f"{line}\n")
                        unique_lines.add(line)
            f.write("\n")  # Separate categories
    print(f"Data saved to TXT: {txt_path}")



# Extract emails and phone numbers
def extract_emails_and_phones(soup):
    text = soup.get_text(separator="\n")
    emails = re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)
    phones = re.findall(r"\+?\d[\d\s\-()]{7,}", text)
    return list(set(emails)), list(set(phones))


# General function to extract specific categories of data
def extract_category_data(soup, category_keywords):
    category_data = []
    for keyword in category_keywords:
        elements = soup.find_all(string=re.compile(rf"{keyword}", re.IGNORECASE))
        for element in elements:
            parent = element.find_parent()
            if parent:
                category_data.append(parent.get_text(strip=True))
    return list(set(category_data))


# Crawl a single page
def crawl_page(url):
    try:
        driver.get(url)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        page_content = driver.find_element(By.TAG_NAME, "body").get_attribute("outerHTML")
        return page_content
    except Exception as e:
        print(f"Error crawling {url}: {e}")
        return None


# Extract data from a single page
def extract_data(url, html_content):
    try:
        soup = BeautifulSoup(html_content, "html.parser")

        # Clean irrelevant tags
        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()

        # Extract data
        text_content = soup.get_text(separator="\n", strip=True)
        emails, phones = extract_emails_and_phones(soup)

        # Define keywords for different domains
        domains_keywords = {
            "company_overview": ["about us", "company overview", "who we are"],
            "service_info": ["services", "solutions", "what we offer"],
            "categories_and_subcategories": ["categories", "subcategories", "industries"],
            "customer_support_info": ["customer support", "help", "contact us"],
            "legal_info": ["terms", "privacy", "legal"],
            "news_and_updates": ["news", "updates", "press"],
            "upcoming_events": ["events", "webinars", "calendar"],
            "portfolio": ["portfolio", "case studies", "projects"],
            "employees_team": ["team", "staff", "employees"]
        }

        # Extract and save category-specific data
        for domain, keywords in domains_keywords.items():
            extracted_data = extract_category_data(soup, keywords)
            if extracted_data:
                all_extracted_data[domain].extend(extracted_data)

        # Append general contact info
        if emails or phones:
            all_extracted_data["contact_info"].append({"emails": emails, "phones": phones})

        # Append raw page data
        all_extracted_data["pages"].append({
            "url": url,
            "content": text_content
        })

    except Exception as e:
        print(f"Error extracting data from {url}: {e}")


# Get all links on the page
def get_all_links(soup):
    links = []
    try:
        anchor_tags = soup.find_all("a", href=True)
        for tag in anchor_tags:
            href = tag["href"]
            normalized_link = normalize_url(href, base_url)
            if base_url in normalized_link and normalized_link not in visited_links:
                links.append(normalized_link)
    except Exception as e:
        print(f"Error extracting links: {e}")
    return links


# Main crawling loop
try:
    while to_visit:
        current_url = to_visit.pop(0)
        if current_url not in visited_links:
            sys.stdout.reconfigure(encoding='utf-8')
            print(f"Visiting: {current_url}")
            html_content = crawl_page(current_url)
            if html_content:
                # Parse HTML and extract data
                extract_data(current_url, html_content)

                # Mark URL as visited
                visited_links.add(current_url)

                # Get new links from the page
                soup = BeautifulSoup(html_content, "html.parser")
                new_links = get_all_links(soup)
                to_visit.extend(new_links)

    

finally:
    driver.quit()
    # Generate SHA-256 hash
    unique_hash = generate_sha256(recieved_email, recieved_link)

    website_name = recieved_link
    user_id = recieved_email
    website_link = recieved_link
    file_path ="C:/Users/hikn0//OneDrive/Desktop/folder/output_data/all_data.txt"
    collection = connect_to_mongodb()

    try:
        # Open and read the content of the txt file
        #with open(file_path, 'r', encoding='utf-8') as file:
        #file_content = file.read()
        # Prepare the document
        json_data = json.dumps(all_extracted_data, indent=4)

        # Save as a .txt file
        file_path = "extracted_data.txt"
        with open(file_path, "w") as file:
            file.write(json_data)

        with open(file_path, "r") as file:
            text_content = file.read()

        document = {
            
            "key": unique_hash,  # Include generated SHA-256 hash
            "text_data": text_content  # Include file content

        }

        # Insert data into MongoDB
        result = collection.insert_one(document)
        print(f"Data uploaded successfully with ID: {result.inserted_id}")
        # Print JSON output for Node.js
        print(json.dumps({"success": True, "data": unique_hash}), flush=True)

    except Exception as e:
        print(json.dumps({"success": False, "error": str(e)}), flush=True)