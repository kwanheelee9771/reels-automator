from moviepy.editor import VideoFileClip, AudioFileClip
import moviepy.video.fx.all as vfx

def merge_video_audio():
    print("영상과 AI 음성 합성 및 루프(Loop) 처리 시작...")
    
    video = VideoFileClip("final_reels.mp4")
    audio = AudioFileClip("voice.mp3")
    
    looping_video = video.fx(vfx.loop, duration=audio.duration)
    final_video = looping_video.set_audio(audio)
    
    output_name = "tiktok_ready.mp4"
    # 👈 아래 줄 끝에 인스타그램 필수 규격 파라미터 추가
    final_video.write_videofile(output_name, codec="libx264", audio_codec="aac", ffmpeg_params=["-pix_fmt", "yuv420p"])
    print(f"합성 완료! {output_name} 파일을 확인하세요.")

if __name__ == "__main__":
    merge_video_audio()