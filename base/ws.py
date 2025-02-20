import websocket
import time
import logging

# 设置最大重试次数
MAX_RETRIES = 300

# 连接 WebSocket 的处理函数
def on_message(ws, message):
    logging.info(f"Received message: {message}")

def on_error(ws, error):
    logging.error(f"Error: {error}")

def on_close(ws, close_status_code, close_msg):
    logging.info("Connection closed")

def on_open(ws):
    logging.info("Connection opened")

# WebSocket 客户端连接函数，包含重试机制
async def create_websocket_client(url):
    retries = 0
    ws = None
    while retries < MAX_RETRIES:
        try:
            logging.warn(f"Attempting to connect... (Attempt {retries + 1})")
            ws = websocket.WebSocketApp(
                url,
                on_message=on_message,
                on_error=on_error,
                on_close=on_close,
                on_open=on_open
            )

            # 启动 WebSocket 客户端并开始监听
            ws.run_forever()
            logging.info("WebSocket connection established.")
            return ws  # 成功连接后返回 ws 对象

        except Exception as e:
            retries += 1
            logging.warn(f"Error connecting: {e}. Retrying in 0.5 seconds...")
            time.sleep(0.5)

    logging.error("Max retries reached. Could not connect.")
    return None