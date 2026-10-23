import os
import sys
import random
import logging
from datetime import datetime

# 하위 모듈 임포트
from fetch_video import download_background_video
from generate_audio import create_reels_audio
from render import make_reels_video
from merge import merge_video_audio
from generate_subtitles import extract_subtitles
from burn_subtitles import burn_subtitles
from upload_instagram import upload_to_instagram

# [1] 실행 기준 디렉터리 절대 경로 고정 (서버 Cron 실행 환경 대응)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def get_abs_path(filename: str) -> str:
    """파일명이 주어지면 BASE_DIR 기준의 절대 경로 반환"""
    return os.path.join(BASE_DIR, filename)

# [2] 영구 로깅 세팅 (터미널 출력 및 월별 파일 기록 동시 수행)
log_filename = get_abs_path(f"pipeline_{datetime.now().strftime('%Y%m')}.log")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(log_filename, encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ]
)

def cleanup_old_files():
    """이전 실행에서 남아있을 수 있는 임시 미디어 및 자막 파일 강제 삭제"""
    target_files = [
        "background_video.mp4",
        "voice.mp3",
        "tiktok_ready.mp4",
        "merged_video.mp4",
        "subtitles.srt",
        "final_reels_with_subtitles.mp4"
    ]
    for filename in target_files:
        file_path = get_abs_path(filename)
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                logging.info(f"🧹 임시 찌꺼기 파일 정리 완료: {filename}")
            except Exception as e:
                logging.warning(f"⚠️ 파일 삭제 실패 ({filename}): {e}")

def run_pipeline(topic: str, video_keyword: str) -> bool:
    """1~6단계 영상 수집, 가공, 자막 합성 전체 파이프라인 제어"""
    logging.info("=" * 60)
    logging.info("🎬 K-Culture 숏폼 제작 파이프라인 가동")
    logging.info(f"📌 주제: {topic}")
    logging.info(f"🔍 키워드: {video_keyword}")
    logging.info("=" * 60)

    # 0. 찌꺼기 정리
    cleanup_old_files()

    # 1. 배경 영상 수집
    logging.info("🚀 [1/6] 배경 영상 수집 시작...")
    try:
        download_success = download_background_video(video_keyword)
        if not download_success:
            logging.error("❌ [1/6] 영상 수집 실패 (반환값 False)")
            return False
    except Exception as e:
        logging.error(f"❌ [1/6] 영상 수집 중 예외 발생: {e}")
        return False

    # 2. AI 영어 대본 및 음성 생성
    logging.info("🚀 [2/6] AI 영어 대본 및 음성 생성...")
    try:
        create_reels_audio(topic)
    except Exception as e:
        logging.error(f"❌ [2/6] 음성 생성 실패: {e}")
        return False

    # 3. 인스타그램 릴스 규격(9:16) 렌더링
    logging.info("🚀 [3/6] 인스타그램 릴스 규격(9:16) 렌더링...")
    try:
        make_reels_video()
    except Exception as e:
        logging.error(f"❌ [3/6] 영상 렌더링 실패: {e}")
        return False

    # 4. 영상 + AI 음성 합성
    logging.info("🚀 [4/6] 영상 + AI 음성 합성...")
    try:
        merge_video_audio()
    except Exception as e:
        logging.error(f"❌ [4/6] 영상/음성 합성 실패: {e}")
        return False

    # 5. Whisper API 자막(SRT) 추출
    logging.info("🚀 [5/6] Whisper API 자막(SRT) 추출...")
    try:
        extract_subtitles()
    except Exception as e:
        logging.error(f"❌ [5/6] 자막 추출 실패: {e}")
        return False

    # 6. 영상에 자막 굽기 (최종 렌더링)
    logging.info("🚀 [6/6] 영상에 자막 굽기 (최종 렌더링)...")
    try:
        burn_subtitles()
    except Exception as e:
        logging.error(f"❌ [6/6] 자막 굽기 실패: {e}")
        return False

    # 최종 결과물 존재 여부 검증
    final_output = get_abs_path("final_reels_with_subtitles.mp4")
    if not os.path.exists(final_output) or os.path.getsize(final_output) == 0:
        logging.error("❌ 최종 렌더링 파일(final_reels_with_subtitles.mp4)이 없거나 0바이트입니다.")
        return False

    logging.info("✅ 100% 무인 숏폼 생성 성공 완료!")
    return True

if __name__ == "__main__":
    # [방어 1] 실행 전 필수 API 키 및 환경 변수 누락 조기 검사 (Fail-Fast)
    required_keys = ["OPENAI_API_KEY", "IG_ACCESS_TOKEN", "IG_ACCOUNT_ID", "GOOGLE_APPLICATION_CREDENTIALS"]
    missing_keys = [key for key in required_keys if not os.environ.get(key)]
    
    if missing_keys:
        logging.error(f"🚨 치명적 오류: 필수 환경 변수가 누락되었습니다: {missing_keys}")
        logging.error("GitHub Secrets 설정을 확인하세요. 파이프라인을 중단합니다.")
        sys.exit(1)

    CONTENT_POOL = [
        {
            "keyword": "seoul aesthetic",
            "topic": "Top 3 aesthetic spots in Seoul you MUST visit in 2026",
            "caption": "Explore the hidden aesthetics of Seoul! 🇰🇷✨ Which spot would you visit first? #Seoul #KoreaTravel #VisitKorea #Aesthetic"
        },
        {
            "keyword": "korean food street",
            "topic": "3 must-try Korean street foods that will blow your mind",
            "caption": "Warning: Do NOT watch this if you're hungry! 🤤🍢 Tag a friend you'd eat this with! #KoreanFood #StreetFood #KFood #Mukbang"
        },
        {
            "keyword": "korea cafe",
            "topic": "The most unique concept cafes in South Korea",
            "caption": "Korean cafe culture hits totally different ☕️✨ Save this for your next Seoul trip! #SeoulCafe #KoreanCulture #TravelKorea #CafeHopping"
        },
        {
            "keyword": "kpop dance",
            "topic": "Why K-pop choreographies are getting harder every year",
            "caption": "The synchronization is unreal! 🎤🔥 Who is your favorite K-pop dancer? #Kpop #KpopDance #KpopIdol #Kculture"
        },
        {
            "keyword": "hanok village seoul",
            "topic": "A peaceful walk inside Korea's traditional Hanok village",
            "caption": "Where tradition meets modern Seoul 🏯🌸 #Hanok #Bukchon #SeoulVibes #KoreaTrip"
        }
    ]

    # [방어 2] 상태가 초기화되는 깃허브 서버를 위한 '날짜 기반' 순차 할당 (중복 차단)
    # 1970년 1월 1일 이후 경과한 날짜를 리스트 길이(5)로 나눈 나머지(0~4)를 인덱스로 사용
    day_index = datetime.now().toordinal() % len(CONTENT_POOL)
    selected = CONTENT_POOL[day_index]
    
    current_topic = selected["topic"]
    current_keyword = selected["keyword"]
    current_caption = selected["caption"]

    # 파이프라인 실행
    pipeline_success = run_pipeline(current_topic, current_keyword)

    if not pipeline_success:
        logging.error("🚨 파이프라인 생성 단계 실패로 전체 프로세스를 중단합니다.")
        sys.exit(1)

    # 7. 인스타그램 자동 업로드 및 발행
    logging.info("🚀 [7/7] 인스타그램 자동 업로드 시작...")
    final_video_file = get_abs_path("final_reels_with_subtitles.mp4")

    try:
        upload_success = upload_to_instagram(final_video_file, current_caption)
        if not upload_success:
            logging.error("🚨 인스타그램 업로드/발행 단계에서 실패했습니다.")
            sys.exit(1)
    except Exception as e:
        logging.error(f"🚨 인스타그램 업로드 함수 호출 중 예외 발생: {e}")
        sys.exit(1)

    logging.info("=" * 60)
    logging.info("🎉 [전체 완료] 영상 생성부터 인스타그램 릴스 발행까지 성공했습니다.")
    logging.info("=" * 60)
    sys.exit(0)