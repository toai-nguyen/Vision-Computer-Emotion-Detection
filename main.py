from flask import Flask, flash, request, redirect, send_from_directory, url_for, render_template, Response
from models.video import VideoCamera
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['TEMPLATE_FOLDER'] = 'templates/'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB file size limit
camera = VideoCamera()

def gen_frames():
    while True:
        frame = camera.get_frame()
        if frame is None:
            break
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'fileUpload' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['fileUpload']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file:
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            # Process the uploaded file using the VideoCamera class
            processed_file_path = camera.process_file(file_path)
           
            if processed_file_path is not None:
                if file_path.endswith('.mp4') or file_path.endswith('.avi'):
                    return render_template('index.html', processed_video=processed_file_path)
                else:
                    return render_template('index.html', processed_image=processed_file_path)
            else:
                flash('Error processing the file')
                return redirect(request.url)
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/download/<filename>')
def download_video(filename):
    return send_from_directory(app.config['TEMPLATE_FOLDER'], filename, as_attachment=True)

if __name__ == "__main__":
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    if not os.path.exists(app.config['TEMPLATE_FOLDER']):
        os.makedirs(app.config['TEMPLATE_FOLDER'])
    app.run(debug=True)
