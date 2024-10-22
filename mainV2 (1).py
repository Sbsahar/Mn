import os
import time
import random
import asyncio
import cloudscraper
import requests
from colorama import Fore, Style, init
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from telethon import TelegramClient
from telethon.errors import PhoneNumberBannedError, FloodWaitError, PhoneNumberFloodError

init()  # Initialize colorama for colored terminal output


class Numero:
    def __init__(self):
        self.api_id = '20221248'
        self.api_hash = 'eefd535340bd8c6c93a870a25327448b'
        self.scraper = cloudscraper.create_scraper()
        self.token = input('Enter your token: ')
        self.chat_id = input('Enter your chat id: ')
        self.proxy_list = self.load_proxies('proxies.txt')
        try:
            os.mkdir('Sessions')
        except FileExistsError:
            pass

    def load_proxies(self, proxy_file):
        """Load proxies from a file into a list."""
        with open(proxy_file, 'r') as f:
            proxies = [line.strip() for line in f.readlines()]
        return proxies

    def get_random_proxy(self):
        """Retrieve a random proxy from the proxy list."""
        if not self.proxy_list:
            raise Exception("No proxies available")
        return random.choice(self.proxy_list)

    def set_proxy(self):
        """Set a random proxy for the scraper."""
        proxy = self.get_random_proxy()
        self.scraper.proxies = {'https': f'http://lmmjtmxg:byiwhak7bncf@{proxy}'}
        return proxy

    def send_telegram(self, message):
        """Send a message to Telegram."""
        url = f"https://api.telegram.org/bot{self.token}/sendMessage?chat_id={self.chat_id}&text={message}"
        requests.get(url)

    async def check_multiple_numbers(self, numbers):
        """Check multiple phone numbers concurrently."""
        tasks = [self.check_tele(number) for number in numbers]
        return await asyncio.gather(*tasks)

    async def check_tele(self, number):
        """Check if a phone number is banned on Telegram."""
        try:
            client = TelegramClient(f'Sessions/session{number}', self.api_id, self.api_hash)
            await client.connect()
            await client.send_code_request(f'+48{number}')
            return True  # Phone number is valid and not banned
        except PhoneNumberBannedError:
            return False  # Phone number is banned
        except PhoneNumberFloodError:
            print(Fore.RED + '[!] Phone number flood detected. Skipping.' + Style.RESET_ALL)
            return False
        finally:
            await client.disconnect()

    def signup(self):
        """Generate an email, sign up, and return the email."""
        while True:
            try:
                proxy = self.set_proxy()
                print(Fore.YELLOW + f'[*] Using proxy: {proxy}' + Style.RESET_ALL)

                # Generate a random email
                resp = requests.get('https://www.1secmail.com/api/v1/?action=genRandomMailbox&count=1')
                email = resp.json()[0]
                if not email.split('@')[1] == 'dpptd.com':
                    continue

                # Step 2: Sign up with the generated email
                url = 'https://api.2nr.xyz/auth/register'
                headers = {
                    "authority": "api.2nr.xyz",
                    "method": "POST",
                    "content-type": "application/json; charset=UTF-8",
                    "user-agent": "okhttp/4.10.0"
                }
                data = {
                    "query": {
                        "email": email,
                        "imei": "b5e32db5b0fa3337",
                        "password": "97809780aA@"
                    },
                    "id": 103
                }

                response = self.scraper.post(url, headers=headers, json=data)
                if response.status_code == 200:
                    print(Fore.GREEN + f'[*] Registration request sent for {email}' + Style.RESET_ALL)
                    time.sleep(10)  # Wait for the email to be received
                    self.activate_email(email)
                    return email
                else:
                    print(Fore.RED + f'[?] Failed to register {email}, retrying...' + Style.RESET_ALL)
            except Exception as e:
                print(Fore.YELLOW + f'[!] Signup failed. Error: {e}, retrying...' + Style.RESET_ALL)
                continue

    def activate_email(self, email):
        """Activate the account by clicking the activation link."""
        try:
            inbox_url = f'https://www.1secmail.com/api/v1/?action=getMessages&login={email.split("@")[0]}&domain={email.split("@")[1]}'
            resp = requests.get(inbox_url)
            responses = resp.json()

            if responses:
                message_id = responses[0]['id']
                message_content = requests.get(
                    f'https://www.1secmail.com/api/v1/?action=readMessage&login={email.split("@")[0]}&domain={email.split("@")[1]}&id={message_id}')
                soup = BeautifulSoup(message_content.json()['body'], 'html.parser')
                links = soup.find_all('a')
                activation_links = [link['href'] for link in links if link.has_attr('href')]

                if activation_links:
                    # Find the longest link, assuming it's the activation link
                    activation_link = max(activation_links, key=len)
                    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
                    driver.get(activation_link)
                    print(Fore.GREEN + '[*] Email activated' + Style.RESET_ALL)
                    self.send_telegram(f'{email}')
                    driver.quit()
                else:
                    print(Fore.YELLOW + "[!] Couldn't find activation link" + Style.RESET_ALL)
            else:
                print(Fore.RED + '[?] No email messages found' + Style.RESET_ALL)
        except Exception as e:
            print(Fore.RED + f'[!] Failed to activate email. Error: {e}' + Style.RESET_ALL)

    def login(self, email):
        """Log into the account using the saved credentials."""
        url = 'https://api.2nr.xyz/auth/login'
        headers = {
            "authority": "api.2nr.xyz",
            "method": "POST",
            "content-type": "application/json; charset=UTF-8",
            "user-agent": "okhttp/4.10.0"
        }
        data = {
            "query": {
                "email": email,
                "imei": "b5e32db5b0fa3337",
                "password": "97809780aA@"
            },
            "id": 101
        }
        response = self.scraper.post(url, json=data, headers=headers)
        if response.status_code == 200 and response.json().get('success'):
            return response.headers.get('set-cookie')  # Return the token only
        else:
            return None  # Return None if login fails

    def reserve_number(self, num_id, token):
        """Reserve a phone number."""
        url = 'https://api.2nr.xyz/numbers/reserveNumber'
        data = {
            "query": {
                "availability_days": [1, 2, 3, 4, 5, 6, 7],
                "color": "#E63147",
                "hour_from": None,
                "hour_to": None,
                "integrity_token": "eyJhbGciOiJBMjU2S1ciLCJlbmMiOiJBMjU2R0NNIn0.5gAnGinMJHCAsjcFug-HkochR9yBDiIx3YbjrxLi-h8jeKLhKrU0Zg.ESjD25i684OYX7UI.Hm5DrV3pBdNYN5NOkhRF6o52b9EkmUYfB9r9xFfCU56WqIL8D0O_4x6E7bU-A4jcZEzERG7PYA2Y7Sp941TykaMTISB6hFgHfVlxRgMUQYSgzedktbgSkufbwA_MM4WozsfHWrCrwGEVbMxUCyt2Kbn3jIYUgi_tW96l0LrNjr6pY7dl_pMDPSAq0LOW-J7CjEKCGPGI8oH82FP_dMWYxC8yvMjOytyUuSeBx1PHRIK9AmKRCZM8GQa9dXK-J6-C8kmNJDzNRQqILt1a26vqhxZMxB6_7S_avOGXQUZ-a0JBDf1MtYow8tYDamFCZZgJWVuBaMWzjw5WXKClZdTyJFJnQIcAEjPVcqKVkkbJthbagc9BdCv4nj3YbCteYM7KlzWvq-c5E6QkSm6VtiMUM0tFE27gJ3MhNH5PRZNqKSLEl2yKjwSK4swZUALDcYDJdZuFveKyVM65QinmWdyk4DcoP3Cqr_nwT3NM_bLALkKA4zqWkda9E7MaSCB7CI7QODulX8byMe-ZfmC_uSrtXwQe2SLcDQ9M3mjwVx6ZW4nH6QcwJquYAvfu7381GiksZCxbq6IMNc4Y0XwZm9c4oLaw3ZvKcs2GqaPbFNpc81Dh-RmPbMNWLt8-KXeH0AaHtSWhwGlNWHbGnLV3unvblRoiKe3C0XKl-JoQ6lyZNIpKvmmZMqaUsEcE7d4VelWJC66vXTKuaflDTUZ4vMzwHDao3uAj148_LwCucFzAvIsps_ylOCIgIbzgEGWc--iuWYaXLZnDgu5P40F1bHLmab5BhLf61IbdgQwKbPE6GIyP9c3hQ79CNV4mQBaI4WBDN5oX3cPgMbkVfHwxmuGD9Dz7E7gD18wNOvNtfFzK9R7hD_T7edHBD8xIrjfQwakZ4xLhkDlOvZWD6zrs9Mu_7J5pEDI7UWJWYOv9aHDO7k7M_sj50JeAsE8pDhtIZf-rlXXQD53y12uDJTAK_32krMiUXibN_RhUKwyob2CZNCcqCPo0tyvVAKerLplkN469F37qXkemSqX6Xxx_bX1AFYiXx8HYwfhAPiMeXU-oyuwc98v2Y094U_xkbcnXdGayRdwXKcL-lif1EThjoa2Gfp-6L4AYoubQ1nOYBfNZpm-paTCpBzGmR59dK7w7ilIhEp8.X_4w42f50LBYDr8xeho2ww",
                "marketing": True,
                "name": "Random",
                "nonce": "MjFuZWU5dm1jOWRlcXFvaTk0NDk0bWMya2M",
                "number_id": num_id
            },
            "id": 301
        }
        response = self.scraper.post(url, json=data, headers={"token": token})
        return response.status_code == 200

    def get_number(self):
        """Get and check a phone number for availability."""
        email = self.signup()
        if not email:
            print(Fore.RED + 'Signup failed.' + Style.RESET_ALL)
            return None

        token = self.login(email)
        if not token:
            print(Fore.RED + 'Login failed.' + Style.RESET_ALL)
            return None

        while True:
            try:
                url = 'https://api.2nr.xyz/numbers/getRandomNumber'
                response = self.scraper.post(url, headers={"token": token, "x-app-version": "44"}, json={"id": 300})
                data = response.json()

                if data and isinstance(data, list) and 'number' in data[0]:
                    numbers = [f"+48{data[i]['number']}" for i in range(len(data))]  # Fetch multiple numbers
                    results = asyncio.run(self.check_multiple_numbers(numbers))

                    for i, number in enumerate(numbers):
                        if results[i]:  # Check if the result is True
                            print(Fore.GREEN + f'[+] Valid {number}' + Style.RESET_ALL)
                            num_id = data[i]['id']
                            if self.reserve_number(num_id, token):
                                print(Fore.LIGHTGREEN_EX + f'[+] Reserved {number}' + Style.RESET_ALL)
                            else:
                                print(Fore.RED + f'[!] Failed to reserve {number}' + Style.RESET_ALL)
                        else:
                            print(Fore.RED + f'[-] Banned {number}' + Style.RESET_ALL)

                else:
                    print('[!] The Account Got Limit Numbers')
                    self.get_number()

            except Exception as e:
                print(Fore.RED + f'[!] Error while fetching numbers. Retrying. {e}' + Style.RESET_ALL)
                continue


if __name__ == '__main__':
    num = Numero()
    num.get_number()
