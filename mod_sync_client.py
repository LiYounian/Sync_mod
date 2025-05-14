import os
import hashlib
import requests
import argparse

def calculate_hash(filepath):
    hash_md5 = hashlib.md5()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def sync_mods(server_url, mods_dir, upload_password):
    # 确保目录存在
    os.makedirs(mods_dir, exist_ok=True)
    
    try:
        response = requests.get(f"{server_url}/mods")
        server_mods = {mod['filename']: mod['hash'] for mod in response.json()}
    except Exception as e:
        print(f"无法连接服务器: {e}")
        return

    local_mods = {}
    for filename in os.listdir(mods_dir):
        if filename.endswith('.jar'):
            filepath = os.path.join(mods_dir, filename)
            local_mods[filename] = calculate_hash(filepath)

    to_download = []
    to_remove = []

    for server_file, server_hash in server_mods.items():
        if local_mods.get(server_file) != server_hash:
            to_download.append(server_file)

    for local_file in local_mods:
        if local_file not in server_mods:
            to_remove.append(local_file)

    # 执行下载
    for filename in to_download:
        print(f"正在下载: {filename}")
        try:
            response = requests.get(f"{server_url}/mods/{filename}")
            with open(os.path.join(mods_dir, filename), 'wb') as f:
                f.write(response.content)
        except Exception as e:
            print(f"下载失败 {filename}: {e}")

    # 执行删除
    for filename in to_remove:
        print(f"正在删除: {filename}")
        try:
            os.remove(os.path.join(mods_dir, filename))
        except Exception as e:
            print(f"删除失败 {filename}: {e}")

    print("同步完成！")

def upload_mod(server_url, filepath, upload_password):
    if not os.path.exists(filepath):
        print("文件不存在")
        return

    filename = os.path.basename(filepath)
    try:
        with open(filepath, 'rb') as f:
            files = {'file': (filename, f)}
            data = {'password': upload_password}
            response = requests.post(
                f"{server_url}/upload",
                files=files,
                data=data
            )
            print(response.json().get('message', '上传失败'))
    except Exception as e:
        print(f"上传失败: {e}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Minecraft Mod同步客户端')
    parser.add_argument('--server', required=True, help='服务器地址（包含端口）')
    parser.add_argument('--mods-dir', required=True, help='本地mod目录路径')
    parser.add_argument('--password', required=True, help='上传所需密码')
    parser.add_argument('--sync', action='store_true', help='执行同步操作')
    parser.add_argument('--upload', help='上传指定Mod文件')
    
    args = parser.parse_args()
    
    # 处理路径中的特殊符号（如~）
    mods_dir = os.path.expanduser(args.mods_dir)

    if args.sync:
        sync_mods(args.server, mods_dir, args.password)
    elif args.upload:
        upload_mod(args.server, os.path.expanduser(args.upload), args.password)
    else:
        print("请指定操作类型：--sync 或 --upload")