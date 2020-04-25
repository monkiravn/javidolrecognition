#Usage: python app.py
import os
 
from flask import Flask, render_template, request
from werkzeug import secure_filename
from keras.preprocessing.image import  load_img, img_to_array,array_to_img
from keras.models import  load_model
import pickle
from mtcnn import MTCNN
import numpy as np
import uuid
import base64

detector = MTCNN()

MODEL_FILE = "models/finetuningvgg16.hdf5"

pkl_filename = 'data_y_enc.pkl'
with open(pkl_filename, 'rb') as file:
    output_enc = pickle.load(file)

model = load_model(MODEL_FILE, compile=False)
print('Model loaded.')

#model.load_weights(model_weights_path)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = set(['jpg', 'jpeg'])

def get_as_base64(url):
    return base64.b64encode(request.get(url).content)

def preprocess(img):
    results = detector.detect_faces(img)
    x1, y1, width, height = results[0]['box']
    x1, y1 = abs(x1), abs(y1)
    x2, y2 = x1 + width, y1 + height
    face = img[y1:y2, x1:x2]
    img = array_to_img(face)
    img = img.resize((224, 224))
    img = np.asarray(img)
    return img


def predict(file):
    x = load_img(file)
    x = img_to_array(x)
    x = preprocess(x)
    x = np.expand_dims(x, axis=0)
    pre_name = model.predict(x)
    pre_name = output_enc.inverse_transform([np.argmax(pre_name)])
    return pre_name[0]

def my_random_string(string_length=10):
    """Returns a random string of length string_length."""
    random = str(uuid.uuid4()) # Convert UUID format to a Python string.
    random = random.upper() # Make all characters uppercase.
    random = random.replace("-","") # Remove the UUID '-'.
    return random[0:string_length] # Return the random string.

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route("/")
def template_test():
    return render_template('template.html', label='', imagesource='../uploads/template.jpg')

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        import time
        start_time = time.time()
        file = request.files['file']

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)

            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            result = predict(file_path)
            label = result
            print(result)
            print(file_path)
            filename = my_random_string(6) + filename

            os.rename(file_path, os.path.join(app.config['UPLOAD_FOLDER'], filename))
            print("--- %s seconds ---" % str (time.time() - start_time))
            return render_template('template.html', label=label, imagesource='../uploads/' + filename)

from flask import send_from_directory

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)

from werkzeug import SharedDataMiddleware
app.add_url_rule('/uploads/<filename>', 'uploaded_file',
                 build_only=True)
app.wsgi_app = SharedDataMiddleware(app.wsgi_app, {
    '/uploads':  app.config['UPLOAD_FOLDER']
})

if __name__ == "__main__":
    app.debug=False
    app.run(threaded=False)