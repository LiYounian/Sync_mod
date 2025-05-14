# ---------- 客户端代码 (client.py) ----------
import os
import requests
import hashlib
import shutil


SERVER_URL = "http://你的服务器IP:5000"  # 修改为你的服务器地址
CLIENT_MODS_DIR = "client_mods"  # 客户端mod目录

def get_local_mods():
    mods = {}
    if not os.path.exists(CLIENT_MODS_DIR):
        os.makedirs(CLIENT_MODS_DIR)
    for filename in os.listdir(CLIENT_MODS_DIR):
        if filename.endswith('.jar'):
            path = os.path.join(CLIENT_MODS_DIR, filename)
            with open(path, 'rb') as f:
                md5 = hashlib.md5(f.read()).hexdigest()
            mods[filename] = md5
    return mods


def sync_mods():
    # 获取服务器mod列表
    try:
        server_mods = requests.get(f"{SERVER_URL}/mods/list").json()
    except Exception as e:
        print(f"连接服务器失败: {e}")
        return

    local_mods = get_local_mods()

    # 删除本地多余mod
    for filename in set(local_mods) - set(server_mods):
        print(f"删除过期mod: {filename}")
        os.remove(os.path.join(CLIENT_MODS_DIR, filename))

    # 下载新增/更新的mod
    for filename, server_md5 in server_mods.items():
        local_md5 = local_mods.get(filename)
        if local_md5 != server_md5:
            print(f"下载mod: {filename}")
            response = requests.get(f"{SERVER_URL}/mods/{filename}")
            with open(os.path.join(CLIENT_MODS_DIR, filename), 'wb') as f:
                f.write(response.content)

    print("同步完成！")


if __name__ == '__main__':
    sync_mods()