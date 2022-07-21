from app import app
from flask import request, jsonify, render_template
from werkzeug.utils import secure_filename

import os
import datetime
import pymediainfo

from .db import db_init, db, ma_init
from .models import Video, VideoSchema


# initalize database and schema
db_init(app)
ma_init(app)


@app.errorhandler(413)
def app_handle_413(e):
    resp = jsonify({'message': 'file size larger than 1 gb'})
    resp.status_code = 413
    return resp


def allowed_file(filename):
    ftype = filename.rsplit('.', 1)[1].lower()
    return '.' in filename and ftype in app.config['ALLOWED_EXTENSIONS']


def allowed_length(filename):
    # using pymediainfo ( for max duration;
    # check should be kept in client side rather than serverside)
    file = pymediainfo.MediaInfo.parse(filename)
    duration = file.tracks[0].duration/60000
    return duration


def return_schema(videos):
    video_schema = VideoSchema(many=True)
    return video_schema.dump(videos)


def length_check(char, len):
    if float(len) < 6.3:
        charge = 12.5 + char
    else:
        charge = char+20
    return charge


@app.route('/')
def main():
    return render_template('home.html')


# api endpoint to upload and validate and store file in database
@app.route('/upload', methods=['POST'])
def upload_video():
    if 'files[]' not in request.files:
        resp = jsonify({'message': 'No file part in the request'})
        resp.status_code = 400
        return resp
    files = request.files.getlist('files[]')
    errors = {}
    success = False

    for file in files:
        if file and allowed_file(file.filename):
            # to verify if the input file is same
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            duration = allowed_length(file_path)
            if duration > app.config['ALLOWED_DURATION']:
                errors['message'] = 'File duration greater than 10 minutes'
                os.remove(file_path)
            else:
                file_size = os.path.getsize(file_path)/(1024*1024.0)
                vid = Video(
                    file_name=filename,
                    path=file_path,
                    vid_type=file.filename.rsplit('.', 1)[1].lower(),
                    upload_date=datetime.datetime.utcnow(),
                    vid_size=file_size,
                    vid_duration=duration,
                )
                try:
                    db.session.add(vid)
                    db.session.commit()
                    success = True
                except Exception:
                    errors["message"] = f'{file.filename} already exists'
        else:
            errors['message'] = 'File type is not allowed'

        if success:
            resp = jsonify(
                {"message": f'{file.filename} successfylly uploaded'})
            resp.status_code = 201
            return resp
        else:
            resp = jsonify(errors)
            resp.status_code = 500
            return resp


# I set up simple query based on name or max video
# duration or maximum size (you can perform only one type of query )
@app.route('/files', methods=['GET'])
def show_all_files():
    args = request.args
    if args == {}:
        videos = Video.query.all()
    elif 'name' in args:
        videos = Video.query.filter(
            Video.file_name.contains(args['name'])).all()
    elif 'max_duration' in args:
        videos = Video.query.filter(
            Video.vid_duration < int(args['max_duration'])).all()
    elif 'max_size' in args:
        videos = Video.query.filter(
            Video.vid_size < int(args['max_size'])).all()

    output = return_schema(videos)
    if output == []:
        return jsonify({'message': 'no vidos matching found'})
    else:
        return jsonify({'Videos': output})


@app.route('/charge', methods=['POST'])
def payment():
    vid_size = request.form['size']
    vid_length = request.form['length']
    # I didn't add length, size and type limit validation here rather just
    # calculated the charge
    try:
        if int(vid_size) < 500:
            charge = length_check(5, vid_length)
        else:
            charge = length_check(12.5, vid_length)

        return jsonify({"charge": charge})
    except Exception:
        return jsonify({'message': 'form input field data error'})
