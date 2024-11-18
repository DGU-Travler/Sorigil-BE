
#-*- coding:utf-8 -*-
import pyaudio
import urllib3
import json
import base64
import time
import environ
from pathlib import Path
import os

env = environ.Env(DEBUG=(bool, True))
BASE_DIR = Path(__file__).resolve().parent.parent

environ.Env.read_env(os.path.join(BASE_DIR, '.env'))
openApiURL = "http://aiopen.etri.re.kr:8000/WiseASR/Recognition"
accessKey = env('ETRI_API_KEY')
languageCode = "korean"
 
chunk = 1024
FORMAT = pyaudio.paInt16
Channels = 1
Rate = 16000
device_index = 1
record_seconds = 5



p = pyaudio.PyAudio()
stream = p.open(format=FORMAT,
                channels=Channels,
                rate=Rate,
                input=True,
                frames_per_buffer=chunk,
                input_device_index=device_index)

print("녹음 시작...")
http = urllib3.PoolManager()

frames = []  # 오디오 데이터를 저장할 리스트
start_time = time.time()

try:
    while time.time() - start_time < record_seconds:
        data = stream.read(chunk, exception_on_overflow=False)
        frames.append(data)

    # 오디오 데이터를 base64로 인코딩
    audioContents = base64.b64encode(b''.join(frames)).decode("utf8")

    # JSON 요청 생성
    requestJson = {
        "argument": {
            "language_code": languageCode,
            "audio": audioContents
        }
    }

    # API 요청
    response = http.request(
        "POST",
        openApiURL,
        headers={
            "Content-Type": "application/json; charset=UTF-8",
            "Authorization": accessKey
        },
        body=json.dumps(requestJson)
    )

    # 응답 출력
    print("[responseCode]", response.status)
    print("[responseBody]", str(response.data, "utf-8"))
except Exception as e:
    print("Error occurred:", str(e))

except KeyboardInterrupt:
    print("녹음 종료")

except Exception as e:
    print("Error occurred:", str(e))

finally:
    stream.stop_stream()
    stream.close()
    p.terminate()