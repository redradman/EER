import sys
import requests
from bs4 import BeautifulSoup

url = input("Enter the URL to visit (include: https): ")

response = requests.get(url)
print(response.status_code)
response.raise_for_status()



# def get_plaintext_from_url(url):
#     try:
#         # Send a GET request
#         response = requests.get(url)
#         response.raise_for_status() # halt if unsuccessful
#         # Parse HTML via BeautifulSoup
#         soup = BeautifulSoup(response.content, 'html.parser')
#         # Extract and return the plain text
#         return soup.get_text()
#     except requests.exceptions.RequestException as e:
#         return f"An error occurred: {e}"

# if __name__ == "__main__":
#     if len(sys.argv) != 2:
#         print("Usage: python script.py <URL>")
#         sys.exit(1)

#     url = sys.argv[1]
#     plaintext = get_plaintext_from_url(url)
#     print(plaintext)