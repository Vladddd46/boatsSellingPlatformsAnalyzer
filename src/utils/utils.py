import os
import json
from datetime import datetime
import requests

def is_file_exist(path):
    return os.path.exists(path)


# Define a custom JSON encoder for datedime
class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            # Convert datetime object to ISO format string
            return obj.isoformat()
        return super().default(obj)


# Custom JSON Decoder for handling datetime objects
def datetime_decoder(dct):
    for key, value in dct.items():
        if isinstance(value, str):
            try:
                # Try to parse the datetime string back to datetime object
                dct[key] = datetime.fromisoformat(value)
            except ValueError:
                pass  # If the string is not in datetime format, leave it as is
    return dct


def save_json_data(path, data):
    with open(path, "w") as json_file:
        json.dump(data, json_file, indent=4, cls=DateTimeEncoder)


def read_json_file(path):
    with open(path, "r") as json_file:
        json_data = json.load(json_file, object_hook=datetime_decoder)
    return json_data


def convert_strdate_to_date(date_string):
    return datetime.strptime(date_string, "%d.%m.%Y").date()


# converts other currencies to euro based on curreng exchange rate.
def convert_to_euro(currency: str, amount: float) -> float:
    def fetch_exchange_rates(base_currency: str = "EUR"):
        url = f"https://api.exchangerate-api.com/v4/latest/{base_currency}"
        
        response = requests.get(url)
        if response.status_code != 200:
            raise Exception(f"Error fetching exchange rates: {response.status_code}")
        
        return response.json()["rates"]

    try:
        if is_file_exist("data/exchange_rates.json") == True:
            rates = read_json_file("data/exchange_rates.json")
        else:
            rates = fetch_exchange_rates("EUR")
            save_json_data("data/exchange_rates.json", rates)
        
        currency = currency.upper()
        
        if currency not in rates:
            return 0
            # raise ValueError(f"Unsupported currency: {currency}")
        
        euro_amount = amount / rates[currency]
        return euro_amount
    except:
        return 0
