# ---------- 服务端代码 (server.py) ----------
import os
import hashlib
from flask import Flask, send_file, jsonify

app = Flask(__name__)
MODS_DIR = "server_mods"  # 服务端mod目录

def get_mods_info():
    mods = {}
    for filename in os.listdir(MODS_DIR):
        if filename.endswith('.jar'):
            path = os.path.join(MODS_DIR, filename)
            with open(path, 'rb') as f:
                md5 = hashlib.md5(f.read()).hexdigest()
            mods[filename] = md5
    return mods

@app.route('/mods/list')
def mods_list():
    return jsonify(get_mods_info())

@app.route('/mods/<filename>')
def download_mod(filename):
    safe_path = os.path.join(MODS_DIR, os.path.basename(filename))
    if not os.path.exists(safe_path):
        return "Not Found", 404
    return send_file(safe_path, as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)