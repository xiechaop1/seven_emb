import uuid
from datetime import datetime

class messageid:
    
    message_id = 0


    def get_id() -> str:
        timestamp = datetime.now().strftime('%Y%m%d-%H%M%S-%f')[:-3]
        return f"{timestamp}-{uuid.uuid4().hex}"

    def get_conversation_id() -> str:
        return uuid.uuid4().hex

    def get_message_id() -> str:
        return messageid.get_id()

    def generate():
        messageid.message_id = messageid.get_id()
        return messageid.message_id

    def get_latest_message_id():
        return messageid.message_id

    def get_token():
        datetime.utcnow().strftime("%Y%m%d-%H%M%S-") + str(uuid.uuid4())
