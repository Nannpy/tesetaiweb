import os
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash
from ultralytics import YOLO
from datetime import datetime

app = Flask(__name__)
app.secret_key = "supersecret"

# โฟลเดอร์สำหรับเก็บภาพ
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'static/output'

# โหลดโมเดล YOLO (เปลี่ยน path ตามโมเดลของคุณ)
model = YOLO("yolov8n.pt")

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # ตรวจสอบไฟล์
        if 'image' not in request.files:
            flash('ไม่พบไฟล์ภาพ')
            return redirect(request.url)

        file = request.files['image']
        if file.filename == '':
            flash('ยังไม่ได้เลือกไฟล์')
            return redirect(request.url)

        if file:
            # ตั้งชื่อไฟล์ input แบบไม่ซ้ำ
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            input_filename = f"{timestamp}_{file.filename}"
            upload_path = os.path.join(app.config['UPLOAD_FOLDER'], input_filename)
            file.save(upload_path)

            # วิเคราะห์ภาพด้วย YOLO
            results = model(upload_path)

            # ตั้งชื่อ output แบบไม่ซ้ำ
            output_filename = f"output_{timestamp}.jpg"
            output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)

            # save output
            results[0].save(filename=output_path)

            return render_template(
                'index.html',
                uploaded_image=url_for('uploaded_file', filename=input_filename),
                detected_image=url_for('output_file', filename=output_filename)
            )

    return render_template('index.html')

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/static/output/<filename>')
def output_file(filename):
    return send_from_directory(app.config['OUTPUT_FOLDER'], filename)

if __name__ == '__main__':
    os.makedirs('uploads', exist_ok=True)
    os.makedirs('static/output', exist_ok=True)
    app.run(host='0.0.0.0', port=5003, debug=True)
