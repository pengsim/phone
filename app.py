from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import pymysql
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)

# Config
app.config['MYSQL_HOST'] = 'shop-ratanayorm787-82b5.g.aivencloud.com'
app.config['MYSQL_PORT'] = 12695
app.config['MYSQL_USER'] = 'avnadmin'
app.config['MYSQL_PASSWORD'] = 'AVNS_rdTIwRKaGJtBXhX9MSL'
app.config['MYSQL_DB'] = 'defaultdb'
app.config['UPLOAD_FOLDER'] = 'uploads'

# Create uploads folder if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# DB connection
def get_database():
    return pymysql.connect(
        host=app.config['MYSQL_HOST'],
        port=app.config['MYSQL_PORT'],
        user=app.config['MYSQL_USER'],
        password=app.config['MYSQL_PASSWORD'],
        database=app.config['MYSQL_DB'],
        ssl={'ssl-mode': 'REQUIRED'},
        cursorclass=pymysql.cursors.DictCursor
    )

# Serve uploaded images
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Get all phones
@app.route('/phones', methods=['GET'])
def get_phones():
    conn = get_database()
    cur = conn.cursor()
    cur.execute("SELECT * FROM phone")
    rows = cur.fetchall()
    conn.close()
    # rows are dicts due to DictCursor
    return jsonify(rows)

# Add phone with image
@app.route('/add', methods=['POST'])
def add_phone():
    model = request.form.get('model')
    color = request.form.get('color')
    price = request.form.get('price')
    detail = request.form.get('detail')
    image_file = request.files.get('image')

    if image_file and image_file.filename != '':
        filename = secure_filename(image_file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        image_file.save(filepath)
    else:
        filename = ''

    conn = get_database()
    cur = conn.cursor()
    cur.execute(
        'INSERT INTO phone (model, color, price, image, detail) VALUES (%s, %s, %s, %s, %s)',
        (model, color, price, filename, detail)
    )
    conn.commit()
    conn.close()

    return jsonify({'message': 'Phone added successfully'})

# Delete phone
@app.route('/delete/<int:id>', methods=['DELETE'])
def delete_phone(id):
    conn = get_database()
    cur = conn.cursor()
    cur.execute("DELETE FROM phone WHERE phone_id=%s", (id,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Deleted successfully'})

# Edit phone
@app.route('/edit/<int:id>', methods=['POST'])
def edit_phone(id):
    data = request.form
    model = data.get('model')
    color = data.get('color')
    price = data.get('price')
    detail = data.get('detail')
    image_file = request.files.get('image')

    conn = get_database()
    cur = conn.cursor()

    if image_file and image_file.filename != '':
        filename = secure_filename(image_file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        image_file.save(filepath)
        cur.execute(
            'UPDATE phone SET model=%s, color=%s, price=%s, image=%s, detail=%s WHERE phone_id=%s',
            (model, color, price, filename, detail, id)
        )
    else:
        cur.execute(
            'UPDATE phone SET model=%s, color=%s, price=%s, detail=%s WHERE phone_id=%s',
            (model, color, price, detail, id)
        )

    conn.commit()
    conn.close()

    return jsonify({'message': 'Updated successfully'})

if __name__ == '__main__':
    app.run(host='0.0.0.0' port=5000)
