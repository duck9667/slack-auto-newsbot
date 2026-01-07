[![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)]()

# Slack을 활용한 자동 뉴스봇 (Slack Auto Newsbot)

간단한 웹 크롤러로 뉴스(또는 공지) 내용을 수집하여 Slack의 특정 채널로 자동 전송하는 봇입니다.  
주요 구성 요소는 BeautifulSoup을 이용한 크롤링, Slack Webhook/Token을 통한 메시지 전송이며, 주기적 실행을 위해 GCP(Cloud Scheduler / Cloud Run 또는 VM의 cron)를 사용할 수 있습니다.

![예시화면](https://user-images.githubusercontent.com/33515088/107921848-799b1300-6fb2-11eb-8fc8-3f666a98094b.png)

## 주요 기능
- BeautifulSoup을 사용한 뉴스/웹 페이지 크롤링
- Slack으로 포맷된 메시지(텍스트, 링크 등) 전송 (Webhook 또는 Bot Token 사용)
- GCP를 활용한 주기적 자동 실행(Cloud Scheduler, Cloud Run 또는 VM cron)
- 간단한 구성으로 로컬 실행 및 클라우드 배포 가능

---

## 요구 사항(예시)
- Python 3.8+
- 주요 패키지: requests, beautifulsoup4, python-dotenv (사용 시)
- GCP 계정(클라우드에서 주기 실행 시)
- Slack 워크스페이스 권한: Incoming Webhook 또는 Bot Token

requirements.txt 예시
```
requests
beautifulsoup4
python-dotenv
```

---

## 설치 및 빠른 시작 (로컬)
1. 레포지토리 클론
   - git clone https://github.com/duck9667/slack-auto-newsbot.git
2. 가상 환경 생성 및 활성화
   - python -m venv venv
   - source venv/bin/activate  (Windows: venv\Scripts\activate)
3. 의존성 설치
   - pip install -r requirements.txt
4. 환경 변수 설정
   - 프로젝트 루트에 `.env` 파일을 만들거나 환경 변수로 설정합니다. 예:
     ```
     SLACK_WEBHOOK_URL=https://hooks.slack.com/services/XXX/YYY/ZZZ
     SLACK_CHANNEL=#news
     NEWS_SOURCE_URL=https://example.com/news
     ```
   - 또는 Bot Token을 사용하는 경우:
     ```
     SLACK_BOT_TOKEN=xoxb-....
     ```
5. 스크립트 실행
   - 예: `python bot.py` 또는 실제 프로젝트의 실행 파일명으로 실행하세요.
   - (프로젝트에 따라 `main.py`, `app.py` 등으로 파일명이 다를 수 있습니다.)

---

## 구성(설명)
- SLACK_WEBHOOK_URL: Slack Incoming Webhook URL. Webhook을 사용하여 메시지를 전송합니다.
- SLACK_BOT_TOKEN: Bot Token을 사용할 때 필요(차후 기능 확장 시).
- SLACK_CHANNEL: 메시지를 보낼 채널 (예: `#general`).
- NEWS_SOURCE_URL(S): 크롤링할 뉴스 페이지 또는 RSS/목록 URL들.
- SCHEDULE: (로컬 테스트용) 실행 주기 정보. 클라우드에서는 Cloud Scheduler나 Cron 사용.

---

## Slack에 메시지 전송 예시 (간단한 포맷)
- 제목 (헤드라인)
- 링크 (원문)
- 요약 (크롤링으로 추출한 짧은 요약 또는 첫 문단)
- 발행일 (가능하면)

코드 예시(요약)
```python
import requests

payload = {
    "channel": "#news",
    "text": "*[뉴스 제목]*\nhttp://news.example.com/123\n요약 내용..."
}
requests.post(os.getenv("SLACK_WEBHOOK_URL"), json=payload)
```

---

## GCP에 배포하고 주기적으로 실행하는 방법(요약)
여러 가지 방법이 있으나 일반적인 워크플로는 다음과 같습니다:

옵션 A — Cloud Run + Cloud Scheduler
1. 애플리케이션을 컨테이너로 패키징하여 Cloud Run에 배포.
2. Cloud Scheduler에서 HTTP 타겟으로 Cloud Run의 엔드포인트를 주기 호출하도록 설정.
3. 필요한 비밀(웹훅 URL 등)은 Secret Manager에 보관하고 Cloud Run에서 읽도록 구성.

옵션 B — Cloud Function + Cloud Scheduler
1. 크롤링 및 메시지 전송 로직을 Cloud Function으로 작성.
2. Cloud Scheduler가 HTTP로 Cloud Function을 정기 호출.

옵션 C — VM(Compute Engine) + cron
1. VM에 코드 배치 및 가상환경 설정.
2. crontab에 주기 실행 스케줄 추가.

참고: 배포 시 비밀(웹훅, 토큰)을 코드에 하드코딩하지 말고 환경 변수 또는 Secret Manager를 사용하세요.

---

## 스케줄 예시 (crontab)
매일 오전 9시에 실행:
```
0 9 * * * /path/to/venv/bin/python /path/to/bot.py >> /var/log/newsbot.log 2>&1
```

GitHub Actions에서 스케줄링:
```yaml
on:
  schedule:
    - cron: '0 9 * * *'  # UTC 기준
jobs:
  run:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: run bot
        run: |
          python -m pip install -r requirements.txt
          python bot.py
```

---

## 문제 해결 및 팁
- Slack 메시지가 도착하지 않음: Webhook URL 또는 채널 권한 확인, 요청 로그(HTTP 응답 코드) 확인
- 크롤링이 실패함: 타겟 사이트의 HTML 구조 변경 가능성 — BeautifulSoup 선택자 재검토
- 배포 시 환경변수 누락이나 권한 문제: Secret/Service Account 권한 확인

---

## 기여
이 프로젝트는 단순한 템플릿 형태입니다. 개선(예: RSS 지원, 중복 전송 방지, 요약(요약 모델 연동), 에러 알림 등) 환영합니다. Pull request나 issue를 통해 제안해주세요.

---

## 라이선스
원하시는 라이선스(예: MIT)를 추가하세요.
