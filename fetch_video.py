import os
import requests
import random

def download_background_video(video_keyword):
    """Pixabay API를 최적화하여 고품질 세로형 영상을 무작위로 다운로드합니다."""
    api_key = os.environ.get("PIXABAY_API_KEY")
    if not api_key:
        print("❌ PIXABAY_API_KEY 환경 변수가 설정되지 않았습니다.")
        return False

    # 최적화 1: orientation=vertical (세로형 강제), safesearch=true (안전한 영상), per_page=15 (상위 15개 추출)
    url = f"https://pixabay.com/api/videos/?key={api_key}&q={video_keyword}&video_type=film&orientation=vertical&safesearch=true&per_page=15"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        total_hits = int(data.get("totalHits", 0))

        if total_hits > 0:
            # 검색된 결과 리스트 (최대 15개)
            hits = data.get("hits", [])
            
            # 최적화 2: 항상 1위가 아닌 상위 결과물 중 무작위로 하나 선택 (도배 방지)
            selected_video = random.choice(hits)
            
            # 해상도가 가장 안정적인 medium 사이즈 URL 추출
            video_url = selected_video["videos"]["medium"]["url"]
            
            print(f"📥 픽사베이 세로형 영상 다운로드 중... (키워드: {video_keyword}, 선택된 영상 ID: {selected_video['id']})")
            video_response = requests.get(video_url, stream=True)
            video_response.raise_for_status()
            
            local_filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), "background_video.mp4")
            
            with open(local_filename, 'wb') as f:
                for chunk in video_response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            print("✅ 픽사베이 최적화 배경 영상 다운로드 완료")
            return True
        else:
            print(f"❌ '{video_keyword}' 키워드에 대한 세로형 영상을 픽사베이에서 찾을 수 없습니다.")
            return False
            
    except Exception as e:
        print(f"❌ 픽사베이 영상 수집 중 오류 발생: {e}")
        return False