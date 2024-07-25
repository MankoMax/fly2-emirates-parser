import json
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time
from bs4 import BeautifulSoup
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# You should use your own version of the driver
DRIVER_VERSION = 126


class EmiratesFlightParser:
    def __init__(self,
                 user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"):
        options = uc.ChromeOptions()
        options.add_argument(f"user-agent={user_agent}")
        self.driver = uc.Chrome(options=options, version_main=DRIVER_VERSION)
        self.wait = WebDriverWait(self.driver, 20)

    def open_start_page(self):
        try:
            self.driver.get("https://fly2.emirates.com/CAB/IBE/SearchAvailability.aspx")
            self._accept_cookies()
            self._handle_session_expired()
        except Exception as e:
            logger.error(f"Error opening the start page: {e}")

    def _accept_cookies(self):
        try:
            trust_button = self.wait.until(EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler")))
            trust_button.click()
        except Exception as e:
            logger.error(f"Error accepting cookies: {e}")

    def _handle_session_expired(self):
        try:
            session_expire_button = self.wait.until(
                EC.element_to_be_clickable((By.CLASS_NAME, "ts-session-expire--link")))
            session_expire_button.click()
        except Exception as e:
            logger.error(f"Error handling session expiration: {e}")

    def search_flights(self, start_city, destination_city, travel_date):
        self.open_start_page()
        self._select_one_way()
        self._enter_city(start_city, "ctl00_c_CtWNW_ddlFrom-suggest")
        self._enter_city(destination_city, "ctl00_c_CtWNW_ddlTo-suggest")
        self._enter_date(travel_date)
        self._click_search()

        return self._parse_results()

    def _select_one_way(self):
        try:
            oneway_radio_button = self.wait.until(EC.element_to_be_clickable((By.ID, "dvRadioOneway")))
            oneway_radio_button.click()
        except Exception as e:
            logger.error(f"Error selecting one way flight: {e}")

    def _enter_city(self, city_name, element_id):
        try:
            city_input = self.wait.until(EC.element_to_be_clickable((By.ID, element_id)))
            city_input.clear()
            city_input.send_keys(city_name)

            time.sleep(2)

            city_input.send_keys(Keys.ENTER)
        except Exception as e:
            logger.error(f"Error entering city: {e}")

    def _enter_date(self, travel_date):
        try:
            date_input = self.wait.until(EC.element_to_be_clickable((By.ID, "txtDepartDate")))
            self.driver.execute_script(f"arguments[0].value = '{travel_date}';", date_input)

            time.sleep(2)
        except Exception as e:
            logger.error(f"Error entering date: {e}")

    def _click_search(self):
        try:
            search_button = self.wait.until(EC.element_to_be_clickable((By.ID, "ctl00_c_IBE_PB_FF")))
            self.driver.execute_script("arguments[0].click();", search_button)
            self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "flights-row")))
        except Exception as e:
            logger.error(f"Error clicking search: {e}")

    def _parse_results(self):
        page_source = self.driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        flights = []
        results = soup.find_all(class_='flights-row')

        if not results:
            logger.error("No results found")
            return flights

        logger.info(f"Found {len(results)} results")

        for result in results:
            try:
                flight_time = result.find_all('time')[-1].get_text().strip().replace('Duration\n\n\n', '')
                flight_cost = \
                    result.find(class_='carrier-imposed-curr carrier-imposed-span').get_text().strip().replace(',', '')
                flight_connections = result.find(class_='ts-fid__value').get_text().strip().split('\xa0')[0]
                flight_class = result.find(class_='ts-fid__value ts-fid__value--ellipsis').get_text().strip()

                flights.append(
                    {'flight time': flight_time,
                     'flight cost': flight_cost,
                     'flight connections': flight_connections,
                     'flight class': flight_class}
                )
            except Exception as e:
                logger.error(f"Error parsing flight: {e}")

        return flights

    def quit(self):
        self.driver.quit()

    def save_results(self, flight_results, filename='output.json'):
        with open(filename, 'w') as f:
            json.dump(flight_results, f, indent=4)


if __name__ == "__main__":
    # departure_airport = "East London (ELS)"
    # arrival_airport = "Abu Dhabi (BUS) (ZVJ)"
    # travel_date = "26-07-2024"

    departure_airport = input("Enter the departure airport (e.g. East London (ELS)): ")
    arrival_airport = input("Enter the arrival airport (e.g. Abu Dhabi (BUS) (ZVJ)): ")
    travel_date = input("Enter the travel date (e.g. 26-07-2024): ")

    parser = EmiratesFlightParser()
    flight_results = parser.search_flights(departure_airport, arrival_airport, travel_date)
    logger.info(flight_results)
    parser.save_results(flight_results)
    parser.quit()
