from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import time


def get_full_html(url, wait_time=10):
    """
    Selenium을 사용하여 전체 HTML을 가져오는 함수

    Parameters:
    url (str): 크롤링할 웹페이지의 URL
    wait_time (int): 페이지 로딩 대기 시간 (초)

    Returns:
    str: 전체 HTML 코드
    """
    # Chrome 옵션 설정
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # 브라우저 창 안 띄움
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920x1080')
    chrome_options.add_argument(
        '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

    try:
        # WebDriver 초기화
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(url)

        # 페이지가 완전히 로드될 때까지 대기
        time.sleep(wait_time)  # 동적 콘텐츠가 로드될 때까지 대기

        # 페이지 스크롤
        last_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            # 페이지 끝까지 스크롤
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)  # 새로운 내용이 로드될 때까지 대기

            # 새로운 높이 계산
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        # 전체 HTML 가져오기
        full_html = driver.page_source

        return full_html

    except Exception as e:
        print(f"에러 발생: {str(e)}")
        return None

    finally:
        driver.quit()


def save_html(html, filename="output.html"):
    """
    HTML을 파일로 저장하는 함수

    Parameters:
    html (str): 저장할 HTML 문자열
    filename (str): 저장할 파일 이름
    """
    if html:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"HTML이 {filename}로 저장되었습니다.")
    else:
        print("저장할 HTML이 없습니다.")


# 사용 예시
if __name__ == "__main__":
    url = "https://www.naver.com"  # 크롤링하고 싶은 웹사이트 URL
    html_content = get_full_html(url)
    save_html(html_content)