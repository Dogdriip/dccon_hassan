from datetime import datetime
import requests
from io import BytesIO
from bs4 import BeautifulSoup
from discord import Game
from discord import Embed
from discord.ext.commands import Bot
from dotenv import load_dotenv
import os

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
DCCON_HOME_URL = "http://dccon.dcinside.com/"
DCCON_SEARCH_URL = "http://dccon.dcinside.com/hot/1/title/"
DCCON_DETAILS_URL = 'http://dccon.dcinside.com/index/package_detail'
# USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36"

client = Bot(command_prefix='')


@client.event
async def on_ready():
    await client.change_presence(game=Game(name="!도움"))
    print("Bot ready: " + str(datetime.now()))


@client.event
async def on_message(msg):
    if msg.content.startswith('!'):  # usage: !dccon pkg name 01
        msg_content = msg.content[1:]
        print("{} | message identified: {}".format(str(datetime.now()), msg_content))

        if msg_content == "!도움":
            print(str(datetime.now()) + " | help command")
            embed = Embed(title="안녕하세요! 디시콘 핫산이에요!",
                          description="명령어들은 아래에서 전부 보실 수 있어요.",
                          color=0x4559e9)
            embed.add_field(name="사용 방법", value="!디시콘 패키지 제목 콘이름", inline=False)
            embed.add_field(name="명령어", value="도움, 대하여, 초대링크", inline=False)
            embed.set_footer(text="그코좆망겜")
            await client.send_message(msg.channel, embed=embed)

        elif msg_content == "!대하여":
            print(str(datetime.now()) + " | about command")
            embed = Embed(title="About",
                          description="freakin/awesome/thing/goes/here",
                          color=0x4559e9)
            await client.send_message(msg.channel, embed=embed)

        elif msg_content == "!초대링크":
            print(str(datetime.now()) + " | invite command")
            await client.send_message(msg.channel, "초대링크드렸습니다")

        else:
            msg_list = msg_content.split()
            idx = msg_list[-1]  # last word in message goes to index
            package_name = " ".join(str(x) for x in msg_list[0:-1])  # stupid fuckfuckfuckfuck

            print("{} | interpreted: {}, {}".format(str(datetime.now()), package_name, idx))

            if package_name == '':
                package_name = idx

            ############################################################################################################
            # respect https://github.com/gw1021/dccon-downloader/blob/master/python/app.py#L7:L18

            s = requests.Session()

            package_search_req = s.get(DCCON_SEARCH_URL + package_name)
            package_search_html = BeautifulSoup(package_search_req.text, 'html.parser')
            package_search_list = package_search_html.select("body > \
                                                              div.wrap_dccone > \
                                                              div.content > \
                                                              div.shop_cont > \
                                                              div > \
                                                              div.sticker_list_box > \
                                                              ul > \
                                                              li")

            try:
                target_package = package_search_list[0]  # pick first dccon package (bs4 obj) from search list
            except IndexError as e:  # maybe no search result w/ IndexError?
                print("{} | error! (maybe no search result): {}".format(str(datetime.now()), e))
                await client.send_message(msg.channel, "\"{}\" 디시콘 패키지 정보를 찾을 수 없습니다.".format(package_name))
            else:
                target_package_num = target_package.get("package_idx")  # get dccon number of target dccon package

                package_detail_cookie_req = s.get(DCCON_DETAILS_URL, headers={'X-Requested-With': 'XMLHttpRequest'})
                package_detail_req = s.post(DCCON_DETAILS_URL,
                                            headers={'X-Requested-With': 'XMLHttpRequest'},
                                            data={'ci_t': package_detail_cookie_req.cookies['ci_c'],
                                                  'package_idx': target_package_num})

                package_detail_json = package_detail_req.json()
                '''
                    info /  'package_idx'
                            'seller_no'
                            'seller_id'
                            'title'
                            'category'
                            'path'
                            'description'
                            'price'
                            'period'
                            'icon_cnt'
                            'state'
                            'open'
                            'sale_count'
                            'reg_date'
                            'seller_name'
                            'code'
                            'seller_type'
                            'mandoo'
                            'main_img_path'
                            'list_img_path'
                            'reg_date_short'
                            
                    detail /  () /  'idx'
                                    'package_idx'
                                    'title'
                                    'sort'
                                    'ext'
                                    'path'
                '''

                # too classic method
                succeed = False
                for dccon in package_detail_json['detail']:
                    if dccon['title'] == idx:
                        dccon_img = "http://dcimg5.dcinside.com/dccon.php?no=" + dccon['path']
                        dccon_img_request = s.get(dccon_img, headers={'Referer': DCCON_HOME_URL})
                        buffer = BytesIO(dccon_img_request.content)
                        await client.send_file(msg.channel,
                                               fp=buffer,
                                               filename=package_detail_json['info']['title'] + '_' + dccon['title'] + '.' + dccon['ext'])
                        succeed = True
                        break
                if not succeed:
                    available_dccon_list = []
                    for dccon in package_detail_json['detail']:
                        available_dccon_list.append(dccon['title'])
                    await client.send_message(msg.channel, "\"{}\" 디시콘 패키지에서 \"{}\" 디시콘을 찾지 못했습니다."
                                                           .format(package_name, idx))
                    await client.send_message(msg.channel, "사용 가능한 디시콘 : {}"
                                              .format(', '.join(available_dccon_list).rstrip(', ')))

            ############################################################################################################
            #  old
            '''
            options = webdriver.ChromeOptions()
            options.add_argument("headless")
            options.add_argument("window-size=1920x1080")
            options.add_argument("disable-gpu")
            options.add_argument("user-agent=" + USER_AGENT)
            driver = webdriver.Chrome("driver/chromedriver", chrome_options=options)
    
            # search dccon package with package_name
            driver.get(DCCON_SEARCH_URL + package_name)
            package_search_list = list(driver.find_elements_by_css_selector("body > \
                                                                             div.wrap_dccone > \
                                                                             div.content > \
                                                                             div.shop_cont > \
                                                                             div > \
                                                                             div.sticker_list_box > \
                                                                             ul > \
                                                                             li"))
    
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
            '''
            ############################################################################################################

if __name__ == "__main__":
    client.run(BOT_TOKEN)
