import module_manager
module_manager.review()
import requests
from bs4 import BeautifulSoup

def print_lyrics(artist, title):
    pageurl = "https://makeitpersonal.co/lyrics?artist=" + artist + \
              "&title=" + title
    print(pageurl)
    lyrics = requests.get(pageurl).text.strip()

    if lyrics == "Sorry, We don't have lyrics for this song yet.":
        print("____foo___")
        wiki_url = "https://lyrics.fandom.com/wiki/"
        title = title.replace(" ", "_")
        artist = artist.replace(" ", "_")
        url = wiki_url + f"{artist}:{title}"
        print(url)

        r = requests.get(url)
        soup = BeautifulSoup(r.text, 'html.parser')

        lyric_box = str(soup.find("div", {"class": "lyricbox"}))
        lyrics = lyric_box.replace("<br/>", "\n")
        lyrics = lyrics.replace('<div class="lyricbox">', '')
        lyrics = lyrics.replace('<div class="lyricsbreak">', '')
        lyrics = lyrics.replace('</div>', '')

    print(lyrics)