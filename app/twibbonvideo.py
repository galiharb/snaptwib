from flask import render_template, request, redirect, url_for, session, make_response, Response
from app import app, db
from app.models import User, Twibbon
from datetime import datetime
from PIL import Image
import hashlib, os, imghdr ,requests ,subprocess, datetime
import moviepy.config as config
from multiprocessing import cpu_count
# from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip
from moviepy.editor import *
from werkzeug.utils import secure_filename
from ffprobe import FFProbe

#env grep
upload_video=os.environ.get('UPLOAD_FOLDER')
temp_video=os.environ.get('TEMP_FOLDER')
hasil_video=os.environ.get('HASIL_VIDEO')
folder_twibbon=os.environ.get('PATH_TWIBBON')
url_download=os.environ.get('URL_PATH_VIDEO')

# use Multi-threading for CPU cores
config.change_settings({
    "threads": cpu_count(),
    "max_threads": cpu_count(),
    "prefetch_threads": cpu_count()
})

# use GPU acceleration
config.change_settings({"use_gpu": True})

def resize_video(input_path, output_path, width, height):
    clip = VideoFileClip(input_path)
    print(input_path)
    resized_clip = clip.resize(newsize=(width, height))
    resized_clip.write_videofile(output_path)


def create_twibbon_video(background_path, overlay_path, output_path):
    background_clip = VideoFileClip(background_path)
    overlay_clip = ImageClip(overlay_path)
    overlay_clip = overlay_clip.set_duration(background_clip.duration)

    x_pos = (background_clip.w - overlay_clip.w) / 2
    y_pos = (background_clip.h - overlay_clip.h) / 2
    overlay_clip = overlay_clip.set_position((x_pos, y_pos))

    final_clip = CompositeVideoClip([background_clip, overlay_clip])
    final_clip.write_videofile(output_path)

@app.route('/<id_twibbon>/twibbonvideo', methods=['GET','POST'])
def twibbonvideo(id_twibbon):
    twibbons = Twibbon.query.with_entities(Twibbon.id_twibbon).all()
    if (id_twibbon,) not in twibbons:
        return render_template('error.html', message='Halaman tidak dapat ditemukan')

    if request.method == 'POST':
        # Get the uploaded file
        video_file = request.files['file']
        filename = secure_filename(video_file.filename)

        if filename.endswith('.mp4') or filename.endswith('.MOV'):
            output = subprocess.check_output(['ffprobe', '-i', '-', '-show_entries', 'format=duration', '-v', 'quiet', '-of', 'csv=p=0'], stdin=video_file.stream, stderr=subprocess.STDOUT)
            duration = float(output)
            max_duration = 15

            if duration > max_duration:
                error_limit = 'Maaf, durasi video maksimal 15 detik'
                twibbons = Twibbon.query.filter_by(id_twibbon=id_twibbon).first()
                return render_template('twibbonvideo.html',title='Snaptwib.com | Upload Video', error_limit=error_limit,twibbons=twibbons)

            if filename.endswith('.mp4'):
                timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
                new_filename = timestamp + '_' + filename 
                video_file.seek(0)
                video_file.save(upload_video+'/'+new_filename)
            elif filename.endswith('.MOV'):
                video_file.seek(0)
                video_file.save(upload_video+'/'+filename)
                input_file = VideoFileClip(upload_video+'/'+filename)
                filename_ganti = filename.split('.MOV')
                ganti = filename[0]+'.mp4'
                timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
                new_filename = timestamp + '_' + ganti
                output_file = input_file.write_videofile(upload_video+'/'+new_filename, codec='libx264', audio_codec='aac', bitrate="5000k", fps=input_file.fps, audio_bitrate='256k')
                os.system('rm -rf '+upload_video+'/'+filename)


            twibbons = Twibbon.query.filter_by(id_twibbon=id_twibbon).first()
            
            resize_video(upload_video+'/'+new_filename, temp_video+'/'+'temp_'+new_filename, 1080, 1920)
            create_twibbon_video(temp_video+'/'+'temp_'+new_filename, folder_twibbon+'/'+twibbons.username+'/'+id_twibbon+'.png', hasil_video+'/'+new_filename)
            os.system('rm -rf '+upload_video+'/'+new_filename)
            os.system('rm -rf '+temp_video+'/'+'temp_'+new_filename)

            success = 'twibbon video selesai :)'
            download = url_download+'/'+new_filename

            return render_template('twibbonvideo.html',title='Snaptwib.com | Upload Video',twibbons=twibbons, success=success ,download=download)
        else:
            twibbons = Twibbon.query.filter_by(id_twibbon=id_twibbon).first()
            return render_template('twibbonvideo.html',title='Snaptwib.com | Upload Video',error="Format Video tidak support",twibbons=twibbons)
    
    twibbons = Twibbon.query.filter_by(id_twibbon=id_twibbon).first()
    return render_template('twibbonvideo.html',title='Snaptwib.com | '+twibbons.title_twibbon,twibbons=twibbons)