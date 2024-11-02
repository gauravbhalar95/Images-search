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
            # Check for higher quality image attributes
            image_url = img.get('data-srcset') or img.get('data-src') or img.get('srcset') or img.get('src')
            if image_url:
                # Ensure the URL starts with http or https
                if not image_url.startswith('http'):
                    image_url = "https:" + image_url
                # Extract HD quality image if possible from srcset
                if " " in image_url:
                    image_url = image_url.split(" ")[0]

                # Filter based on default dimension (greater than 720px)
                try:
                    width, height = self.get_image_dimensions(img)
                    if width >= DEFAULT_MIN_DIMENSION and height >= DEFAULT_MIN_DIMENSION:
                        image_urls.append(image_url)
                except ValueError:
                    # If dimensions are not found, add the image URL anyway
                    image_urls.append(image_url)

        return image_urls

    def get_image_dimensions(self, img):
        """Extract width and height from the image tag."""
        width = img.get('width') or img.get('data-width')
        height = img.get('height') or img.get('data-height')

        if width and height:
            return int(width), int(height)
        else:
            raise ValueError("Dimensions not found")


def search_hd_image(query, engine):
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
        extractor = HDImageExtractor(response.text, engine)
        return extractor.get_image_tags()
    else:
        return []


@bot1.message_handler(commands=['start'])
def send_welcome_bot1(message):
    bot1.reply_to(message, "Welcome! Use /google, /bing, /yahoo, /duckduckgo, or /yandex followed by your search query to find HD images.")


@bot1.message_handler(commands=['google', 'bing', 'yahoo', 'duckduckgo', 'flickr', 'pixabay', 'pexels', 'unsplash', 'shutterstock', 'yandex'])
def image_search(message):
    try:
        command = message.text.split(' ', 1)[0][1:]  # Extract the command without '/'
        query = message.text.split(' ', 1)[1]
        image_urls = search_hd_image(query, command.lower())

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
    bot1.set_webhook(url=os.getenv('KOYEB_URL') + '/' + API_TOKEN_1, timeout=60)
    return "Webhook set", 200

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
