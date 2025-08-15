"""

A small Python script for getting KRA access token and checking if a KRA PIN is 
valid using the sandbox API

"""

import requests
from requests.auth import HTTPBasicAuth


# --- Configuration ---
CONSUMER_SECRET = ''
CONSUMER_KEY = ''
TOKEN_URL = 'https://sbx.kra.go.ke/v1/token/generate?grant_type=client_credentials'
PIN_CHECKER_URL = 'https://sbx.kra.go.ke/checker/v1/pinbypin'


class KRAPinChecker:
    """Client for interacting with KRA's API (Token generation & PIN validation)."""

    def __init__(self, consumer_key: str, consumer_secret: str):
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret

    def get_access_token(self):
        try:
            response = requests.get(
                TOKEN_URL,
                auth=HTTPBasicAuth(self.consumer_key, self.consumer_secret),
                timeout=10,
            )
            response.raise_for_status()
            token_data = response.json()
            return token_data['access_token']

        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Failed to get access token: {e}")

        except ValueError:
            print("[ERROR] Failed to parse access token response as JSON.")

        return None

    def check_pin(self, kra_pin: str):
        """Validate a KRA PIN and return the parsed response."""

        token = self.get_access_token()
        if not token:
            print("[ERROR] Cannot check PIN without access token.")
            return None

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}',
        }

        payload = {"KRAPIN": kra_pin}

        try:
            response = requests.post(PIN_CHECKER_URL, json=payload, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()

            # If there's an error in the response
            if "ErrorMessage" in data:
                print(f"[ERROR] API Error: {data['ErrorMessage']}")
                return None
            return data

        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Failed to call PIN checker: {e}")
        except ValueError:
            print("[ERROR] Failed to parse PIN checker response as JSON.")
        return None


def print_pin_details(pin_data):
    """Pretty-print KRA PIN details."""
    try:
        print(f"Message: {pin_data.get('Message')}")
        pindata = pin_data.get("PINDATA", {})
        print(f"PIN: {pindata.get('KRAPIN')}")
        print(f"PIN Type: {pindata.get('TypeOfTaxpayer')}")
        print(f"Full Name: {pindata.get('Name')}")
        print(f"Status: {pindata.get('StatusOfPIN')}")
    except Exception as e:
        print(f"[ERROR] Failed to print PIN details: {e}")


if __name__ == "__main__":
    kra = KRAPinChecker(CONSUMER_KEY, CONSUMER_SECRET)
    result = kra.check_pin("A744610021G")
    if result:
        print_pin_details(result)
