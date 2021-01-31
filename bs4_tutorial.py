import requests

from bs4 import BeautifulSoup

url = 'https://www.franksonnenbergonline.com/blog/are-you-grateful/'
response = requests.get(url)
response.raise_for_status()

soup = BeautifulSoup(response.text, 'lxml')

title = soup.find('div').find('header').find('h1').text
picture = soup.find('img', class_='attachment-post-image').get('src')
post = soup.find('article').find('div', class_='entry-content').text
