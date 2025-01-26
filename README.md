Steam CS2 Item Scraper

Overview
--------
Steam Item Scraper is a Python-based tool designed to automatically scrape item details from the Steam Store. 
It collects essential data such as item prices, statistics, and other relevant information, then stores the data either in a SQL database or a JSON file based on your configuration.

Features
--------
- **Automated Scraping:** Utilizes Selenium and BeautifulSoup to navigate and extract data from Steam item pages.
- **Data Storage Options:** Choose between storing data in a SQL Server database or a JSON file.
- **Configurable Settings:** Easily toggle between database and JSON storage using a configuration file.
- **Robust Error Handling:** Logs detailed information and errors for easy debugging and maintenance.
- **Continuous Monitoring:** Continuously cycles through item links to keep the data up-to-date.

Usage
-----
1. **Clone the Repository and Configure Environment:**
- Clone the repository and navigate to its directory:
  ```
  git clone https://github.com/muakyz/steam-csgo-market-price-tracker.git
  ```
- Create a `.env` file based on the sample provided and fill in your own credentials.

2. **Prepare Item Details:**
- Fill in the `item_details.json` file as shown in the example. Providing only the `item_link` data is sufficient.
- The example file includes all knives and gloves in the CSGO market; you can use it if desired.

3. **Run the Script:**
  - python itempage.py

4. **Check Results:**
- Depending on your configuration, check your database or the `item_data.json` file for the results.
