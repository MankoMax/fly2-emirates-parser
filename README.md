# Emirates Flight Parser

This script automates the process of searching for one-way flights on the https://fly2.emirates.com/ using Selenium and BeautifulSoup. Users can input the departure city, destination city, and travel date through the console, and the script will fetch flight details and save them in a `.json` output file.

## Requirements

- Python 3.10
- `undetected-chromedriver`
- `selenium`
- `beautifulsoup4`

## Installation

1. **Create and activate a virtual environment (poetry):**
    ```sh
    poetry shell
    ```

3. **Install the required packages:**
    ```sh
    poetry install
    ```

## Usage

1. **Run the script:**
    ```sh
    python main.py
    ```

2. **Enter the required information when prompted:**
    - Departure city
    - Destination city
    - Travel date (in the format DD-MM-YYYY)

3. **Check the `output.json` file for the results.**

## Example

After running the script, you will be prompted to enter the required details:

```sh
    departure_airport = "East London (ELS)"
    arrival_airport = "Abu Dhabi (BUS) (ZVJ)"
    travel_date = "26-07-2024"
