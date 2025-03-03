import websocket
import time
import logging
import websockets
import threading

# 设置最大重试次数
MAX_RETRIES = 300
RETRY_INTERVAL = 0.5

class WebSocketClient:

    ws = None

    def __init__(self, url, max_retries=1, retry_interval=3):
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
        self.connected = False

    # 连接 WebSocket 的处理函数
    def on_message(self, ws, message):
        logging.info(f"Received message: {message}")

    def on_error(self, ws, error):
        print(error)
        logging.error(f"Error: {error}")

    def on_close(self, ws, close_status_code, close_msg):
        self.connected = False
        logging.warning("WebSocket closed. Attempting to reconnect...")
        # self.reconnect()

    def on_open(self, ws):
        # print("open")
        logging.info("Connection opened")
        self.connected = True

    def get_client(self):
        return self.ws

    def reconnect(self):
        """WebSocket 断线时尝试自动重连"""
        time.sleep(self.retry_interval)
        # self.connect()

    def send(self, req):
        if self.ws:
            self.ws.send(req)
            logging.info(f"Sent: {req}")

    def receive(self):
        """
        接收 WebSocket 服务器的消息
        """
        if self.ws:
            response = self.ws.recv()
            logging.info(f"Received: {response}")
            return response


    # WebSocket 客户端连接函数，包含重试机制
    def connect(self):
        retries = 0
        if self.ws == None:
            while retries < self.max_retries:
                try:
                    logging.warn(f"Attempting to connect... (Attempt {retries + 1})")
                    # ws = websocket.create_connection(url)
                    # self.ws = await websockets.connect(url)
                    self.ws = websocket.WebSocketApp(
                        self.url,
                        on_message=self.on_message,
                        on_error=self.on_error,
                        on_close=self.on_close,
                        on_open=self.on_open
                    )

                    # 启动 WebSocket 客户端并开始监听
                    # thread = threading.Thread(target=self.ws.run_forever)
                    # thread.daemon = True
                    # thread.start()
                    self.ws.run_forever()
                    logging.info("WebSocket connection established.")
                    if self.connected:
                        return self.ws  # 返回 WebSocket 句柄

                except Exception as e:
                    retries += 1
                    logging.warn(f"Error connecting: {e}. Retrying in 0.5 seconds...")
                    time.sleep(self.retry_interval)

            logging.error("Max retries reached. Could not connect.")
            self.ws = None
        return None