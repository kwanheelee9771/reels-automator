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

# [강력 방어] 모든 Pillow(이미지 라이브러리) 버전 호환성 강제 확보
from PIL import Image
try:
    resample_method = Image.Resampling.LANCZOS
except AttributeError:
    resample_method = getattr(Image, 'LANCZOS', 1)
if not hasattr(Image, 'ANTIALIAS'):
    Image.ANTIALIAS = resample_method

from moviepy.editor import VideoFileClip, ColorClip, CompositeVideoClip
import moviepy.video.fx.all as vfx

def process_background_for_copyright(video_path):
    """인스타그램 저작권 필터링 우회를 위한 시각적 4중 변조 수행"""
    clip = VideoFileClip(video_path)
    
    # 1. 크롭 (3%) & 2. 리사이즈
    w, h = clip.size
    crop_x = int(w * 0.03)
    crop_y = int(h * 0.03)
    clip = clip.crop(x1=crop_x, y1=crop_y, x2=w-crop_x, y2=h-crop_y)
    clip = clip.resize((1080, 1920))
    
    # 3. 배속 (1.02배)
    clip = clip.fx(vfx.speedx, 1.02)
    
    # 4. 블랙 오버레이 (15%)
    dark_overlay = ColorClip(size=(1080, 1920), color=(0,0,0)).set_opacity(0.15).set_duration(clip.duration)
    return CompositeVideoClip([clip, dark_overlay])

# audio_path 파라미터는 4단계에서 사용하므로 무시하고 시각 효과만 렌더링
def make_reels_video(video_path="background_video.mp4", audio_path=None, output_path="final_reels.mp4"):
    """최종 시각 영상 렌더링 (오디오는 4단계가 전담하므로 제외)"""
    try:
        # 깃허브 서버 어디서 실행되든 최상단 루트에 파일을 보장하는 절대 경로 설정
        v_path = os.path.abspath(video_path)
        o_path = os.path.abspath(output_path)

        if not os.path.exists(v_path):
            print(f"❌ 배경 영상이 존재하지 않습니다: {v_path}")
            return False

        print(f"🎬 저작권 회피 렌더링 시작... (출력 파일: {o_path})")
        final_visuals = process_background_for_copyright(v_path)
        
        # 깃허브 2코어 서버 맞춤형 렌더링 세팅 (오디오 제외)
        final_visuals.write_videofile(
            o_path, 
            fps=30, 
            codec="libx264", 
            audio=False,         # 4단계와의 충돌을 막기 위해 음성 병합 안 함
            preset="ultrafast", 
            threads=2,           # 메모리 다운(OOM) 방지
            logger=None
        )
        
        final_visuals.close()
        print("✅ 3단계: 시각적 필터 렌더링 완료")
        return True
        
    except Exception as e:
        print(f"❌ 3단계 렌더링 중 오류 발생: {e}")
        return False