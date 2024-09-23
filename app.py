import os
from flask import Flask, request
import telebot
import requests
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO

API_TOKEN_1 = os.getenv('API_TOKEN_1')
bot1 = telebot.TeleBot(API_TOKEN_1)

app = Flask(__name__)

class HDImageExtractor:
    def __init__(self, html_content, engine, min_width=None, max_width=None, min_height=None, max_height=None):
        self.soup = BeautifulSoup(html_content, 'html.parser')
        self.engine = engine
        self.min_width = min_width
        self.max_width = max_width
        self.min_height = min_height
        self.max_height = max_height

    def image_fits_size(self, image_url):
        try:
            response = requests.get(image_url)
            img = Image.open(BytesIO(response.content))
            width, height = img.size

            if self.min_width and width < self.min_width:
                return False
            if self.max_width and width > self.max_width:
                return False
            if self.min_height and height < self.min_height:
                return False
            if self.max_height and height > self.max_height:
                return False

            return True
        except Exception as e:
            print(f"Error fetching image size: {e}")
            return False

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
            image_url = img.get('data-srcset') or img.get('data-src') or img.get('srcset') or img.get('src')
            if image_url:
                if not image_url.startswith('http'):
                    image_url = "https:" + image_url
                if " " in image_url:
                    image_url = image_url.split(" ")[0]

                # Check image size if the constraints are set
                if self.image_fits_size(image_url):
                    image_urls.append(image_url)

            if len(image_urls) >= 100:  # Limit to top 100 images
                break

        return image_urls

def search_hd_image(query, engine, min_width=None, max_width=None, min_height=None, max_height=None):
    search_engines = {
        'google': f"https://www.google.com/search?q={query}&tbm=isch",
        'bing': f"https://www.bing.com/images/search?q={query}&qft=+filterui:imagesize-large",
        'yahoo': f"https://images.search.yahoo.com/search/images?p={query}",
        'duckduckgo': f"https://duckduckgo.com/?q={query}&iar=images&iax=images&ia=images",
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
        extractor = HDImageExtractor(response.text, engine, min_width, max_width, min_height, max_height)
        return extractor.get_image_tags()
    else:
        return []

@bot1.message_handler(commands=['start'])
def send_welcome_bot1(message):
    bot1.reply_to(message, "Welcome! Use /google, /bing, /yahoo, /duckduckgo, or /yandex followed by your search query to find HD images. Optionally, you can add size constraints in the format `min_width,max_width,min_height,max_height`.")

@bot1.message_handler(commands=['google', 'bing', 'yahoo', 'duckduckgo', 'flickr', 'pixabay', 'pexels', 'unsplash', 'shutterstock', 'yandex'])
def image_search(message):
    try:
        # Extract the command and query
        command = message.text.split(' ', 1)[0][1:]  # Extract the command without '/'
        args = message.text.split(' ', 2)

        query = args[1]
        size_constraints = None

        if len(args) > 2:
            size_constraints = args[2].split(',')

        # Handle size constraints
        min_width = int(size_constraints[0]) if size_constraints and len(size_constraints) >= 1 else None
        max_width = int(size_constraints[1]) if size_constraints and len(size_constraints) >= 2 else None
        min_height = int(size_constraints[2]) if size_constraints and len(size_constraints) >= 3 else None
        max_height = int(size_constraints[3]) if size_constraints and len(size_constraints) >= 4 else None

        image_urls = search_hd_image(query, command.lower(), min_width, max_width, min_height, max_height)

        if not image_urls:
            bot1.send_message(message.chat.id, "No images found. Please try a different search query.")
            return

        for img_url in image_urls[:5]:  # Limit to sending 5 images at a time
            bot1.send_photo(message.chat.id, img_url)

    except IndexError:
        bot1.send_message(message.chat.id, "Please provide a search query after the command.")
    except Exception as e:
        bot1.send_message(message.chat.id, f"An error occurred: {str(e)}")

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
