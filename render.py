# import PIL.Image
# if not hasattr(PIL.Image, 'ANTIALIAS'):
#     PIL.Image.ANTIALIAS = PIL.Image.Resampling.LANCZOS

# from moviepy.editor import VideoFileClip
# import os

# def make_reels_video():
#     print("영상 렌더링 시작...")
    
#     # 1. 원본 영상 불러오기
#     clip = VideoFileClip("background.mp4")
    
#     # 2. 릴스 비율(9:16) 계산 및 가운데 크롭(자르기)
#     # 인스타그램 릴스 해상도: 1080 x 1920
#     target_ratio = 9 / 16
#     current_ratio = clip.w / clip.h
    
#     if current_ratio > target_ratio:
#         # 가로가 더 긴 경우 (좌우를 자름)
#         new_width = int(clip.h * target_ratio)
#         x_center = clip.w / 2
#         clip = clip.crop(x1=x_center - new_width/2, y1=0, x2=x_center + new_width/2, y2=clip.h)
#     else:
#         # 세로가 더 긴 경우 (위아래를 자름)
#         new_height = int(clip.w / target_ratio)
#         y_center = clip.h / 2
#         clip = clip.crop(x1=0, y1=y_center - new_height/2, x2=clip.w, y2=y_center + new_height/2)
    
#     # 3. 1080x1920 사이즈로 최종 리사이즈
#     final_clip = clip.resize((1080, 1920))
    
#     # 4. 결과물 저장 (렌더링)
#     final_clip.write_videofile("final_reels.mp4", codec="libx264", audio_codec="aac")
#     print("렌더링 완료! final_reels.mp4 파일을 확인하세요.")

# if __name__ == "__main__":
#     make_reels_video()
import os
import glob

# [핵심 방어 코드] MoviePy와 최신 Pillow 버전 충돌 강제 해결
from PIL import Image
if not hasattr(Image, 'ANTIALIAS'):
    Image.ANTIALIAS = Image.LANCZOS

from moviepy.editor import VideoFileClip, AudioFileClip, ColorClip, CompositeVideoClip
import moviepy.video.fx.all as vfx

def process_background_for_copyright(video_path, target_duration):
    """인스타그램 저작권 필터링 우회를 위한 시각적 변조 수행"""
    clip = VideoFileClip(video_path)
    
    w, h = clip.size
    crop_x = int(w * 0.03)
    crop_y = int(h * 0.03)
    clip = clip.crop(x1=crop_x, y1=crop_y, x2=w-crop_x, y2=h-crop_y)
    clip = clip.resize((1080, 1920))
    
    clip = clip.fx(vfx.speedx, 1.02)
    
    if clip.duration < target_duration:
        clip = clip.fx(vfx.loop, duration=target_duration)
    else:
        clip = clip.subclip(0, target_duration)
    
    dark_overlay = ColorClip(size=(1080, 1920), color=(0,0,0)).set_opacity(0.15).set_duration(target_duration)
    return CompositeVideoClip([clip, dark_overlay])

def make_reels_video(video_path="background_video.mp4", audio_path="tts_audio.mp3", output_path="rendered_video.mp4"):
    """최종 영상과 오디오 합성 (오디오 파일 자동 탐색 기능 포함)"""
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        v_path = os.path.join(base_dir, video_path)
        a_path = os.path.join(base_dir, audio_path)
        o_path = os.path.join(base_dir, output_path)

        if not os.path.exists(a_path):
            mp3_files = glob.glob(os.path.join(base_dir, "*.mp3"))
            if mp3_files:
                a_path = mp3_files[0]
            else:
                print("❌ 폴더 내에 오디오(.mp3) 파일이 존재하지 않습니다.")
                return False

        if not os.path.exists(v_path):
            print(f"❌ 배경 영상이 존재하지 않습니다: {v_path}")
            return False

        print(f"🎬 렌더링 시작... (영상: {os.path.basename(v_path)}, 오디오: {os.path.basename(a_path)})")
        audio = AudioFileClip(a_path)
        final_visuals = process_background_for_copyright(v_path, audio.duration)
        final_video = final_visuals.set_audio(audio)
        
        final_video.write_videofile(
            o_path, 
            fps=30, 
            codec="libx264", 
            audio_codec="aac", 
            preset="ultrafast", 
            threads=4,
            logger=None
        )
        
        audio.close()
        final_video.close()
        print("✅ 1차 렌더링 완료")
        return True
        
    except Exception as e:
        print(f"❌ 렌더링 중 오류 발생: {e}")
        return False