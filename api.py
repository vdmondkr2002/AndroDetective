from email import message
import requests
import urllib.parse
import validators
import requests
import json
import json
from bs4 import BeautifulSoup
import re


myString = "Get Free Bitcoin Worth Rs.1000!! Click on this link: https://www.getbitcoins.com"

url=""
try:
    url = re.search("(?P<url>https?://[^\s]+)", myString).group("url")
except:
    new=""

print(url)



# message_data = row[4]
# isUrl =  validators.url(message_data)
# suspicious = False
# malware = False
# phishing = False
# risk_score = 0
# if isUrl:
#     parsed_link = urllib.parse.quote('http://www.csm-testcenter.org/download/malicious/index.html', safe='')
#     api = "https://ipqualityscore.com/api/json/url/" + key + "/" + parsed_link
#     response = requests.get(api)
#     response_json = json.loads(response.content)
#     suspicious = response_json.get('suspicious', "")
#     malware = response_json.get('malware', "")
#     phishing = response_json.get('phishing', "")
#     risk_score = response_json.get('risk_score', "")

# print(response.content)

