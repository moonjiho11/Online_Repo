from datetime import datetime, timedelta
import json
import pandas as pd
import requests

# 데이터 로드
data = pd.read_excel('http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getUltraSrtFcst?key="9WmYIaybS0epmCGsmytHvw&Seoul&api=yes')


print(data.head())

# 설정 값  김해 좌표
servicekey = "9WmYIaybS0epmCGsmytHvw"
base_date = '20230503' # 발표 일자
base_time = '0700' # 발표 시간
nx = '94' # 예보 지점 x좌표
ny = '77' # 예보 지점 y좌표
input_d = datetime.strptime(base_date + base_time, "%Y%m%d%H%M" )
print(input_d)

# 실제 입력 시간
input_d = datetime.strptime(base_date + base_time, "%Y%m%d%H%M" ) - timedelta(hours=1)
print(input_d)

input_datetime = datetime.strftime(input_d, "%Y%m%d%H%M")
input_date = input_datetime[:-4]
input_time = input_datetime[-4:]
url = f"http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getUltraSrtFcst?serviceKey"
print(url)

# API 호출
response = requests.get(url, verify=False)
res = json.loads(response.text)
informations = dict()

# 데이터 파싱
for items in res['response']['body']['items']['item']:
    cate = items['category']
    fcstTime = items['fcstTime']
    fcstValue = items['fcstValue']
    if fcstTime not in informations:
        informations[fcstTime] = dict()
    informations[fcstTime][cate] = fcstValue

print(informations)

# 코드 정의
sky_code = {1 : '맑음', 3 : '구름많음', 4 : '흐림'}

# 결과 출력
for key, val in zip(informations.keys(), informations.values()):
    template = f"""{base_date[:4]}년 {base_date[4:6]}월 {base_date[-2:]}일 {key[:2]}시 {key[2:]}분 {(int(nx), int(ny))} 지역의 날씨는 """ 
    
    if 'SKY' in val:
        sky_temp = sky_code[int(val['SKY'])]
        template += sky_temp + " "
    
    if 'T1H' in val:
        t1h_temp = float(val['T1H'])
        template += f" 기온 {t1h_temp}℃ "
    
    print(template)
