# Web Scraper Script

## Overview
This web scraping script is designed to extract structured data from websites using Selenium and BeautifulSoup. It dynamically navigates web pages, extracts relevant information, and stores the results in a MongoDB database. The script efficiently processes different categories of data, such as company details, contact information, services, and legal information.

## Features
- **Automated Crawling**: Utilizes Selenium to navigate and extract web content.
- **Data Extraction**: Gathers emails, phone numbers, company information, services, legal details, and more.
- **MongoDB Integration**: Stores structured data in a MongoDB database.
- **SHA-256 Hashing**: Generates unique hashes for data integrity.
- **JSON & TXT Output**: Saves extracted data in structured JSON and human-readable TXT formats.
- **Dynamic Link Navigation**: Identifies and follows new links within the domain.

## Technologies Used
- **Python**: Core programming language.
- **Selenium**: Web automation for page navigation and content retrieval.
- **BeautifulSoup**: HTML parsing and data extraction.
- **MongoDB**: Database for storing extracted data.
- **Regular Expressions**: Extracts emails and phone numbers.
- **SHA-256 Hashing**: Ensures data uniqueness.

## Installation
1. Clone the repository:
   ```sh
   git clone https://github.com/yourusername/webscraper.git
   ```
2. Navigate to the project directory:
   ```sh
   cd webscraper
   ```
3. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
4. Ensure you have Chrome and ChromeDriver installed.

## Usage
Run the script using:
```sh
python process_link.py <email> <link>
```
Where:
- `<email>` is the user's email for data tracking.
- `<link>` is the starting URL to scrape.

## Output
- Extracted data is saved in:
  - **JSON format** (`output_data/all_data.json`)
  - **TXT format** (`output_data/all_data.txt`)
- Data is also stored in MongoDB under the `botnistdata` database.

## Future Enhancements
- Implement multi-threading for faster data collection.
- Add support for more complex websites with JavaScript-heavy content.
- Introduce an API to access scraped data programmatically.

---
Developed by Humayun Abdullah

