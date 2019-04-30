import requests
import os
from datetime import datetime
from io import BytesIO
from bs4 import BeautifulSoup
from discord import Game, Embed, File
from discord.ext.commands import Bot
from dotenv import load_dotenv


def log(fr, text):
    print('{} | {} | {}'.format(fr, str(datetime.now()), text))  # TODO: 시간대 조정


load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
DCCON_HOME_URL = 'https://dccon.dcinside.com/'
DCCON_SEARCH_URL = 'https://dccon.dcinside.com/hot/1/title/'
DCCON_DETAILS_URL = 'https://dccon.dcinside.com/index/package_detail'
EMBED_COLOR = 0x4559e9


client = Bot(command_prefix='')


@client.event
async def on_ready():
    await client.change_presence(activity=Game(name='!도움'))
    log('SYSTEM', 'Bot ready')


@client.event
async def on_message(msg):
    # msg_fr = msg.server.name + ' > ' + msg.channel.name + ' > ' + msg.author.name
    # msg.server --> msg.guild
    # https://discordpy.readthedocs.io/en/latest/migrating.html#server-is-now-guild
    msg_guild = msg.guild
    msg_channel = msg.channel
    msg_author = msg.author
    msg_fr = f'{msg_guild.name} > {msg_channel.name} > {msg_author.name}'

    if msg.content.startswith('!'):  # usage: !dccon pkg name 01
        log(msg_fr, 'message identified: ' + msg.content)
        msg_content = msg.content[1:]

        if msg_content == '도움':
            log(msg_fr, 'help command')
            embed = Embed(title='안녕하세요! 디시콘 핫산이에요!',
                          description='명령어들은 아래에서 전부 보실 수 있어요.',
                          color=EMBED_COLOR)
            embed.add_field(name='사용 방법', value='!디시콘 패키지 제목 콘이름', inline=False)
            embed.add_field(name='사용 예시 1', value='!멘헤라콘 15, !마히로콘 리메이크 꿀잠, !좋은말콘 스페셜 에디션 응원, ...', inline=False)
            embed.add_field(name='사용 예시 2', value='!나나히라 라인, !카구야는인사받고싶어, ... (디시콘 패키지 이름만 입력 시 디시콘 목록 출력)', inline=False)
            # TODO: 로직을 아예 바꿔야됨
            embed.add_field(name='명령어', value='!도움, !대하여, !초대링크', inline=False)

            # embed.set_footer(text='그코좆망겜')

            await msg_channel.send(embed=embed)
        elif msg_content == '대하여':
            log(msg_fr, 'about command')
            embed = Embed(title='디시콘 핫산',
                          description='디시콘을 디스코드에서 쓸 수 있게 해주는 디스코드 봇입니다.',
                          color=EMBED_COLOR)
            embed.add_field(name='Repository', value='https://github.com/Dogdriip/dccon_hassan', inline=False)
            embed.add_field(name='Contribution', value='이슈나 PR 보내주세용', inline=False)

            await msg_channel.send(embed=embed)
        elif msg_content == '초대링크':
            log(msg_fr, 'invite command')

            url = 'https://discordapp.com/oauth2/authorize?&client_id=464437182887886850&scope=bot&permissions=101376'
            await msg_channel.send(f'봇 초대 링크 : {url}')

        else:
            msg_list = msg_content.split()
            idx = msg_list[-1]  # last word in message goes to index
            package_name = " ".join(str(x) for x in msg_list[0:-1])  # stupid fuckfuckfuckfuck

            log(msg_fr, f'interpreted: {package_name}, {idx}')

            if package_name == '':
                package_name = idx

            ############################################################################################################
            # respect https://github.com/gw1021/dccon-downloader/blob/master/python/app.py#L7:L18

            # TODO: 변수명 간단히

            s = requests.Session()

            package_search_req = s.get(DCCON_SEARCH_URL + package_name)
            package_search_html = BeautifulSoup(package_search_req.text, 'html.parser')
            package_search_list = package_search_html.select('#right_cont_wrap > div > div.dccon_listbox > ul > li')

            try:
                target_package = package_search_list[0]  # pick first dccon package (bs4 obj) from search list
            except IndexError as e:  # maybe no search result w/ IndexError?
                log(msg_fr, 'error! (maybe no search result) : ' + str(e))
                await msg_channel.send(f'"{package_name}" 디시콘 패키지 정보를 찾을 수 없습니다.')
            else:
                target_package_num = target_package.get('package_idx')  # get dccon number of target dccon package
                log(msg_fr, 'processing with: ' + target_package_num)

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

                # 로직 최적화 필요
                succeed = False
                for dccon in package_detail_json['detail']:
                    if dccon['title'] == idx:
                        dccon_img = "http://dcimg5.dcinside.com/dccon.php?no=" + dccon['path']
                        dccon_img_request = s.get(dccon_img, headers={'Referer': DCCON_HOME_URL})

                        buffer = BytesIO(dccon_img_request.content)
                        filename = package_detail_json['info']['title'] + '_' + dccon['title'] + '.' + dccon['ext']

                        await msg_channel.send(file=File(buffer, filename))
                        succeed = True
                        break
                if succeed:
                    log(msg_fr, 'succeed')
                else:
                    log(msg_fr, 'not found')
                    available_dccon_list = []
                    for dccon in package_detail_json['detail']:
                        available_dccon_list.append(dccon['title'])

                    await msg_channel.send(f'"{package_name}" 디시콘 패키지에서 "{idx}" 디시콘을 찾지 못했습니다.')
                    await msg_channel.send('사용 가능한 디시콘 : ' + ', '.join(available_dccon_list).rstrip(', '))
            #
            ############################################################################################################

if __name__ == "__main__":
    client.run(BOT_TOKEN)
