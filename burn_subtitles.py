import subprocess
import imageio_ffmpeg

def burn_subtitles():
    print("🚀 [6/6] 자막 하드코딩 및 영상 초고속 압축 중 (메타 타임아웃 방지)...")
    
    ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
    
    input_video = "tiktok_ready.mp4"
    subtitle_file = "subtitles.srt"
    output_video = "final_reels_with_subtitles.mp4"
    
    command = [
        ffmpeg_path,
        "-y", 
        "-i", input_video,
        # 1. 릴스 규격(1080x1920) 강제 크롭 후 자막을 덧씌워 비율 에러 원천 차단
        "-vf", f"scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,subtitles={subtitle_file}",
        "-c:v", "libx264",
        "-profile:v", "main",      
        "-pix_fmt", "yuv420p",
        "-r", "30",
        # 2. 비트레이트를 2M로 제한하여 파일 용량을 극적으로 압축 (다운로드 타임아웃 방지)
        "-b:v", "2M",
        "-maxrate", "2M",
        "-bufsize", "1M",
        "-c:a", "aac",             
        "-b:a", "128k",
        "-ar", "44100",
        "-ac", "2",
        "-movflags", "+faststart", 
        output_video
    ]
    
    try:
        subprocess.run(command, check=True)
        print(f"\n🎉 용량 압축 및 최종 결과물 [{output_video}] 생성 완료!")
    except subprocess.CalledProcessError as e:
        print("\n자막 합성 중 오류 발생:", e)

if __name__ == "__main__":
    burn_subtitles()