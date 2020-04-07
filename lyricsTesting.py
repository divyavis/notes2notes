import module_manager
module_manager.review()
import requests
from bs4 import BeautifulSoup

#modified from https://www.promptcloud.com/blog/scraping-song-lyrics-using-python-from-genius/
URL = "https://genius.com/James-blake-timeless-lyrics"
# URL format is https://genius.com/Artist-name-song-name-lyrics
page = requests.get(URL)
soup = BeautifulSoup(page.content, 'html.parser')
for div in soup.findAll('div', attrs = {'class': 'lyrics'}):
    lyrics = div.text.strip().split("\n")

for line in lyrics:
    print(line)