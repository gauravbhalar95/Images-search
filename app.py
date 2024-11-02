import os
from flask import Flask, request
import telebot
import requests
from bs4 import BeautifulSoup

API_TOKEN_1 = os.getenv('API_TOKEN_1')
bot1 = telebot.TeleBot(API_TOKEN_1)

app = Flask(__name__)

# Default min width and height
DEFAULT_MIN_DIMENSION = 720

class HDImageExtractor:
    def __init__(self, html_content, engine):
        self.soup = BeautifulSoup(html_content, 'html.parser')
        self.engine = engine

    def get_image_tags(self):
        image_tags = []
        # Define the image tag extraction based on the engine
        # ...

def search_hd_image(query, engine):
    search_engines = {
        'google': f"https://www.google.com/search?q={query}&tbm=isch",
        # Other engines...
    }

    url = search_engines.get(engine)
    if not url:
        return []

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        extractor = HDImageExtractor(response.text, engine)
        return extractor.get_image_tags()
    return []

@bot1.message_handler(commands=['start'])
def send_welcome_bot1(message):
    bot1.reply_to(message, "Welcome! Use /google, /bing, /yahoo, /duckduckgo, or /yandex followed by your search query to find HD images.")

@bot1.message_handler(commands=['google', 'bing', 'yahoo', 'duckduckgo', 'flickr', 'pixabay', 'pexels', 'unsplash', 'shutterstock', 'yandex'])
def image_search(message):
    try:
        command = message.text.split(' ', 1)[0][1:]  # Extract command
        query = message.text.split(' ', 1)[1]
        image_urls = search_hd_image(query, command.lower())

        if not image_urls:
            bot1.send_message(message.chat.id, "No images found. Please try a different search query.")
            return

        for img_url in image_urls[:5]:  # Limit to 5 images
            bot1.send_photo(message.chat.id, img_url)

    except IndexError:
        bot1.send_message(message.chat.id, "Please provide a search query after the command.")
    except Exception as e:
        bot1.send_message(message.chat.id, f"An error occurred: {str(e)}")

@app.route('/' + API_TOKEN_1, methods=['POST'])
def getMessage_bot1():
    try:
        json_str = request.stream.read().decode("utf-8")
        update = telebot.types.Update.de_json(json_str)
        bot1.process_new_updates([update])
    except Exception as e:
        print(f"Error processing update: {e}")
    return "!", 200

@app.route('/')
def webhook():
    bot1.remove_webhook()
    webhook_url = os.getenv('KOYEB_URL') + '/' + API_TOKEN_1
    success = bot1.set_webhook(url=webhook_url, timeout=60)
    if success:
        print("Webhook set successfully:", webhook_url)
    else:
        print("Failed to set webhook")
    return "Webhook set", 200

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)