import sys
import json
import os


class InitManager:
    def __init__(self):
        self.init_file = "init.json"
        self.data = None

    def load_init_data(self):
        """加载初始化数据"""
        if os.path.exists(self.init_file):
            try:
                with open(self.init_file, 'r', encoding='utf-8') as f:
                    self.data = json.load(f)
                return True
            except Exception as e:
                print(f"Error loading init data: {e}")
                return False
        return False

    def save_init_data(self, data):
        """保存初始化数据"""
        try:
            with open(self.init_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Error saving init data: {e}")
            return False