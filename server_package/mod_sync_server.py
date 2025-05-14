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
    mods = []

    server_mods_dir = app.config['SERVER_MODS_DIR']
    for filename in os.listdir(server_mods_dir):
        if filename.endswith('.jar'):
            filepath = os.path.join(server_mods_dir, filename)
            mods.append({
                'filename': filename,
                'hash': calculate_hash(filepath)
            })
    
    client_mods_dir = app.config['CLIENT_MODS_DIR']
    for filename in os.listdir(client_mods_dir):
        if filename.endswith('.jar'):
            filepath = os.path.join(client_mods_dir, filename)
            mods.append({
                'filename': filename,
                'hash': calculate_hash(filepath)
            })

    return jsonify(mods)


@app.route('/mods/<filename>', methods=['GET'])
def download_mod(filename):
    file_map = {}

    server_mods_dir = app.config['SERVER_MODS_DIR']
    for filename in os.listdir(server_mods_dir):
        if filename.endswith('.jar'):
            file_map[filename] = os.path.join(server_mods_dir, filename)
            
    client_mods_dir = app.config['CLIENT_MODS_DIR']
    for filename in os.listdir(client_mods_dir):
        if filename.endswith('.jar'):
            file_map[filename] = os.path.join(client_mods_dir, filename)

    return send_from_directory(file_map[filename], filename)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Minecraft Mod同步服务端')
    parser.add_argument('--host', default='0.0.0.0', help='监听地址 默认0.0.0.0')
    parser.add_argument('--port', type=int, default=1234, help='监听端口 默认1234')
    parser.add_argument('--server-mods-dir', default='/root/MC/Server/mods', help='服务器mod存储目录')
    parser.add_argument('--client-mods-dir', default='/root/MC/ClinentMods', help='客户端所需mod存储目录')
    args = parser.parse_args()

    if not os.path.exists(args.server_mods_dir):
        os.makedirs(args.server_mods_dir)

    if not os.path.exists(args.client_mods_dir):
        os.makedirs(args.client_mods_dir)

    app.config['SERVER_MODS_DIR'] = args.server_mods_dir
    app.config['CLIENT_MODS_DIR'] = args.client_mods_dir

    app.run(host=args.host, port=args.port, debug=True)