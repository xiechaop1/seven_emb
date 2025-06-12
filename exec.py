import os
import json
import hashlib
import requests
import shutil
import subprocess

# 配置
SERVER_URL = 'http://114.55.90.104:8000/api/version'  # 替换为实际接口
VER_FILE = 'ver.json'
TMP_DIR = './tmp'

# 1. 读取本地版本号
def get_local_version():
    if not os.path.exists(VER_FILE):
        return '0.0.0'
    with open(VER_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
        return data.get('version', '0.0.0')

# 2. 请求服务端json
def get_server_info():
    resp = requests.get(SERVER_URL)
    resp.raise_for_status()
    return resp.json()

# 3. 版本号比较
def version_greater(v1, v2):
    def parse(v):
        return [int(x) for x in v.split('.')]
    return parse(v1) > parse(v2)

# 4. 下载文件
def download_file(url, dest):
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(dest, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)

# 5. 校验md5
def check_md5(filepath, md5):
    hash_md5 = hashlib.md5()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest() == md5

# 6. 解压缩
def extract_file(filepath, outdir):
    if filepath.endswith('.tar.gz'):
        import tarfile
        with tarfile.open(filepath, 'r:gz') as tar:
            tar.extractall(outdir)
    elif filepath.endswith('.zip'):
        import zipfile
        with zipfile.ZipFile(filepath, 'r') as zip_ref:
            zip_ref.extractall(outdir)
    elif filepath.endswith('.rar'):
        # 需要安装unrar命令
        subprocess.run(['unrar', 'x', '-o+', filepath, outdir], check=True)
    else:
        raise ValueError('不支持的文件类型')

# 7. 执行脚本
def exec_script(tmpdir):
    for fname in os.listdir(tmpdir):
        fpath = os.path.join(tmpdir, fname)
        if os.path.isfile(fpath):
            if fname.endswith('.sh'):
                subprocess.run(['sh', fpath], check=True)
                return
            elif fname.endswith('.py'):
                subprocess.run(['python3', fpath], check=True)
                return

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
        download_file(file_url, filename)
        print('下载完成，校验MD5...')
        if not check_md5(filename, md5):
            print('MD5校验失败!')
            exit(1)
        print('MD5校验通过，解压缩...')
        extract_file(filename, TMP_DIR)
        print('解压完成，查找可执行脚本...')
        exec_script(TMP_DIR)
    else:
        print('当前已是最新版本，无需更新。') 