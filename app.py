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
            image_tags = self.soup.find_all('img')
            for img in image_tags:
                url = img.get('src')
                if url and not url.startswith('data:image/') and len(image_urls) < 10:
                    if 'http' in url:
                        image_urls.append(url)

        elif self.engine == 'bing':
            image_tags = self.soup.find_all('a', {'class': 'iusc'})
            for tag in image_tags:
                img_url = tag.get('m')
                if img_url:
                    # Parse the JSON string to get the actual image URL
                    img_info = json.loads(img_url)
                    if img_info.get('murl'):
                        image_urls.append(img_info['murl'])

        elif self.engine == 'duckduckgo':
            image_tags = self.soup.find_all('img', class_='tile--img__img')
            for img in image_tags:
                url = img.get('src')
                if url and not url.startswith('data:image/') and len(image_urls) < 10:
                    image_urls.append(url)

        elif self.engine == 'yandex':
            image_tags = self.soup.find_all('img', class_='serp-item__thumb')
            for img in image_tags:
                url = img.get('src')
                if url and not url.startswith('data:image/') and len(image_urls) < 10:
                    image_urls.append(url)

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

# Bot 1 commands and handlers
@bot1.message_handler(commands=['start'])
def send_welcome_bot1(message):
    bot1.reply_to(message, "Welcome! Use /google, /bing, /yahoo, etc., followed by your search query to find images.")

@bot1.message_handler(commands=['google', 'bing', 'yahoo', 'duckduckgo', 'flickr', 'pixabay', 'pexels', 'unsplash', 'shutterstock', 'yandex'])
def image_search(message):
    try:
        command = message.text.split(' ', 1)[0][1:]  # Extract the command without '/'
        query = message.text.split(' ', 1)[1]
        image_urls = search_image(query, command.lower())

        if not image_urls:
            bot1.send_message(message.chat.id, "No images found. Please try a different search query.")
            return

        for img_url in image_urls:
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
