import requests
import os
from datetime import datetime
from io import BytesIO
from bs4 import BeautifulSoup
from discord import Game, Embed
from discord.ext.commands import Bot
from dotenv import load_dotenv


def log(text):
    print("{} | {}".format(str(datetime.now()), text))


load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
DCCON_HOME_URL = "https://dccon.dcinside.com/"
DCCON_SEARCH_URL = "https://dccon.dcinside.com/hot/1/title/"
DCCON_DETAILS_URL = 'https://dccon.dcinside.com/index/package_detail'


client = Bot(command_prefix='')

@client.event
async def on_ready():
    await client.change_presence(game=Game(name="!도움"))
    log('Bot ready')


@client.event
async def on_message(msg):
    if msg.content.startswith('!'):  # usage: !dccon pkg name 01
        msg_content = msg.content[1:]
        log('message identified: ' + msg_content)

        if msg_content == "도움":
            log('help command')
            embed = Embed(title="안녕하세요! 디시콘 핫산이에요!",
                          description="명령어들은 아래에서 전부 보실 수 있어요.",
                          color=0x4559e9)
            embed.add_field(name="사용 방법", value="!디시콘 패키지 제목 콘이름", inline=False)
            embed.add_field(name="명령어", value="도움, 대하여, 초대링크", inline=False)
            embed.set_footer(text="그코좆망겜")
            await client.send_message(msg.channel, embed=embed)
        elif msg_content == "대하여":
            log('about command')
            embed = Embed(title="About",
                          description="구에엑",
                          color=0x4559e9)
            await client.send_message(msg.channel, embed=embed)
        elif msg_content == "초대링크":
            log('invite command')
            await client.send_message(msg.channel, "초대링크드렸습니다")
        else:
            msg_list = msg_content.split()
            idx = msg_list[-1]  # last word in message goes to index
            package_name = " ".join(str(x) for x in msg_list[0:-1])  # stupid fuckfuckfuckfuck

            log('interpreted: ' + package_name + ', ' + idx)

            if package_name == '':
                package_name = idx

            ############################################################################################################
            # respect https://github.com/gw1021/dccon-downloader/blob/master/python/app.py#L7:L18
            #

            s = requests.Session()

            package_search_req = s.get(DCCON_SEARCH_URL + package_name)
            package_search_html = BeautifulSoup(package_search_req.text, 'html.parser')
            package_search_list = package_search_html.select("#right_cont_wrap > div > div.dccon_listbox > ul > li")

            try:
                target_package = package_search_list[0]  # pick first dccon package (bs4 obj) from search list
            except IndexError as e:  # maybe no search result w/ IndexError?
                log('error! (maybe no search result) : ' + str(e))
                await client.send_message(msg.channel, '"' + package_name + '"' + ' 디시콘 패키지 정보를 찾을 수 없습니다.')
            else:
                target_package_num = target_package.get("package_idx")  # get dccon number of target dccon package

                # for i in package_search_req.cookies:
                #     print(i.name, i.value)

                package_detail_req = s.post(DCCON_DETAILS_URL,
                                            # content-type: application/x-www-form-urlencoded; charset=UTF-8
                                            cookies={'ci_c': package_search_req.cookies['ci_c'],
                                                     'PHPSESSID': package_search_req.cookies['PHPSESSID']},
                                            headers={'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                                                     'Referer': DCCON_SEARCH_URL + str(package_name.encode('utf-8')),
                                                     'Origin': DCCON_HOME_URL,
                                                     'X-Requested-With': 'XMLHttpRequest'},
                                            data={'ci_t': package_search_req.cookies['ci_c'],
                                                  'package_idx': target_package_num,
                                                  'code': ''})
                
                # 에러 핸들링 여기서 해야함

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

                # 최적화 필요
                succeed = False
                for dccon in package_detail_json['detail']:
                    if dccon['title'] == idx:
                        dccon_img = "http://dcimg5.dcinside.com/dccon.php?no=" + dccon['path']
                        dccon_img_request = s.get(dccon_img, headers={'Referer': DCCON_HOME_URL})
                        buffer = BytesIO(dccon_img_request.content)
                        filename = package_detail_json['info']['title'] + '_' + dccon['title'] + '.' + dccon['ext']
                        await client.send_file(msg.channel,
                                               fp=buffer,
                                               filename=filename)
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
            #
            #
            ############################################################################################################

if __name__ == "__main__":
    client.run(BOT_TOKEN)
