from flask import flash
import os
import uuid
from werkzeug.exceptions import BadRequest, UnsupportedMediaType

GPX_FILE = 'gpx'
UPLOAD_FOLDER = 'gpx_upload'
SIZE_MAX = 512

def get_unique_filename():
    return str(uuid.uuid4()) + '.' + GPX_FILE

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() == GPX_FILE

def upload_gpx_file(files):
    if 'file' not in files or files['file'].filename == '':
        raise BadRequest(description="A GPX file is required in the payload.")
    
    file = files['file']
    
    if not allowed_file(file.filename):
        raise UnsupportedMediaType(description="Only GPX files are allowed.")

    file.seek(0,2)
    file_size = file.tell()
    if file_size / 1024 > SIZE_MAX:
        raise BadRequest(description="GPX file should be less than 512ko.")

    file.seek(0,0)
    if file:
        filename = get_unique_filename()
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)

        return file_path
    
    return None
    

def delete_gpx_file(filename):
    if os.path.exists(filename) and allowed_file(filename):
        os.remove(filename)