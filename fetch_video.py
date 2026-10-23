# import os
# import requests
# import random

# def download_background_video(video_keyword):
#     """Pixabay API를 최적화하여 고품질 세로형 영상을 무작위로 다운로드합니다."""
#     api_key = os.environ.get("PIXABAY_API_KEY")
#     if not api_key:
#         print("❌ PIXABAY_API_KEY 환경 변수가 설정되지 않았습니다.")
#         return False

#     # 최적화 1: orientation=vertical (세로형 강제), safesearch=true (안전한 영상), per_page=15 (상위 15개 추출)
#     url = f"https://pixabay.com/api/videos/?key={api_key}&q={video_keyword}&video_type=film&orientation=vertical&safesearch=true&per_page=15"
    
#     try:
#         response = requests.get(url)
#         response.raise_for_status()
#         data = response.json()
        
#         total_hits = int(data.get("totalHits", 0))

#         if total_hits > 0:
#             # 검색된 결과 리스트 (최대 15개)
#             hits = data.get("hits", [])
            
#             # 최적화 2: 항상 1위가 아닌 상위 결과물 중 무작위로 하나 선택 (도배 방지)
#             selected_video = random.choice(hits)
            
#             # 해상도가 가장 안정적인 medium 사이즈 URL 추출
#             video_url = selected_video["videos"]["medium"]["url"]
            
#             print(f"📥 픽사베이 세로형 영상 다운로드 중... (키워드: {video_keyword}, 선택된 영상 ID: {selected_video['id']})")
#             video_response = requests.get(video_url, stream=True)
#             video_response.raise_for_status()
            
#             local_filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), "background_video.mp4")
            
#             with open(local_filename, 'wb') as f:
#                 for chunk in video_response.iter_content(chunk_size=8192):
#                     f.write(chunk)
            
#             print("✅ 픽사베이 최적화 배경 영상 다운로드 완료")
#             return True
#         else:
#             print(f"❌ '{video_keyword}' 키워드에 대한 세로형 영상을 픽사베이에서 찾을 수 없습니다.")
#             return False
            
#     except Exception as e:
#         print(f"❌ 픽사베이 영상 수집 중 오류 발생: {e}")
#         return False
import os
import requests
import random

def download_background_video(video_keyword):
    """새로운 RapidAPI 구조(videos 배열)에 맞춘 틱톡 다운로드"""
    rapidapi_key = os.environ.get("RAPIDAPI_KEY")
    if not rapidapi_key:
        print("❌ RAPIDAPI_KEY 환경 변수가 설정되지 않았습니다.")
        return False

    # [수정 필수] 새로 찾으신 API의 URL과 Host 주소로 반드시 변경하세요.
    raw_url = "https://tiktok-api6.p.rapidapi.com/search/general/query?query=mreast&sort_type=0"
    base_url = raw_url.split("?")[0] 
    
    headers = {
        "X-RapidAPI-Key": rapidapi_key,
        "X-RapidAPI-Host": "tiktok-api6.p.rapidapi.com",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    # 주의: API 화면 좌측 파라미터 탭에서 검색어 변수명이 'keyword'인지 'query'인지 확인 후 맞춰주세요.
    # (JSON 응답에 "query": "mr beast"로 찍힌 것으로 보아 파라미터명이 query일 확률이 높습니다)
    querystring = {"query": video_keyword} # 만약 작동 안 하면 "keyword": video_keyword 로 변경

    try:
        print(f"🔍 틱톡 영상 검색 중... (키워드: {video_keyword})")
        response = requests.get(base_url, headers=headers, params=querystring)
        response.raise_for_status()
        
        data = response.json()
            
        # 1. 올려주신 구조에 맞춰 'videos' 배열에서 데이터를 꺼냅니다.
        video_list = data.get("videos", [])
        if not video_list:
            print("❌ 검색된 틱톡 영상이 없습니다.")
            return False
            
        selected_video = random.choice(video_list)
        
        # 2. 올려주신 구조에 맞춰 워터마크 없는 URL을 즉시 추출합니다.
        video_url = selected_video.get("unwatermarked_download_url") or selected_video.get("download_url")
        
        if not video_url:
            print("❌ 영상 다운로드 URL을 찾을 수 없습니다.")
            return False

        print("📥 워터마크 없는 틱톡 영상 다운로드 중...")
        video_response = requests.get(video_url, stream=True)
        video_response.raise_for_status()
        
        local_filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), "background_video.mp4")
        with open(local_filename, 'wb') as f:
            for chunk in video_response.iter_content(chunk_size=8192):
                f.write(chunk)
                
        print("✅ 틱톡 배경 영상 다운로드 완료")
        return True

    except Exception as e:
        print(f"❌ 틱톡 영상 수집 중 오류 발생: {e}")
        return False