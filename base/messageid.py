import uuid
from common.code import Code
from datetime import datetime

class messageid:
    
    message_id = {}
    conversation_id = None

    pre_message_id = {}

    last_message_id = {}

    @staticmethod
    def get_id() -> str:
        timestamp = datetime.now().strftime('%Y%m%d-%H%M%S-%f')[:-3]
        return f"{timestamp}-{uuid.uuid4().hex}"

    @staticmethod
    def get_conversation_id() -> str:
        if messageid.conversation_id is None:
            messageid.conversation_id = uuid.uuid4().hex
        return messageid.conversation_id

    @staticmethod
    def get_message_id() -> str:
        return messageid.get_id()

    @staticmethod
    def generate(type = Code.REC_METHOD_VOICE_CHAT):
        # messageid.last_message_id[type] = messageid.message_id[type]
        # messageid.message_id[type] = messageid.get_id()
        messageid.pre_message_id[type] = messageid.get_id()
        return messageid.pre_message_id[type]

    @staticmethod
    def get_pre_message_id(type = Code.REC_METHOD_VOICE_CHAT):
        return messageid.get_pre_message_id(type)

    @staticmethod
    def get_latest_message_id(type = Code.REC_METHOD_VOICE_CHAT):
        return messageid.message_id[type]

    @staticmethod
    def get_token():
        return datetime.utcnow().strftime("%Y%m%d-%H%M%S-") + str(uuid.uuid4())

    @staticmethod
    def confirm_message_id(type = Code.REC_METHOD_VOICE_CHAT):
        messageid.message_id[type] = messageid.pre_message_id[type]
        return messageid.message_id[type]

    @staticmethod
    def cover_with_last(type = Code.REC_METHOD_VOICE_CHAT):
        messageid.message_id[type] = messageid.last_message_id[type]
        return messageid.message_id[type]
