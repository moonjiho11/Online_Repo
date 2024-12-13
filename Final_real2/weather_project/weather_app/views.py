import requests
import json
from datetime import datetime, timedelta
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils.timezone import localtime

# JSON 파일 저장 경로
USER_JSON_FILE = "user_data.json"

def save_users_to_json():
    """
    데이터베이스에 저장된 모든 사용자 데이터를 JSON 파일로 저장.
    """
    users = User.objects.all()
    user_data = [
        {
            "id": user.id,
            "username": user.username,
            "email": user.email if user.email else "None",
            # 시간대 변환
            "date_joined": localtime(user.date_joined).strftime("%Y-%m-%d %H:%M:%S"),
            "last_login": localtime(user.last_login).strftime("%Y-%m-%d %H:%M:%S") if user.last_login else "Never"
        }
        for user in users
    ]

    with open(USER_JSON_FILE, "w", encoding="utf-8") as file:
        json.dump(user_data, file, ensure_ascii=False, indent=4)

# 기상청 API 키
KMA_API_KEY = "2X1K2z0-SHO9Sts9PghzAw"
# Google Maps API 키
GOOGLE_API_KEY = "AIzaSyBV9xHdsunjLlXR6M4DtlAjJ-8k6AOwD2k"

def home(request):
    return render(request, 'home.html')

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            # 사용자 저장
            form.save()

            # JSON 파일 업데이트
            save_users_to_json()

            # 메시지 출력 및 리다이렉트
            messages.success(request, "회원가입이 완료되었습니다. 로그인해주세요.")
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('weather')
        else:
            messages.error(request, "로그인 정보가 올바르지 않습니다.")
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('home')

def get_location_name(lat, lng):
    """
    Geocoding API를 사용해 위도와 경도를 기반으로 지역명을 가져옵니다.
    """
    geocoding_url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        "latlng": f"{lat},{lng}",
        "key": GOOGLE_API_KEY,
        "language": "ko"  # 결과를 한국어로 반환
    }

    try:
        response = requests.get(geocoding_url, params=params)
        response.raise_for_status()
        data = response.json()

        if data.get("status") == "OK":
            location = data["results"][0]["formatted_address"]
            return location

        raise ValueError(
            f"Geocoding API 오류: {data.get('status')} - {data.get('error_message', 'No additional information')}")

    except requests.exceptions.RequestException as e:
        raise ValueError(f"API 호출 오류: {e}")


@login_required
def weather(request):
    """
    날씨 화면 초기 렌더링. 기본 화면에서는 사용자 위치 데이터를 요청하도록 함.
    """
    return render(request, 'weather.html', {
        "location": "사용자 위치를 가져오는 중입니다...",
        "updated_datetime": "정보 없음",
        "google_maps_url": None,
        "weather_data": None
    })

@login_required
def get_weather_data(request):
    """
    클라이언트가 전송한 위치 정보(위도, 경도)를 기반으로 날씨와 지역 정보를 반환.
    """
    lat = request.GET.get("lat")
    lng = request.GET.get("lng")

    if not lat or not lng:
        return JsonResponse({"error": "위치 정보가 제공되지 않았습니다."}, status=400)

    try:
        # 지역명 가져오기
        location_name = get_location_name(lat, lng)

        # 기상청 API 호출
        weather_api_url = "https://apihub.kma.go.kr/api/typ02/openApi/VilageFcstInfoService_2.0/getUltraSrtNcst"
        now = datetime.now()
        base_date = now.strftime("%Y%m%d")
        base_time = (now - timedelta(hours=now.hour % 6)).strftime("%H%M")

        weather_params = {
            "pageNo": 1,
            "numOfRows": 1000,
            "dataType": "JSON",
            "base_date": base_date,
            "base_time": base_time,
            "nx": 98,  # WGS84 -> 기상청 격자 변환 필요
            "ny": 76,
            "authKey": KMA_API_KEY
        }

        response = requests.get(weather_api_url, params=weather_params)
        response.raise_for_status()
        data = response.json()

        # 데이터 처리
        category_map = {
            "REH": "습도 (%)",
            "RN1": "1시간 강수량 (mm)",
            "T1H": "기온 (°C)",
            "VEC": "풍향 (deg)",
            "WSD": "풍속 (m/s)"
        }

        items = data["response"]["body"]["items"]["item"]
        weather_data = [
            {"category": category_map[item["category"]], "value": item["obsrValue"]}
            for item in items if item["category"] in category_map
        ]

        updated_datetime = f"{base_date[:4]}년 {base_date[4:6]}월 {base_date[6:]}일 {base_time[:2]}시"

        return JsonResponse({
            "location": location_name,
            "updated_datetime": updated_datetime,
            "weather_data": weather_data,
            "latitude": float(lat),  # 위도 추가
            "longitude": float(lng),  # 경도 추가
        })

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)