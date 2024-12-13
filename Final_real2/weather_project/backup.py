import os
import shutil
from datetime import datetime

USER_JSON_FILE = "user_data.json"
BACKUP_DIR = "backups"

def backup_user_data():
    """
    user_data.json 파일을 백업 디렉토리에 날짜별로 저장.
    """
    if not os.path.exists(USER_JSON_FILE):
        print(f"{USER_JSON_FILE} 파일이 존재하지 않습니다. 백업을 중단합니다.")
        return

    # 백업 디렉토리 생성
    os.makedirs(BACKUP_DIR, exist_ok=True)

    # 날짜를 포함한 백업 파일 이름 생성
    today_date = datetime.now().strftime("%Y-%m-%d")
    backup_file = os.path.join(BACKUP_DIR, f"backup_{today_date}.json")

    # JSON 파일 백업
    shutil.copy(USER_JSON_FILE, backup_file)
    print(f"백업 완료: {backup_file}")

# 백업 실행
if __name__ == "__main__":
    backup_user_data()
