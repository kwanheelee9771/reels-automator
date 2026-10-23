import os
from dotenv import load_dotenv
from openai import OpenAI

# API 키 불러오기
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def extract_subtitles():
    print("음성 분석 및 타이밍 추출 중 (Whisper API)...")
    
    # 1. 앞서 생성한 음성 파일 열기
    audio_file = open("voice.mp3", "rb")
    
    # 2. Whisper 모델을 사용해 오디오를 SRT(자막) 형식으로 변환
    transcript = client.audio.transcriptions.create(
        model="whisper-1", 
        file=audio_file, 
        response_format="srt"
    )
    
    # 3. 자막 파일 저장
    subtitle_filename = "subtitles.srt"
    with open(subtitle_filename, "w", encoding="utf-8") as f:
        f.write(transcript)
        
    print(f"자막 추출 완료! {subtitle_filename} 파일이 저장되었습니다.")

if __name__ == "__main__":
    extract_subtitles()