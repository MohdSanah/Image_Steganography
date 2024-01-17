from flask import Flask, render_template, request, redirect, url_for
from flask import send_file
from stegano import lsb
from io import BytesIO
import base64
from filters import bytes_to_hex

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/encode', methods=['POST'])
def encode():
    if 'image' not in request.files:
        return redirect(url_for('index'))

    image = request.files['image']
    secret_text = request.form['secret_text']

    
    image_binary = image.read()

    
    secret_image = lsb.hide(BytesIO(image_binary), secret_text)

    
    secret_image_io = BytesIO()
    secret_image.save(secret_image_io, format='PNG')
    secret_image_io.seek(0)

    
    secret_image_base64 = base64.b64encode(secret_image_io.read()).decode('utf-8')

    return render_template('result.html', result=secret_image_base64)

@app.route('/download', methods=['POST'])
def download():
    file_name = request.form['file_name']
    image_data = base64.b64decode(request.form['image_data'])

    with open(f'{file_name}.png', 'wb') as f:
        f.write(image_data)

    return send_file(f'{file_name}.png', as_attachment=True)

@app.route('/extract_text', methods=['GET', 'POST'])
def extract_text():
    if request.method == 'POST':
        if 'image' not in request.files:
            return redirect(url_for('extract_text'))

        image = request.files['image']

        # Read the binary image data
        image_data = image.read()

        try:
            # Attempt to reveal text from the image
            revealed_text_bytes = lsb.reveal(image_data)
        except UnicodeDecodeError:
            # Handle UnicodeDecodeError by sending the binary data directly
            return send_file(
                BytesIO(image_data),
                as_attachment=True,
                download_name='extracted_text.bin',
                mimetype='application/octet-stream',
                conditional=True
            )

        # Send the revealed text as a file with appropriate parameters
        return send_file(
            BytesIO(revealed_text_bytes),
            as_attachment=True,
            download_name='extracted_text.bin',
            mimetype='application/octet-stream',
            conditional=True
        )

    return render_template('extract_text.html')



app.jinja_env.filters['bytes_to_hex'] = bytes_to_hex

if __name__ == '__main__':
    app.run(debug=True)
