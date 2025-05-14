import os
import hashlib
import argparse
from flask import Flask, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename

app = Flask(__name__)

def create_server():
    # 配置会在运行时通过命令行参数设置
    return app

def calculate_hash(filepath):
    hash_md5 = hashlib.md5()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

@app.route('/mods', methods=['GET'])
def get_mods():
    mods_dir = app.config['SERVER_MODS_DIR']
    mods = []
    for filename in os.listdir(mods_dir):
        if filename.endswith('.jar'):
            filepath = os.path.join(mods_dir, filename)
            mods.append({
                'filename': filename,
                'hash': calculate_hash(filepath)
            })
    return jsonify(mods)

@app.route('/mods/<filename>', methods=['GET'])
def download_mod(filename):
    return send_from_directory(app.config['SERVER_MODS_DIR'], filename)

@app.route('/upload', methods=['POST'])
def upload_mod():
    if request.form.get('password') != app.config['UPLOAD_PASSWORD']:
        return jsonify({'error': 'Invalid password'}), 403

    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    filename = secure_filename(file.filename)
    file.save(os.path.join(app.config['SERVER_MODS_DIR'], filename))
    return jsonify({'message': 'File uploaded successfully'}), 200

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Minecraft Mod同步服务端')
    parser.add_argument('--host', default='0.0.0.0', help='监听地址（默认0.0.0.0）')
    parser.add_argument('--port', type=int, default=5000, help='监听端口（默认5000）')
    parser.add_argument('--mods-dir', required=True, help='服务器mod存储目录')
    parser.add_argument('--password', required=True, help='上传所需密码')
    args = parser.parse_args()

    if not os.path.exists(args.mods_dir):
        os.makedirs(args.mods_dir)

    app.config['SERVER_MODS_DIR'] = args.mods_dir
    app.config['UPLOAD_PASSWORD'] = args.password

    app.run(host=args.host, port=args.port, debug=True)