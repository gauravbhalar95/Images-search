import os
from flask import Flask, request
import telebot
import requests
from bs4 import BeautifulSoup

API_TOKEN_1 = os.getenv('API_TOKEN_1')
bot1 = telebot.TeleBot(API_TOKEN_1)

app = Flask(__name__)

class ImageExtractor:
    def __init__(self, html_content, engine):
        self.soup = BeautifulSoup(html_content, 'html.parser')
        self.engine = engine

    def get_image_tags(self):
        image_tags = []
        if self.engine == 'google':
            image_tags = self.soup.find_all('img', {'class': 'rg_i Q4LuWd'})
        elif self.engine == 'bing':
            image_tags = self.soup.find_all('img', {'class': 'mimg'})
        elif self.engine == 'yahoo':
            image_tags = self.soup.find_all('img', {'class': 'process'})
        elif self.engine == 'duckduckgo':
            image_tags = self.soup.find_all('img', {'class': 'tile--img__img'})
        elif self.engine == 'flickr':
            image_tags = self.soup.find_all('img', {'class': 'photo-list-photo-view'})
        elif self.engine == 'pixabay':
            image_tags = self.soup.find_all('img', {'class': 'preview'})
        elif self.engine == 'pexels':
            image_tags = self.soup.find_all('img', {'class': 'photo-item__img'})
        elif self.engine == 'unsplash':
            image_tags = self.soup.find_all('img', {'class': 'YVj9w'})
        elif self.engine == 'shutterstock':
            image_tags = self.soup.find_all('img', {'class': 'z_h_8iJ6'})
        elif self.engine == 'yandex':
            image_tags = self.soup.find_all('img', {'class': 'serp-item__thumb justifier__thumb'})

        image_urls = []
        for img in image_tags:
            image_url = img.get('src') or img.get('data-src')
            if image_url and len(image_urls) < 100:  # Limit to top 100 images
                if not image_url.startswith('http'):
                    image_url = "https:" + image_url
                image_urls.append(image_url)

        return image_urls



def search_image(query, engine):
    search_engines = {
                      'google': f"https://www.google.com/search?q={query}+&client=ms-android-samsung-ss&sca_esv=ec3eb9fcd9e1b35d&udm=2&biw=384&bih=729&sxsrf=ADLYWIKSFHY6SdMGsYC9iL70OTZLa8KzNw%3A1724849897556&ei=6R7PZpXVIa-q4-EPk5252A8&oq={query}+&gs_lp=EhNtb2JpbGUtZ3dzLXdpei1zZXJwIgxraW5qYWwgZGF2ZSAyChAAGIAEGEMYigUyChAAGIAEGEMYigUyChAAGIAEGEMYigUyBRAAGIAEMgoQABiABBhDGIoFSPKJAlCtOVitOXAEeACQAQCYAfACoAHsBaoBBzAuMi4wLjG4AQPIAQD4AQX4AQGYAgegAqMGwgIEEAAYA5gDAOIDBRIBMSBAiAYBkgcHNC4xLjEuMaAH4Ak&sclient=mobile-gws-wiz-serp",
                      'bing': f"https://www.bing.com/images/search?q={query}",
                      'yahoo': f"https://images.search.yahoo.com/search/images?p={query}",
                      'duckduckgo': f"https://duckduckgo.com/?q={query}+&t=h_&iar=images&iax=images&ia=images",
                      'flickr': f"https://www.flickr.com/search/?text={query}",
                      'pixabay': f"https://pixabay.com/images/search/{query}/",
                      'pexels': f"https://www.pexels.com/search/{query}/",
                      'unsplash': f"https://unsplash.com/s/photos/{query}",
                      'shutterstock': f"https://www.shutterstock.com/search/images?searchterm={query}",
                      'yandex': f"https://yandex.com/images/touch/search?lr=10569&text={query}"
         }

    if engine not in search_engines:
        return []

    url = search_engines[engine]
    headers = {
        'google': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'bing': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0',
    'yahoo': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'duckduckgo': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'flickr': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0',
    'pixabay': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'pexels': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0',
    'unsplash': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0',
    'shutterstock': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'yandex': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0'
      }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        extractor = ImageExtractor(response.text, engine)
        return extractor.get_image_tags()
    else:
        return []


@bot1.message_handler(commands=['start'])
def send_welcome_bot1(message):
    bot1.reply_to(message, "Welcome! Use /google, /bing, /yahoo, /duckduckgo, or /yandex followed by your search query to find images.")

@bot1.message_handler(commands=['google', 'bing', 'yahoo', 'duckduckgo', 'yandex'])
def image_search(message):
    command = message.text.split()[0][1:]  # Get the engine name
    query = " ".join(message.text.split()[1:])  # Get the search query
    if not query:
        bot1.reply_to(message, "Please provide a search query.")
        return

    images = search_image(query, command)
    if images:
        for img in images:
            bot1.send_message(message.chat.id, img)
    else:
        bot1.reply_to(message, "No images found.")

@app.route('/' + API_TOKEN_1, methods=['POST'])
def getMessage_bot1():
    bot1.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "!", 200

@app.route('/')
def webhook():
    bot1.remove_webhook()
    bot1.set_webhook(url=f'https://images-search.onrender.com/{API_TOKEN_1}', timeout=60)
    return "Webhook set", 200

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
