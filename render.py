import PIL.Image
if not hasattr(PIL.Image, 'ANTIALIAS'):
    PIL.Image.ANTIALIAS = PIL.Image.Resampling.LANCZOS

from moviepy.editor import VideoFileClip
import os

def make_reels_video():
    print("영상 렌더링 시작...")
    
    # 1. 원본 영상 불러오기
    clip = VideoFileClip("background.mp4")
    
    # 2. 릴스 비율(9:16) 계산 및 가운데 크롭(자르기)
    # 인스타그램 릴스 해상도: 1080 x 1920
    target_ratio = 9 / 16
    current_ratio = clip.w / clip.h
    
    if current_ratio > target_ratio:
        # 가로가 더 긴 경우 (좌우를 자름)
        new_width = int(clip.h * target_ratio)
        x_center = clip.w / 2
        clip = clip.crop(x1=x_center - new_width/2, y1=0, x2=x_center + new_width/2, y2=clip.h)
    else:
        # 세로가 더 긴 경우 (위아래를 자름)
        new_height = int(clip.w / target_ratio)
        y_center = clip.h / 2
        clip = clip.crop(x1=0, y1=y_center - new_height/2, x2=clip.w, y2=y_center + new_height/2)
    
    # 3. 1080x1920 사이즈로 최종 리사이즈
    final_clip = clip.resize((1080, 1920))
    
    # 4. 결과물 저장 (렌더링)
    final_clip.write_videofile("final_reels.mp4", codec="libx264", audio_codec="aac")
    print("렌더링 완료! final_reels.mp4 파일을 확인하세요.")

if __name__ == "__main__":
    make_reels_video()