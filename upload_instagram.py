import os
import time
import json
import requests
from datetime import timedelta
from google.cloud import storage
from dotenv import load_dotenv

load_dotenv()
ACCESS_TOKEN = os.getenv("IG_ACCESS_TOKEN")
IG_ACCOUNT_ID = os.getenv("IG_ACCOUNT_ID")

# [필수 세팅] 구글 클라우드 서비스 계정 키 파일 경로와 버킷 이름
# .env 파일에 등록해 두셨다면 os.getenv()로 불러오셔도 됩니다.
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "gcp_key.json"
GCP_BUCKET_NAME = "k-reels-temp-1234"

def upload_to_instagram(video_path, caption):
    print("\n인스타그램 릴스 발행 프로세스 시작...")
    
    # 1. 구글 클라우드 연동 및 파일명 난수 생성
    storage_client = storage.Client()
    bucket = storage_client.bucket(GCP_BUCKET_NAME)
    blob_name = f"reels_temp_{int(time.time())}.mp4"
    blob = bucket.blob(blob_name)
    
    print(f"1. 구글 클라우드에 임시 영상 업로드 중... ({blob_name})")
    blob.upload_from_filename(video_path)
    
    # 2. 메타 크롤러만 읽을 수 있는 15분짜리 시한부 직링크(Signed URL) 발급
    video_url = blob.generate_signed_url(version="v4", expiration=timedelta(minutes=15), method="GET")
    print("👉 구글 클라우드 임시 직링크 발급 성공 (15분 후 자동 만료)")
    
    try:
        print("2. 인스타그램 서버로 영상 전송 중...")
        url = f"https://graph.facebook.com/v18.0/{IG_ACCOUNT_ID}/media"
        payload = {
            "media_type": "REELS",
            "video_url": video_url,
            "caption": caption,
            "access_token": ACCESS_TOKEN
        }
        response = requests.post(url, data=payload)
        result = response.json()
        
        if "id" not in result:
            print("❌ 미디어 등록 실패 (디버깅):", result)
            return False
            
        creation_id = result["id"]
        print(f"미디어 등록 완료 (ID: {creation_id}). 서버 렌더링 상태 확인 중...")
        
        status_url = f"https://graph.facebook.com/v18.0/{creation_id}?fields=status_code,status&access_token={ACCESS_TOKEN}"
        
        while True:
            status_response = requests.get(status_url)
            status_result = status_response.json()
            status_code = status_result.get("status_code")
            
            if status_code == "FINISHED":
                print("\n✅ 인스타그램 렌더링 완료! 피드 발행을 시작합니다.")
                break
            elif status_code == "ERROR":
                print("\n❌ 인스타그램 렌더링 실패.")
                print(json.dumps(status_result, indent=4, ensure_ascii=False))
                return False
            else:
                print(f"현재 상태: {status_code}... 10초 후 다시 확인합니다.")
                time.sleep(10)
        
        print("3. 피드에 최종 발행 중...")
        publish_url = f"https://graph.facebook.com/v18.0/{IG_ACCOUNT_ID}/media_publish"
        publish_payload = {
            "creation_id": creation_id,
            "access_token": ACCESS_TOKEN
        }
        publish_response = requests.post(publish_url, data=publish_payload)
        publish_result = publish_response.json()
        
        if "id" in publish_result:
            print(f"\n🎉 100% 무인 릴스 자동 업로드 완료! (Post ID: {publish_result['id']})")
            return True
        else:
            print("❌ 발행 실패 (디버깅):", publish_result)
            return False

    finally:
        # 3. [핵심] 성공/실패 여부와 관계없이 구글 클라우드에서 파일 즉시 파기
        print(f"\n🧹 [마무리] 구글 클라우드 임시 영상 삭제 중... ({blob_name})")
        blob.delete()
        print("✨ 클라우드 용량 원상복구 완료! (서버에 찌꺼기가 남지 않습니다)")