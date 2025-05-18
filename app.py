from flask import Flask, request, jsonify
from flask_cors import CORS
import pymysql
import cloudinary
import cloudinary.uploader

app = Flask(__name__)
CORS(app)

# ✅ Cloudinary config ត្រូវតែដាក់ជា api_key, api_secret បែបនេះ
cloudinary.config(
    cloud_name='da48norud',
    api_key='471772216243935',
    api_secret='Q0pjsE2NHowI3ycLo8pdWkpT1GA'  # 🛑 ដាច់ api_secret ត្រឹមនេះ
)

# MySQL config
app.config['MYSQL_HOST'] = 'shop-ratanayorm787-82b5.g.aivencloud.com'
app.config['MYSQL_PORT'] = 12695
app.config['MYSQL_USER'] = 'avnadmin'
app.config['MYSQL_PASSWORD'] = 'AVNS_rdTIwRKaGJtBXhX9MSL'
app.config['MYSQL_DB'] = 'defaultdb'

# Function ចាប់ភ្ជាប់ database
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

# ✅ Route ទាញទិន្នន័យទូរស័ព្ទ
@app.route('/phones', methods=['GET'])
def get_phones():
    conn = get_database()
    cur = conn.cursor()
    cur.execute("SELECT * FROM phone")
    rows = cur.fetchall()
    conn.close()
    return jsonify(rows)

# ✅ Route បន្ថែមទូរស័ព្ទ (upload រូបភាពទៅ Cloudinary)
@app.route('/add', methods=['POST'])
def add_phone():
    model = request.form.get('model')
    color = request.form.get('color')
    price = request.form.get('price')
    detail = request.form.get('detail')
    image_file = request.files.get('image')

    image_url = ''
    if image_file and image_file.filename != '':
        upload_result = cloudinary.uploader.upload(image_file)
        image_url = upload_result.get('secure_url', '')

    conn = get_database()
    cur = conn.cursor()
    cur.execute(
        'INSERT INTO phone (model, color, price, image, detail) VALUES (%s, %s, %s, %s, %s)',
        (model, color, price, image_url, detail)
    )
    conn.commit()
    conn.close()
    return jsonify({'message': 'Phone added successfully'})

# ✅ Route កែប្រែទូរស័ព្ទ
@app.route('/edit/<int:id>', methods=['POST'])
def edit_phone(id):
    model = request.form.get('model')
    color = request.form.get('color')
    price = request.form.get('price')
    detail = request.form.get('detail')
    image_file = request.files.get('image')

    conn = get_database()
    cur = conn.cursor()

    if image_file and image_file.filename != '':
        upload_result = cloudinary.uploader.upload(image_file)
        image_url = upload_result.get('secure_url', '')
        cur.execute(
            'UPDATE phone SET model=%s, color=%s, price=%s, image=%s, detail=%s WHERE phone_id=%s',
            (model, color, price, image_url, detail, id)
        )
    else:
        cur.execute(
            'UPDATE phone SET model=%s, color=%s, price=%s, detail=%s WHERE phone_id=%s',
            (model, color, price, detail, id)
        )

    conn.commit()
    conn.close()
    return jsonify({'message': 'Phone updated successfully'})

# ✅ Route លុបទូរស័ព្ទ
@app.route('/delete/<int:id>', methods=['DELETE'])
def delete_phone(id):
    conn = get_database()
    cur = conn.cursor()
    cur.execute("DELETE FROM phone WHERE phone_id=%s", (id,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Phone deleted successfully'})

# ✅ Run server
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
