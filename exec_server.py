from flask import Flask, jsonify, send_from_directory
import json
import os

app = Flask(__name__)

@app.route('/api/version', methods=['GET'])
def get_version():
    if not os.path.exists('version.json'):
        return jsonify({'error': 'version.json not found'}), 404
    with open('version.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    return jsonify(data)

# 新增：文件下载接口
@app.route('/download/<path:filename>', methods=['GET'])
def download_file(filename):
    directory = os.getcwd()  # 当前目录
    if not os.path.exists(os.path.join(directory, filename)):
        return jsonify({'error': 'file not found'}), 404
    return send_from_directory(directory, filename, as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True) 