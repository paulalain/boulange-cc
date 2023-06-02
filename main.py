from flask import Flask, request
from api.pois import get_pois, check_type
from utils.gpx_upload import upload_gpx_file, delete_gpx_file
from werkzeug.exceptions import HTTPException

app = Flask(__name__)
app.secret_key = "super secret key"

@app.route('/<poi_type>', methods = ['POST'])
def poi_type(poi_type):
    file_path = upload_gpx_file(request.files)

    if check_type(poi_type):
        return get_pois(poi_type, file_path)
    
    # Remove file
    delete_gpx_file(file_path)

    return None

@app.route('/')
def index():
    return None
