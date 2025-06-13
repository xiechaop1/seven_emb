import requests
import json
import os
import sys

try:
    from PySide6.QtWidgets import QApplication, QMessageBox
except ImportError:
    QApplication = None
    QMessageBox = None

SERVER_URL = 'http://114.55.90.104:8000/api/version'
LOCAL_VERSION_FILE = 'version.json'

def get_server_info():
    resp = requests.get(SERVER_URL, timeout=5)
    resp.raise_for_status()
    return resp.json()

def get_local_version():
    if not os.path.exists(LOCAL_VERSION_FILE):
        return '0'
    with open(LOCAL_VERSION_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
        return str(data.get('version', '0'))

def version_greater(v1, v2):
    def parse(v):
        return [int(x) for x in str(v).split('.')]
    return parse(v1) > parse(v2)

def show_comment_dialog(comment):
    if QApplication is None or QMessageBox is None:
        print('PySide6 未安装，无法弹窗。内容如下:')
        print(comment)
        return
    app = QApplication.instance() or QApplication(sys.argv)
    msg = QMessageBox()
    msg.setWindowTitle('系统更新提示')
    msg.setText(comment)
    msg.setIcon(QMessageBox.Information)
    msg.exec()

def main():
    try:
        server_info = get_server_info()
        server_version = str(server_info.get('server_version', '0'))
        comment = server_info.get('comment', '')
        local_version = get_local_version()
        if version_greater(server_version, local_version):
            show_comment_dialog(comment)
        else:
            pass  # 版本无更新，直接退出
    except Exception as e:
        print(f'update.py 执行出错: {e}')

if __name__ == '__main__':
    main() 