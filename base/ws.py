import websocket
import threading
import time
import logging
import queue
import datetime
from config import config
from model.undertake_callback import UndertakeCallback

from common.scence import Scence

# logging.basicConfig(level=logging.INFO)


class WebSocketClient:
    def __init__(self, url, max_retries=5, retry_interval=3):
        """
        初始化 WebSocket 客户端
        :param url: WebSocket 服务器地址
        :param max_retries: 最大重连次数
        :param retry_interval: 断线后重连间隔
        """
        self.url = url
        self.ws = None
        self.max_retries = max_retries
        self.retry_interval = retry_interval
        self.close_retries = 0
        self.timeout = 3
        self.connected = False
        self.error_callback = None

        self.message_queue = queue.Queue()

    def set_callback(self, callback):
        self.error_callback = callback

    def on_message(self, ws, message):
        """接收 WebSocket 消息"""
        logging.debug(f"Received message: {message}")
        self.message_queue.put(message)

    def on_error(self, ws, error):
        """处理 WebSocket 错误"""
        logging.error(f"Error: {error}")

        if self.error_callback:
            self.error_callback(error)

    def on_close(self, ws, close_status_code, close_msg):
        """WebSocket 连接关闭时触发"""
        self.connected = False
        logging.warning("WebSocket closed. Attempting to reconnect...")
        time.sleep(self.retry_interval)
        self.reconnect()

    def on_open(self, ws):
        """WebSocket 连接成功时触发"""
        logging.info("WebSocket connection established.")
        ws.sock.settimeout(self.timeout)
        self.connected = True

    def connect(self):
        """
        连接 WebSocket 服务器，并返回 WebSocket 句柄
        """
        retries = 0
        while retries < self.max_retries:
            try:
                logging.info(f"Connecting to WebSocket: {self.url} (Attempt {retries + 1})")

                self.ws = websocket.WebSocketApp(
                    self.url,
                    on_message=self.on_message,
                    on_error=self.on_error,
                    on_close=
                    self.on_close,
                    on_open=self.on_open
                )

                # 在新线程中运行 WebSocket
                thread = threading.Thread(target=self.ws.run_forever)
                thread.daemon = True
                thread.start()

                time.sleep(2)  # 等待连接建立
                if self.connected:
                    return self.ws  # 返回 WebSocket 句柄

            except Exception as e:
                logging.error(f"Connection failed: {e}")
                retries += 1
                time.sleep(self.retry_interval * retries)

        logging.error("Max retries reached. Could not connect.")
        return None

    def reconnect(self):
        """WebSocket 断线时尝试自动重连"""
        time.sleep(self.retry_interval)
        self.connect()

    def send(self, message):
        """
        发送 WebSocket 消息
        # :param ws: WebSocket 句柄
        :param message: 要发送的消息
        """
        # print(ws, self.connected)
        ws = self.ws
        # print("cb:", self.error_callback)
        if ws and self.connected:
            try:
                logging.info(f"Sending message: {datetime.datetime.now()}")
                ws.send(message)
                # print(message)
                logging.info(f"Sent: {datetime.datetime.now()}")
            except Exception as e:
                # print(f"Error: {e}")
                logging.error(f"Failed to send message: {e}")
        else:
            logging.warning("WebSocket is not connected. Unable to send message.")
            self.connect()

    def receive(self, timeout=None):
        """
        获取 WebSocket 服务器返回的数据（从队列取数据）
        :param timeout: 设定超时时间（秒），默认无限等待
        :return: 返回收到的 WebSocket 消息（如果有的话）
        """
        try:
            message = self.message_queue.get(timeout=timeout)  # 从队列取出消息
            return message
        except queue.Empty:
            return None  # 队列为空，返回 None

# # **测试 WebSocket 连接**
# if __name__ == "__main__":
#     websocket_url = "ws://example.com/ws"  # 替换为你的 WebSocket 地址
#     client = WebSocketClient(websocket_url)
#
#     # **获取 WebSocket 句柄**
#     ws_handler = client.connect()
#
#     if ws_handler:
#         # **使用 WebSocket 句柄发送消息**
#         client.send(ws_handler, "Hello, WebSocket!")
#
#     # 保持主线程运行
#     while True:
#         time.sleep(1)