# import subprocess
# import imageio_ffmpeg

# def burn_subtitles():
#     print("🚀 [6/6] 자막 하드코딩 및 영상 초고속 압축 중 (메타 타임아웃 방지)...")
    
#     ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
    
#     input_video = "tiktok_ready.mp4"
#     subtitle_file = "subtitles.srt"
#     output_video = "final_reels_with_subtitles.mp4"
    
#     command = [
#         ffmpeg_path,
#         "-y", 
#         "-i", input_video,
#         # 1. 릴스 규격(1080x1920) 강제 크롭 후 자막을 덧씌워 비율 에러 원천 차단
#         "-vf", f"scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,subtitles={subtitle_file}",
#         "-c:v", "libx264",
#         "-profile:v", "main",      
#         "-pix_fmt", "yuv420p",
#         "-r", "30",
#         # 2. 비트레이트를 2M로 제한하여 파일 용량을 극적으로 압축 (다운로드 타임아웃 방지)
#         "-b:v", "2M",
#         "-maxrate", "2M",
#         "-bufsize", "1M",
#         "-c:a", "aac",             
#         "-b:a", "128k",
#         "-ar", "44100",
#         "-ac", "2",
#         "-movflags", "+faststart", 
#         output_video
#     ]
    
#     try:
#         subprocess.run(command, check=True)
#         print(f"\n🎉 용량 압축 및 최종 결과물 [{output_video}] 생성 완료!")
#     except subprocess.CalledProcessError as e:
#         print("\n자막 합성 중 오류 발생:", e)

# if __name__ == "__main__":
#     burn_subtitles()
import os
import glob

# [강력 방어] 모든 Pillow 버전 호환성 강제 확보
from PIL import Image
try:
    resample_method = Image.Resampling.LANCZOS
except AttributeError:
    resample_method = getattr(Image, 'LANCZOS', 1)
if not hasattr(Image, 'ANTIALIAS'):
    Image.ANTIALIAS = resample_method

from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip

def burn_subtitles(video_path="tiktok_ready.mp4", subtitle_text=None, output_path="final_reels_with_subtitles.mp4"):
    """블랙 필터가 씌워진 영상 위에 가독성을 극대화한 자막 합성"""
    try:
        # 루트 절대 경로 강제 할당
        v_path = os.path.abspath(video_path)
        o_path = os.path.abspath(output_path)
        
        if not os.path.exists(v_path):
            print(f"❌ 4단계 완료 영상(tiktok_ready.mp4)을 찾을 수 없습니다: {v_path}")
            return False
            
        # 대본 파일 자동 탐색
        if subtitle_text is None:
            txt_files = glob.glob(os.path.join(os.path.dirname(v_path), "*.txt"))
            if txt_files:
                script_files = [f for f in txt_files if "requirements" not in os.path.basename(f)]
                if script_files:
                    with open(script_files[0], "r", encoding="utf-8") as f:
                        subtitle_text = f.read().strip()
                else:
                    subtitle_text = ""
            else:
                subtitle_text = ""

        print(f"✍️ 6단계: 자막 합성 시작... (대상 파일: {v_path})")
        video = VideoFileClip(v_path)
        
        if not subtitle_text or subtitle_text.strip() == "":
            print("⚠️ 적용할 자막 텍스트가 없어 원본을 그대로 저장합니다.")
            video.write_videofile(o_path, codec="libx264", audio_codec="aac", threads=2)
            return True

        # 자막 스타일링 강제 (크기 85, 볼드, 두꺼운 테두리)
        txt_clip = TextClip(
            subtitle_text,
            fontsize=85,              
            font='NanumGothicBold',   
            color='white',            
            stroke_color='black',     
            stroke_width=4,           
            method='caption',
            size=(900, None),
            align='center'
        )
        
        txt_clip = txt_clip.set_position(('center', 'center')).set_duration(video.duration)
        final_video = CompositeVideoClip([video, txt_clip])
        
        # 인스타그램 Meta API가 요구하는 필수 표준 규격 강제 주입
        final_video.write_videofile(
            o_path, 
            fps=30, 
            codec="libx264", 
            audio_codec="aac", 
            preset="fast",       # ultrafast에서 fast로 원복
            threads=2,
            ffmpeg_params=["-pix_fmt", "yuv420p", "-movflags", "faststart"], 
            logger=None
        )
        
        video.close()
        final_video.close()
        print("✅ 6단계: 최종 자막 릴스 렌더링 완료")
        return True

    except Exception as e:
        print(f"❌ 자막 합성 중 오류 발생: {e}")
        return False