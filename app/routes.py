from flask import render_template, request, redirect, url_for, session, make_response, Response, jsonify
from flask_caching import Cache
from app import app, db
from app.models import User, Twibbon
from datetime import datetime
from PIL import Image
import hashlib, os, imghdr ,requests

def randomfilename():
    name = str(datetime.today().isoformat())
    name = hashlib.md5((name.encode()))
    name = name.hexdigest()
    return str(name)

cache = Cache(app, config={'CACHE_TYPE': 'simple'})

@app.route('/')
@cache.cached(timeout=300)
def index():
    twibbons = Twibbon.query.order_by(Twibbon.tanggal_twibbon.desc()).limit(4).all()
    return render_template('index.html', title='Snaptwib | Snap Your Twibbon with Photo or Video', ogtwb="https://snaptwib.com/static/img/logo.png" ,twibbons=twibbons ,url=os.environ.get('URL'))

@app.route('/twibbons', methods=['GET'])
def get_twibbons():
    page = request.args.get('page', 1, type=int)
    twibbons = Twibbon.query.order_by(Twibbon.tanggal_twibbon.desc()).paginate(page=page, per_page=4)
    return jsonify(twibbons=[twibbon.to_dict() for twibbon in twibbons.items], has_next=twibbons.has_next)

@app.route('/<id_twibbon>')
def sharelink(id_twibbon):
    twibbons = Twibbon.query.with_entities(Twibbon.id_twibbon).all()
    if (id_twibbon,) not in twibbons:
        return render_template('error.html', message='Halaman tidak dapat ditemukan')
    else:
        twibbons = Twibbon.query.filter_by(id_twibbon=id_twibbon).first()
        return render_template('sharelink.html',title='Snaptwib.com | '+twibbons.title_twibbon,ogtwb=twibbons.path_twibbon,twibbons=twibbons,url=os.environ.get('URL'))

@app.route('/<id_twibbon>/twibbonfoto')
def twibbonfoto(id_twibbon):
    twibbons = Twibbon.query.with_entities(Twibbon.id_twibbon).all()
    if (id_twibbon,) not in twibbons:
        return render_template('error.html', message='Halaman tidak dapat ditemukan')
    else:
        twibbons = Twibbon.query.filter_by(id_twibbon=id_twibbon).first()
        user_agent = request.user_agent.string
        print (user_agent)
        if 'iPhone' in user_agent and 'CriOS' in user_agent:
            return render_template('twibbonfoto.html',title='Snaptwib.com',pesan="Mohon maaf, untuk user iphone silahkan menggunakan Safari")
        else:    
            return render_template('twibbonfoto.html',title='Snaptwib.com | '+twibbons.title_twibbon,twibbons=twibbons)

@app.route('/explore')
def explore():
    return render_template('explore.html', title='Explore')

@app.route('/about')
def about():
    return render_template('about.html', title='About')

@app.route('/kreator')
def kreator():
    if 'username' not in session:
        return render_template('kreator.html', title='Log in | Kreator')
    else:
        username = format(session['username'])
        return redirect(url_for('kreator_user', username=username))

@app.route('/kreator/<username>')
def kreator_user(username):
    if 'username' not in session:
        twibbon = User.query.filter_by(username=username).first()
        if twibbon:
            twibbons = Twibbon.query.filter_by(username=username).order_by(Twibbon.tanggal_twibbon.desc()).limit(10).all()
            if not twibbons:
                return render_template('profile.html',username=username, no_twibbons="Tidak ada twibbon pada user ini")
            else:
                return render_template('profile.html',username=username, twibbons=twibbons, url=os.environ.get('URL'))
        else:
            return render_template('error.html', message='User tidak dapat ditemukan')
    
    if session['username'] != username:
        twibbon = User.query.filter_by(username=username).first()
        if twibbon:
            twibbons = Twibbon.query.filter_by(username=username).order_by(Twibbon.tanggal_twibbon.desc()).limit(10).all()
            if not twibbons:
                return render_template('profile.html',username=username, no_twibbons="Tidak ada twibbon pada user ini")
            else:
                return render_template('profile.html',username=username, twibbons=twibbons, url=os.environ.get('URL'))

    # print(format(session['username']))

    # username = format(session['username'])

    if session['username'] == username:
        twibbons = Twibbon.query.filter_by(username=username).order_by(Twibbon.tanggal_twibbon.desc()).limit(10).all()
        upload_button = True
        if not twibbons:
            return render_template('profile.html',username=username,upload_button=upload_button,no_twibbons="Tidak ada twibbon pada user ini")
        else:
           return render_template('profile.html',username=username, upload_button=upload_button, twibbons=twibbons)
        

    return render_template('profile.html',username=username)
        

@app.route('/kreator/<username>/upload', methods=['GET','POST'])
def kreator_user_upload(username):
    if 'username' not in session:
        return redirect(url_for('kreator'))
    
    username = format(session['username'])

    if session['username'] == username:
        if request.method == 'GET':
            return render_template('adminupload.html',username=username)
        
        if request.method == 'POST':
            if 'file' not in request.files:
                return render_template('adminupload.html',username=username)
            
            file = request.files['file']
            # file_type = imghdr.what(file)

            if file and file.filename.endswith('.png'):
                folder = os.environ.get('PATH_TWIBBON')+'/'+username+'/'
                id_twibbon = randomfilename()
                new_filename = id_twibbon+".png"
                file.save(os.path.join(folder, new_filename))

                with Image.open(os.path.join(folder, new_filename)) as img:
                    width, height = img.size
                    if width == 1080 and height == 1920:
                        title_twibbon = request.form['judul']
                        path_twibbon = os.environ.get('URL_PATH_TWIBBON')+'/'+username+'/'+new_filename
                        tanggal_twibbon = str(datetime.today().isoformat())

                        new_twibbon = Twibbon(username=username,id_twibbon=id_twibbon,title_twibbon=title_twibbon,path_twibbon=path_twibbon,tanggal_twibbon=tanggal_twibbon)
                        db.session.add(new_twibbon)
                        db.session.commit()
                    
                        return render_template('adminupload.html',username=username,pngsuccess='Twibbon Berhasil Terupload !!!')
                    else:
                        os.system('rm -rf'+os.environ.get('PATH_TWIBBON')+'/'+new_filename)
                        return render_template('adminupload.html',username=username,pngwarning='Ukuran PNG Harus 1080 x 1920 pixel')
            else:
                pngwarning = "harus PNG lah woy !!!"
                return render_template('adminupload.html',username=username,pngwarning=pngwarning)
           
    return redirect(url_for('kreator'))

@app.route('/twb/<id_twibbon>.png')
def imagetwibbon(id_twibbon):
    twibbons = Twibbon.query.with_entities(Twibbon.id_twibbon).all()
    if (id_twibbon,) not in twibbons:
        return render_template('error.html', message='Halaman tidak dapat ditemukan')
    else:
        twibbons = Twibbon.query.filter_by(id_twibbon=id_twibbon).first()
        username = twibbons.username
        image = twibbons.id_twibbon

        image_url = os.environ.get('URL_PATH_TWIBBON')+'/'+username+'/'+image+'.png'
        image_response = requests.get(image_url)

        headers = {
            'Content-Type': 'image/png'
        }
        return Response(image_response.content, headers=headers)