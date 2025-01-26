import os
import json
import pyodbc
import time
from dotenv import load_dotenv
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import re
import itertools
import sys

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
load_dotenv()
def get_connection():
    server = os.getenv('DB_SERVER')
    database = os.getenv('DB_DATABASE') 
    driver = os.getenv('DB_DRIVER', 'ODBC Driver 17 for SQL Server')
    username = os.getenv('DB_USERNAME')
    password = os.getenv('DB_PASSWORD')
    connection_string = (
        f'DRIVER={{{driver}}};'
        f'SERVER={server};'
        f'DATABASE={database};'
        f'UID={username};'
        f'PWD={password};'
    )
    try:
        conn = pyodbc.connect(connection_string)
        logging.info("Veritabanına başarıyla bağlanıldı.")
        return conn
    except pyodbc.Error as e:
        logging.error(f"Veritabanı bağlantı hatası: {e}")
        raise

def update_database(conn, item):
    cursor = conn.cursor()
    item_title = item.get('item_title')
    if not item_title:
        logging.warning("item_title eksik olan bir öğe atlanıyor.")
        return
    logging.info(f"İşleniyor: {item_title}")
    exterior = item.get('exterior')
    item_StatTrak = item.get('item_StatTrak', 0)
    item_price = item.get('item_price', 0.0)
    item_price_afterfee = item.get('item_price_afterfee', 0.0)
    item_order_price = item.get('item_order_price', 0.0)
    last_sold_price = item.get('last_sold_price', 0.0)
    last_sold_price_avg = item.get('last_sold_price_avg', 0.0)
    item_profit = item.get('item_profit', 0.0)
    price_stability = item.get('price_stability', 0.0)
    item_profit_percentage = item.get('item_profit_percentage', 0.0)

    try:
        item_StatTrak = int(item_StatTrak)
    except ValueError:
        logging.error(f"Veri tipi dönüşüm hatası için '{item_title}': 'item_StatTrak' geçersiz, 0 olarak ayarlandı.")
        item_StatTrak = 0
    try:
        item_price = float(item_price)
    except ValueError:
        logging.error(f"Veri tipi dönüşüm hatası için '{item_title}': 'item_price' geçersiz, 0.0 olarak ayarlandı.")
        item_price = 0.0
    try:
        item_price_afterfee = float(item_price_afterfee)
    except ValueError:
        logging.error(f"Veri tipi dönüşüm hatası için '{item_title}': 'item_price_afterfee' geçersiz, 0.0 olarak ayarlandı.")
        item_price_afterfee = 0.0
    try:
        item_order_price = float(item_order_price)
    except ValueError:
        logging.error(f"Veri tipi dönüşüm hatası için '{item_title}': 'item_order_price' geçersiz, 0.0 olarak ayarlandı.")
        item_order_price = 0.0
    try:
        last_sold_price = float(last_sold_price)
    except ValueError:
        logging.error(f"Veri tipi dönüşüm hatası için '{item_title}': 'last_sold_price' geçersiz, 0.0 olarak ayarlandı.")
        last_sold_price = 0.0
    try:
        last_sold_price_avg = float(last_sold_price_avg)
    except ValueError:
        logging.error(f"Veri tipi dönüşüm hatası için '{item_title}': 'last_sold_price_avg' geçersiz, 0.0 olarak ayarlandı.")
        last_sold_price_avg = 0.0
    try:
        item_profit = float(item_profit)
    except ValueError:
        logging.error(f"Veri tipi dönüşüm hatası için '{item_title}': 'item_profit' geçersiz, 0.0 olarak ayarlandı.")
        item_profit = 0.0
    try:
        price_stability = float(price_stability)
    except ValueError:
        logging.error(f"Veri tipi dönüşüm hatası için '{item_title}': 'price_stability' geçersiz, 0.0 olarak ayarlandı.")
        price_stability = 0.0
    try:
        item_profit_percentage = float(item_profit_percentage)
    except ValueError:
        logging.error(f"Veri tipi dönüşüm hatası için '{item_title}': 'item_profit_percentage' geçersiz, 0.0 olarak ayarlandı.")
        item_profit_percentage = 0.0

    update_sql = """
    UPDATE dbo.items SET
        exterior = ?,
        item_StatTrak = ?,
        item_price = ?,
        item_price_afterfee = ?,
        item_order_price = ?,
        last_sold_price = ?,
        last_sold_price_avg = ?,
        item_profit = ?,
        price_stability = ?,
        item_profit_percentage = ?,
        last_update_time = GETDATE()
    WHERE item_title = ?;
    """
    try:
        cursor.execute(update_sql, (
            exterior,
            item_StatTrak,
            item_price,
            item_price_afterfee,
            item_order_price,
            last_sold_price,
            last_sold_price_avg,
            item_profit,
            price_stability,
            item_profit_percentage,
            item_title
        ))
        if cursor.rowcount == 0:
            insert_sql = """
            INSERT INTO dbo.items (
                item_title,
                exterior,
                item_StatTrak,
                item_price,
                item_price_afterfee,
                item_order_price,
                last_sold_price,
                last_sold_price_avg,
                item_profit,
                price_stability,
                item_profit_percentage,
                last_update_time
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, GETDATE());
            """
            cursor.execute(insert_sql, (
                item_title,
                exterior,
                item_StatTrak,
                item_price,
                item_price_afterfee,
                item_order_price,
                last_sold_price,
                last_sold_price_avg,
                item_profit,
                price_stability,
                item_profit_percentage
            ))
            logging.info(f"Yeni öğe eklendi: {item_title}")
        else:
            logging.info(f"Öğe güncellendi: {item_title}")
    except pyodbc.Error as e:
        logging.error(f"SQL hatası için '{item_title}': {e}")
    conn.commit()

def scrape_and_update(item_link, driver, item_data, conn):
    try:
        logging.info(f"Scraping başlıyor: {item_link}")
        driver.get(item_link)
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, "market_commodity_orders_header_promote")))
        html_content = driver.page_source
        soup = BeautifulSoup(html_content, "html.parser")
        title_tag = soup.find("title")
        if title_tag:
            item_title = title_tag.text.split("for ")[-1].strip()
            exterior_match = re.search(r'\((.*?)\)', item_title)
            exterior = exterior_match.group(1) if exterior_match else "Not available"
            price_tags = soup.find_all("span", {"class": "market_listing_price market_listing_price_with_fee"})
            item_price = min([float(price.text.strip().replace('$', '').replace(',', '').replace(' USD', '').strip()) for price in price_tags]) if price_tags else "Not available"
            price_afterfee_tags = soup.find_all("span", {"class": "market_listing_price market_listing_price_without_fee"})
            item_price_afterfee = min([float(price.text.strip().replace('$', '').replace(',', '').replace(' USD', '').strip()) for price in price_afterfee_tags]) if price_afterfee_tags else "Not available"
            buy_request_tags = soup.find_all("span", {"class": "market_commodity_orders_header_promote"})
            if len(buy_request_tags) >= 2:
                item_order_price = float(buy_request_tags[1].text.strip().replace('$', '').replace(',', '')) if buy_request_tags[1].text.strip() else "Not available"
            else:
                item_order_price = "Not available"
            line1_match = re.search(r'var line1=\[(.*?)\];', html_content, re.DOTALL)
            if line1_match:
                line1_data = eval('[' + line1_match.group(1) + ']')
                last_sold_price = round(line1_data[-1][1], 2) if line1_data else "Not available"
                last_5_prices = [entry[1] for entry in line1_data[-5:]]
                last_sold_price_avg = round(sum(last_5_prices) / len(last_5_prices), 2) if last_5_prices else "Not available"
            else:
                last_sold_price = last_sold_price_avg = "Not available"
            item_StatTrak = 1 if "StatTrak" in item_title else 0
            item_profit = round(item_price_afterfee - item_order_price, 2) if isinstance(item_price_afterfee, (int, float)) and isinstance(item_order_price, (int, float)) else "Not available"
            if item_price != "Not available" and last_sold_price_avg != "Not available":
                price_stability = round((last_sold_price_avg / item_price) * 100, 2)
            else:
                price_stability = "Not available"
            if item_price != "Not available" and item_profit != "Not available":
                item_profit_percentage = round((item_profit / item_price) * 100, 2)
            else:
                item_profit_percentage = "Not available"
            new_item = {
                "item_title": item_title,
                "exterior": exterior,
                "item_StatTrak": item_StatTrak,
                "item_price": item_price,
                "item_price_afterfee": item_price_afterfee,
                "item_order_price": item_order_price,
                "last_sold_price": last_sold_price,
                "last_sold_price_avg": last_sold_price_avg,
                "item_profit": item_profit,
                "price_stability": price_stability,
                "item_profit_percentage": item_profit_percentage
            }
            updated = False
            for index, existing_item in enumerate(item_data):
                if isinstance(existing_item, dict) and existing_item.get("item_title") == item_title:
                    item_data[index] = new_item
                    updated = True
                    break
            if not updated:
                item_data.append(new_item)
            with open("item_data.json", "w", encoding="utf-8") as json_file:
                json.dump(item_data, json_file, indent=4, ensure_ascii=False)
            logging.info(f"Scraping tamamlandı: {item_link}")
            update_database(conn, new_item)
    except Exception as e:
        logging.error(f"Error occurred while scraping {item_link}: {str(e)}")

username = os.getenv("steam_username")
password = os.getenv("steam_password")
def main():
    try:
        conn = get_connection()
        driver = webdriver.Chrome()
        driver.get("https://store.steampowered.com/login/")
        wait = WebDriverWait(driver, 10)
        username_field = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='text']._2GBWeup5cttgbTw8FM3tfx")))
        username_field.send_keys(username)
        password_field = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='password']._2GBWeup5cttgbTw8FM3tfx")))
        password_field.send_keys(password)
        password_field.send_keys(Keys.RETURN)
        try:
            account_pulldown = wait.until(EC.presence_of_element_located((By.ID, "account_pulldown")))
            if account_pulldown.text.strip() == "2079python":
                logging.info("Başarıyla giriş yapıldı.")
            else:
                logging.error("Giriş başarısız. Hesap bilgileri uyuşmuyor.")
                driver.quit()
                conn.close()
                sys.exit(1)
        except Exception as e:
            logging.error(f"Giriş sırasında hata: {e}")
            driver.quit()
            conn.close()
            sys.exit(1)
        with open("item_details.json", "r", encoding="utf-8") as json_file:
            items = json.load(json_file)
        item_links = [item["item_link"] for item in items if "item_link" in item]
        if not item_links:
            logging.error("item_details.json dosyasında geçerli link bulunamadı.")
            driver.quit()
            conn.close()
            sys.exit(1)
        try:
            with open("item_data.json", "r", encoding="utf-8") as json_file:
                item_data = json.load(json_file)
                if not isinstance(item_data, list):
                    item_data = []
        except (FileNotFoundError, json.JSONDecodeError):
            item_data = []
        for item_link in itertools.cycle(item_links):
            scrape_and_update(item_link, driver, item_data, conn)
    except KeyboardInterrupt:
        logging.info("Kullanıcı tarafından durduruldu.")
    except Exception as e:
        logging.error(f"Genel hata: {e}")
    finally:
        driver.quit()
        conn.close()
        logging.info("Betiğin çalışması durduruldu.")

if __name__ == "__main__":
    main()
