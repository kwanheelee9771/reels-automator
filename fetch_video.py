import os
import random
import requests
from dotenv import load_dotenv

load_dotenv()
PIXABAY_API_KEY = os.getenv("PIXABAY_API_KEY")

def download_background_video(keyword="seoul"):
    print(f"[{keyword}] 키워드로 Pixabay 세로 영상 검색 중...")
    
    # Pixabay Video API 호출 (세로형 orientation=vertical 지정)
    url = f"https://pixabay.com/api/videos/?key={PIXABAY_API_KEY}&q={keyword}&video_type=film&orientation=vertical"
    
    response = requests.get(url)
    if response.status_code != 200:
        print("API 호출 에러:", response.text)
        return False
        
    data = response.json()
    if int(data.get("totalHits", 0)) == 0:
        print("해당 키워드의 영상을 찾을 수 없습니다.")
        return False
        
    # 매번 다른 영상이 나오도록 랜덤 선택
    video = random.choice(data["hits"])
    
    # 제공되는 해상도 중 large 또는 medium 사이즈 추출
    videos = video["videos"]
    download_link = videos.get("large", {}).get("url") or videos.get("medium", {}).get("url")
    
    if not download_link:
        print("다운로드 가능한 영상 링크를 찾을 수 없습니다.")
        return False
        
    print("영상 다운로드 중...")
    video_data = requests.get(download_link)
    
    with open("background.mp4", "wb") as f:
        f.write(video_data.content)
        
    print("성공! 새로운 background.mp4 파일이 준비되었습니다.")
    return True

if __name__ == "__main__":
    download_background_video("seoul")