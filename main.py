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
DCCON_SEARCH_URL = "http://dccon.dcinside.com/hot/1/title/"
DCCON_DETAILS_URL = "http://dccon.dcinside.com/#"
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36"

client = Bot(command_prefix='')


@client.event
async def on_ready():
    await client.change_presence(game=Game(name="Groove Coaster for Steam"))
    print("Bot ready: " + str(datetime.now()))


@client.event
async def on_message(msg):
    if msg.content.startswith('!'):  # usage: !dccon pkg name 01
        print("{} | message identified: {}".format(str(datetime.now()), msg.content))
        await client.send_message(msg.channel, "{} | message identified: {}".format(str(datetime.now()), msg.content))

        msg_list = msg.content.split()
        idx = msg_list[-1]  # last word in message goes to index
        package_name = " ".join(str(x) for x in msg_list[0:-1])  # stupid
        package_name = package_name[1:]  # ignore first character(!)
        print("{} | interpreted: {}, {}".format(str(datetime.now()), package_name, idx))
        await client.send_message(msg.channel, "{} | interpreted: {}, {}".format(str(datetime.now()), package_name, idx))

        options = webdriver.ChromeOptions()
        options.add_argument("headless")
        options.add_argument("window-size=1920x1080")
        options.add_argument("disable-gpu")
        options.add_argument("user-agent=" + USER_AGENT)
        driver = webdriver.Chrome("driver/chromedriver", chrome_options=options)

        # search dccon package with package_name
        driver.get(DCCON_SEARCH_URL + package_name)
        package_search_list = list(driver.find_elements_by_css_selector("body > div.wrap_dccone > div.content > div.shop_cont > div > div.sticker_list_box > ul > li"))

        try:
            target_package = package_search_list[0]  # pick first dccon package from search list
        except IndexError as e:  # maybe no search result w/ IndexError?
            print("{} | error! (maybe no search result): {}".format(str(datetime.now()), e))
            await client.send_message(msg.channel, "{} | error! (maybe no search result): {}".format(str(datetime.now()), e))
        else:
            target_package_num = target_package.get_attribute("package_idx")  # get dccon number of target dccon package

            # go to detail page
            driver.get(DCCON_DETAILS_URL + target_package_num)
            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')

            # dccon_li_list = soup.select("#package_detail > div > ul.Img_box.detail_icon > li")

            # dccon_img_list = []
            #
            # for li in dccon_li_list:
            #     print(str(li))
            #     dccon_img_list.append(li.select("img"))

            dccon = soup.find(attrs={"alt": idx})  # find specified dccon in target package

            try:
                dccon_img = dccon['src']
            except TypeError as e:
                print("{} | error! (maybe wrong dccon idx): {}".format(str(datetime.now()), e))
                await client.send_message(msg.channel, "{} | error! (maybe wrong dccon idx): {}".format(str(datetime.now()), e))
            else:
                response = requests.get("http:" + dccon_img, headers={'Referer': DCCON_DETAILS_URL + target_package_num})
                buffer = BytesIO(response.content)
                await client.send_file(msg.channel, fp=buffer, filename="dccon.gif")

                # if str(idx) is None:

                # TODO: 예외처리!

                # driver.quit()


if __name__ == "__main__":
    client.run(BOT_TOKEN)
