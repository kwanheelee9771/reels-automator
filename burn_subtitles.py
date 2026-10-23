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

# [핵심 방어 코드] MoviePy와 최신 Pillow 버전 충돌 강제 해결
from PIL import Image
if not hasattr(Image, 'ANTIALIAS'):
    Image.ANTIALIAS = Image.LANCZOS

from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip

def burn_subtitles(video_path="rendered_video.mp4", subtitle_text=None, output_path="final_reels_with_subtitles.mp4"):
    """블랙 필터가 씌워진 영상 위에 가독성을 극대화한 자막 합성"""
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        v_path = os.path.join(base_dir, video_path)
        o_path = os.path.join(base_dir, output_path)
        
        if not os.path.exists(v_path):
            print(f"❌ 1차 렌더링된 영상이 없습니다: {v_path}")
            return False
            
        if subtitle_text is None:
            txt_files = glob.glob(os.path.join(base_dir, "*.txt"))
            if txt_files:
                script_files = [f for f in txt_files if "requirements" not in f]
                if script_files:
                    with open(script_files[0], "r", encoding="utf-8") as f:
                        subtitle_text = f.read().strip()
                else:
                    subtitle_text = ""
            else:
                subtitle_text = ""

        print(f"✍️ 자막 합성 시작... (자막 길이: {len(subtitle_text)}자)")
        video = VideoFileClip(v_path)
        
        if not subtitle_text or subtitle_text.strip() == "":
            print("⚠️ 적용할 자막 텍스트가 없어 배경 영상만 그대로 저장합니다.")
            video.write_videofile(o_path, codec="libx264", audio_codec="aac")
            return True

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
        
        final_video.write_videofile(
            o_path, 
            fps=30, 
            codec="libx264", 
            audio_codec="aac", 
            preset="ultrafast",
            threads=4,
            logger=None
        )
        
        video.close()
        final_video.close()
        print("✅ 최종 자막 합성 및 렌더링 완료")
        return True

    except Exception as e:
        print(f"❌ 자막 합성 중 오류 발생: {e}")
        return False