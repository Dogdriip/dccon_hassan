from datetime import datetime
import requests
from io import BytesIO
from selenium import webdriver
from bs4 import BeautifulSoup
from discord import Game
from discord.ext.commands import Bot
from dotenv import load_dotenv
import os

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

client = Bot(command_prefix='')


@client.event
async def on_ready():
    await client.change_presence(game=Game(name="Groove Coaster for Steam"))
    print("Bot ready: " + str(datetime.now()))


@client.event
async def on_message(msg):
    if msg.content.startswith('!'):
        print("message identified: {}".format(msg.content))
        name, idx = msg.content.split()
        name = name[1:]  # ignore first char(prefix) and override it
        print("interpreted: {}, {}".format(name, idx))

        DCCON_SEARCH_URL = "http://dccon.dcinside.com/hot/1/title/"
        DCCON_DETAILS_URL = "http://dccon.dcinside.com/#"
        USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36"
        options = webdriver.ChromeOptions()
        options.add_argument("headless")
        options.add_argument("window-size=1920x1080")
        options.add_argument("disable-gpu")
        options.add_argument("user-agent=" + USER_AGENT)

        driver = webdriver.Chrome("driver/chromedriver", chrome_options=options)

        driver.get(DCCON_SEARCH_URL + name)
        dccon_searchlist = list(driver.find_elements_by_css_selector("body > div.wrap_dccone > div.content > div.shop_cont > div > div.sticker_list_box > ul > li"))
        target_dccon = dccon_searchlist[0]  # pick first dccon from search list

        dccon_idx = target_dccon.get_attribute("package_idx")

        driver.get(DCCON_DETAILS_URL + dccon_idx)
        html = driver.page_source

        soup = BeautifulSoup(html, 'html.parser')
        # dccon_li_list = soup.select("#package_detail > div > ul.Img_box.detail_icon > li")

        # dccon_img_list = []
        #
        # for li in dccon_li_list:
        #     print(str(li))
        #     dccon_img_list.append(li.select("img"))

        dccon = soup.find(attrs={"alt": idx})
        dccon_img = dccon['src']

        response = requests.get("http:" + dccon_img, headers={'Referer': DCCON_DETAILS_URL+dccon_idx})

        buffer = BytesIO(response.content)

        await client.send_file(msg.channel, fp=buffer, filename="dccon.png")

        # if str(idx) is None:

        driver.quit()


if __name__ == "__main__":
    client.run(BOT_TOKEN)
