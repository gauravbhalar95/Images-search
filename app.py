import os
from flask import Flask, request
import telebot
import requests
from bs4 import BeautifulSoup

# Retrieve API tokens from environment variables
API_TOKEN_1 = os.getenv('API_TOKEN_1')

# Initialize Telegram bot
bot1 = telebot.TeleBot(API_TOKEN_1)

# Flask app setup
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
        'google': f"https://www.google.com/search?q={query}&tbm=isch",
        'bing': f"https://www.bing.com/images/search?q={query}",
        'yahoo': f"https://images.search.yahoo.com/search/images?p={query}",
        'duckduckgo': f"https://duckduckgo.com/?q={query}&iax=images&ia=images",
        'flickr': f"https://www.flickr.com/search/?text={query}",
        'pixabay': f"https://pixabay.com/images/search/{query}/",
        'pexels': f"https://www.pexels.com/search/{query}/",
        'unsplash': f"https://unsplash.com/s/photos/{query}",
        'shutterstock': f"https://www.shutterstock.com/search/images?searchterm={query}",
        'yandex': f"https://yandex.com/images/search?text={query}"
    }

    if engine not in search_engines:
        return []

    url = search_engines[engine]
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        extractor = ImageExtractor(response.text, engine)
        return extractor.get_image_tags()
    else:
        return []

@bot1.message_handler(commands=['start'])
def send_welcome_bot1(message):
    bot1.reply_to(message, "Welcome! Use /google, /bing, /yahoo, etc., followed by your search query to find images.")

@bot1.message_handler(commands=['google', 'bing', 'yahoo', 'duckduckgo', 'flickr', 'pixabay', 'pexels', 'unsplash', 'shutterstock', 'yandex'])
def image_search(message):
    command = message.text.split()[0][1:]  # Get the command without '/'
    query = ' '.join(message.text.split()[1:])  # Get the query

    if not query:
        bot1.reply_to(message, "Please provide a search query.")
        return

    image_urls = search_image(query, command)
    if image_urls:
        for url in image_urls:
            bot1.send_message(message.chat.id, url)
    else:
        bot1.send_message(message.chat.id, "No images found.")

@app.route('/' + API_TOKEN_1, methods=['POST'])
def getMessage_bot1():
    bot1.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "!", 200

@app.route('/')
def webhook():
    bot1.remove_webhook()
    # Set your Flask app's URL directly
    bot1.set_webhook(url='https://images-search.onrender.com/' + API_TOKEN_1)
    return "Webhook set", 200

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
  
