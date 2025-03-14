import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime

def bank_indonesia(content):
    """
    Parses and processes exchange rate data from Bank Indonesia.
    Saves the data into a CSV file.
    """
    soup = BeautifulSoup(content, "xml")
    tables = soup.find_all("Table")

    data = []
    for table in tables:
        exchangerate_data = {
            "Currency": table.find("mts_subkursasing").text if table.find("mts_subkursasing") else None,
            "Buy Rate": table.find("beli_subkursasing").text if table.find("beli_subkursasing") else None,
            "Sell Rate": table.find("jual_subkursasing").text if table.find("jual_subkursasing") else None,
        }
        data.append(exchangerate_data)

    # Convert the data into a DataFrame and save to CSV
    df = pd.DataFrame(data)
    df['Currency'] = df['Currency'].str.strip()
    df.to_csv("bank_indonesia_exchange_rates.csv", index=False)
    print("Data saved to bank_indonesia_exchange_rates.csv")

def bank_central_asia(content):
    """
    Parses and processes exchange rate data from Bank Central Asia.
    Saves the data into a CSV file.
    """
    soup = BeautifulSoup(content, "html.parser")
    table = soup.find("table", class_="m-table-kurs m-table--sticky-first-coloumn m-table-kurs--pad")

    if not table:
        print("Exchange rate table not found on the BCA website.")
        return

    rows = table.tbody.find_all("tr")

    data = []
    for row in rows:
        cells = row.find_all("td")
        if len(cells) >= 3:  # Ensure there are enough cells in the row
            try:
                exchangerate_data = {
                    "Currency": cells[0].get_text(strip=True),
                    "Buy Rate": float(cells[1].get_text(strip=True).replace(",", "")),  # Convert to float
                    "Sell Rate": float(cells[2].get_text(strip=True).replace(",", "")),  # Convert to float
                }
                data.append(exchangerate_data)
            except ValueError as e:
                print(f"Error converting rates to float: {e}")
                continue  # Skip rows with invalid data

    # Convert the data into a DataFrame and save to CSV
    df = pd.DataFrame(data)
    df.to_csv("bank_central_asia_exchange_rates.csv", index=False)
    print("Data saved to bank_central_asia_exchange_rates.csv")

def main():
    """
    Main function to get exchange rate data based on the selected bank.
    """
    print("Available banks: BI (Bank Indonesia), BCA (Bank Central Asia)")
    bank_name = input("Enter the bank name to check exchange rates: ").strip().lower()

    # Get the current date formatted as "YYYY-MM-DD"
    formatted_date = datetime.now().strftime("%Y-%m-%d")

    # Map bank names to their respective URLs
    url_mapping = {
        "bi": f"https://www.bi.go.id/biwebservice/wskursbi.asmx/getSubKursAsing2?tgl={formatted_date}",
        "bca": "https://www.bca.co.id/id/informasi/kurs",
    }

    # Retrieve the appropriate URL
    url = url_mapping.get(bank_name)
    if not url:
        print("Invalid bank name. Please choose between BI and BCA.")
        return

    # Send GET request to the selected bank's URL
    response = requests.get(url)

    if response.status_code == 200:
        # Map functions to their respective banks
        functions = {
            "bi": bank_indonesia,
            "bca": bank_central_asia,
        }

        # Call the corresponding function to process the data
        func = functions.get(bank_name)
        func(response.content)
    else:
        print(f"Failed to retrieve data. Status code: {response.status_code}")

if __name__ == "__main__":
    main()