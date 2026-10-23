import os
from dotenv import load_dotenv
from openai import OpenAI

# .env 파일에서 API 키 불러오기
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def create_reels_audio(topic):
    print(f"[{topic}] 주제로 영문 대본 생성 중...")
    
    # 1. 숏폼용 영어 대본 생성 (GPT-4o-mini 사용 - 비용 효율적)
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a viral TikTok/Instagram Reels scriptwriter. Write a 30-second script. Start with a very strong hook. Only provide the spoken text, no visual cues or sound effect notes. Keep it natural and engaging."},
            {"role": "user", "content": f"Write a script about: {topic}"}
        ]
    )
    script_text = completion.choices[0].message.content
    print("\n--- 생성된 대본 ---")
    print(script_text)
    print("-------------------\n")
    
    print("음성(TTS) 파일 생성 중...")
    
    # 2. 대본을 원어민 음성(mp3)으로 변환 (OpenAI TTS API)
    # voice 옵션: alloy, echo, fable, onyx, nova, shimmer 중 선택 가능 (nova가 자연스러운 여성 음성)
    response = client.audio.speech.create(
        model="tts-1",
        voice="nova",
        input=script_text
    )
    
    # 3. mp3 파일로 저장
    audio_filename = "voice.mp3"
    response.stream_to_file(audio_filename)
    print(f"성공! {audio_filename} 파일이 저장되었습니다.")

if __name__ == "__main__":
    # 테스트 주제: 외국인이 환장하는 서울의 숨겨진 명소
    test_topic = "A hidden, aesthetic Hanok cafe in Seoul that tourists don't know about."
    create_reels_audio(test_topic)