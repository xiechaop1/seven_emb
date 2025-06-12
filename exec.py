import os
import json
import hashlib
import requests
import shutil
import subprocess
import time

# 配置
SERVER_URL = 'http://114.55.90.104:8000/api/version'  # 替换为实际接口
VER_FILE = 'ver.json'
TMP_DIR = './tmp'

rate = 0  # 全局进度百分比

# 1. 读取本地版本号
def get_local_version():
    if not os.path.exists(VER_FILE):
        return '0.0.0'
    with open(VER_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
        return data.get('version', '0.0.0')

# 2. 请求服务端json（增加重试3次）
def get_server_info():
    global rate
    retry = 3
    for i in range(retry):
        try:
            resp = requests.get(SERVER_URL, timeout=5)
            resp.raise_for_status()
            info = resp.json()
            rate += 1
            write_update_status("get_server_info", "")
            return info
        except Exception as e:
            write_update_status("get_server_info", str(e))
            time.sleep(1)
    print('请求服务端失败，已重试3次，程序退出。')
    exit(1)

# 3. 版本号比较
def version_greater(v1, v2):
    def parse(v):
        return [int(x) for x in v.split('.')]
    return parse(v1) > parse(v2)

# 4. 下载文件（带进度和写入update_executing.json）
def write_update_status(file, err=None):
    global rate
    with open('update_executing.json', 'w', encoding='utf-8') as jf:
        json.dump({"file": os.path.basename(file), "rate": rate, "err": err or ""}, jf, ensure_ascii=False)

def download_file(url, dest):
    global rate
    try:
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            total = int(r.headers.get('content-length', 0))
            downloaded = 0
            last_rate = -1
            with open(dest, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total > 0:
                            # 下载进度百分比，最大到98
                            download_percent = int((downloaded / total) * 97)
                            new_rate = min(1 + download_percent, 98)  # 1是get_server_info后的进度
                            if new_rate != last_rate:
                                rate = new_rate
                                last_rate = new_rate
                                write_update_status(dest, "")
        return True
    except Exception as e:
        write_update_status(dest, str(e))
        raise

# 5. 校验md5
def check_md5(filepath, md5):
    hash_md5 = hashlib.md5()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest() == md5

# 6. 解压缩
def extract_file(filepath, outdir):
    global rate
    try:
        if filepath.endswith('.tar.gz'):
            import tarfile
            with tarfile.open(filepath, 'r:gz') as tar:
                tar.extractall(outdir)
        elif filepath.endswith('.zip'):
            import zipfile
            with zipfile.ZipFile(filepath, 'r') as zip_ref:
                zip_ref.extractall(outdir)
        elif filepath.endswith('.rar'):
            subprocess.run(['unrar', 'x', '-o+', filepath, outdir], check=True)
        else:
            raise ValueError('不支持的文件类型')
        rate += 1
        write_update_status(filepath, "")
    except Exception as e:
        write_update_status(filepath, str(e))
        raise

# 7. 执行脚本
def exec_script(tmpdir, last_file):
    global rate
    try:
        for fname in os.listdir(tmpdir):
            fpath = os.path.join(tmpdir, fname)
            if os.path.isfile(fpath):
                if fname.endswith('.sh'):
                    subprocess.run(['sh', fpath], check=True)
                    rate += 1
                    write_update_status(last_file, "")
                    return
                elif fname.endswith('.py'):
                    subprocess.run(['python3', fpath], check=True)
                    rate += 1
                    write_update_status(last_file, "")
                    return
        # 没有脚本也算成功
        rate += 1
        write_update_status(last_file, "")
    except Exception as e:
        write_update_status(last_file, str(e))
        raise

if __name__ == '__main__':
    local_version = get_local_version()
    print('本地版本:', local_version)
    info = get_server_info()
    print('服务端信息:', info)
    server_version = info['server_version']
    file_url = info['file']
    comment = info['comment']
    update_type = info['update_type']
    md5 = info['md5']

    if version_greater(server_version, local_version):
        print(f'发现新版本: {server_version}, 开始下载...')
        os.makedirs(TMP_DIR, exist_ok=True)
        filename = os.path.join(TMP_DIR, os.path.basename(file_url))
        try:
            download_file(file_url, filename)
            print('下载完成，校验MD5...')
            if not check_md5(filename, md5):
                write_update_status(filename, 'MD5校验失败!')
                print('MD5校验失败!')
                exit(1)
            print('MD5校验通过，解压缩...')
            extract_file(filename, TMP_DIR)
            print('解压完成，查找可执行脚本...')
            exec_script(TMP_DIR, filename)
        except Exception as e:
            print('更新过程出错:', e)
    else:
        print('当前已是最新版本，无需更新。') 