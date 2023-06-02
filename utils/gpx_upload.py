from flask import flash
import os
import uuid

GPX_FILE = 'gpx'
UPLOAD_FOLDER = 'gpx_upload'

def get_unique_filename():
    return str(uuid.uuid4()) + '.' + GPX_FILE

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() == GPX_FILE

def upload_gpx_file(files):
    if 'file' not in files:
        flash('No file part')

    file = files['file']

    if file.filename == '':
        flash('No selected file')

    if file and allowed_file(file.filename):
        filename = get_unique_filename()
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)

        return file_path

def delete_gpx_file(filename):
    if os.path.exists(filename) and allowed_file(filename):
        os.remove(filename)