# 디시콘 핫산
디시콘을 디스코드에서 쓸 수 있게 해주는 디스코드 봇입니다.

## Demo
[봇 초대 링크](https://discordapp.com/oauth2/authorize?&client_id=464437182887886850&scope=bot&permissions=101376)

Heroku 무료 Dyno에서 테스트용으로 돌아가고 있는 봇입니다. 사용자가 몰리면 봇 응답이 느려지거나 봇이 꺼질 수 있으며, 예고 없이 봇 작동이 중지될 수 있습니다. 

## 설치 및 실행
```
$ pip3 install -r requirements.txt
$ echo "BOT_TOKEN=<YOUR_BOT_TOKEN_HERE>" > .env
$ echo "PREFIX=<YOUR_PREFIX_HERE>" >.env
$ python3 main.py
```

## 사용법
!콘 "디시콘 패키지 제목" "콘 이름"  
사용 예시 1 : !콘 멘헤라콘 15, !콘 "마히로콘 리메이크" 꿀잠, !콘 "좋은말콘 스페셜 에디션" 응원, ...  
사용 예시 2 : !콘 "나나히라 라인", !콘 카구야는인사받고싶어, ... (디시콘 패키지 이름만 입력 시 디시콘 목록 출력)  
다른 커맨드는 봇 초대해서 "!도움" 입력

다른 봇 호출 명령어를 사용하려면 .env에 PREFIX 를 넣어주세요. 기본값은 !입니다.

## TODO
* 라이센스 추가
* 즐겨찾기 기능 추가 (매크로)
* 이것저것
* 디시콘 다운받는 부분을 별도의 모듈로 분리
