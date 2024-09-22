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
        image_urls = []
        if self.engine == 'google':
            for img in self.soup.find_all('img'):
                url = img.get('src')
                if url and len(image_urls) < 10:  # Limit to 10 images
                    image_urls.append(url)
        elif self.engine == 'bing':
            for img in self.soup.find_all('img'):
                url = img.get('src')
                if url and "w=600" in url:  # Filter for high-quality images
                    image_urls.append(url)
                if len(image_urls) >= 10:  # Limit to 10 images
                    break
        elif self.engine == 'yahoo':
            for img in self.soup.find_all('img'):
                url = img.get('src')
                if url and len(image_urls) < 10:
                    image_urls.append(url)
        elif self.engine == 'duckduckgo':
            for img in self.soup.find_all('img'):
                url = img.get('src')
                if url and len(image_urls) < 10:
                    image_urls.append(url)
        elif self.engine == 'yandex':
            for img in self.soup.find_all('img'):
                url = img.get('src')
                if url and len(image_urls) < 10:
                    image_urls.append(url)

        return image_urls

def search_image(query, engine):
    search_engines = {
        'google': f"https://www.google.com/search?hl=en&tbm=isch&q={query}",
        'bing': f"https://www.bing.com/images/search?q={query}",
        'yahoo': f"https://images.search.yahoo.com/search/images?p={query}",
        'duckduckgo': f"https://duckduckgo.com/?q={query}&t=h_&iar=images&iax=images&ia=images",
        'yandex': f"https://yandex.com/images/search?text={query}",
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
