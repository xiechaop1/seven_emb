from pydantic import BaseModel
import tiktoken
from aivc.chat.llm.providers.openai_llm import OpenAILLM
from typing import Optional, TypeVar, Generic
from enum import Enum
from sqlmodel import SQLModel, Field
from sqlalchemy import Index
from datetime import datetime
import json
from aivc.common.sleep_common import ReportReqData,ActionRespData

class VCMethod(str, Enum):
    VOICE_CHAT = "voice-chat"
    TEXT_CHAT = "text-chat"
    PING = "ping"
    PONG = "pong"
    REPORT_STATE = "report-state"
    EXECUTE_COMMAND = "execute-command"

class ContentType(str, Enum):
    AUDIO = "audio"
    IMAGE = "image"
    TEXT = "text"

class ConverMsg(BaseModel):
    method: str 
    conversation_id: str
    conversation_id_ts: str
    message_id: str
    message_id_ts: str 
    client_addr: str

class VCReqData(BaseModel):
    content_type: Optional[str] = ContentType.AUDIO.value  # audio or image
    content: Optional[str] = "" # base64 encoded data
    tts_audio_format: Optional[str] = "pcm" # pcm|ogg_opus|mp3

DataT = TypeVar("DataT")

class Req(BaseModel, Generic[DataT]):
    version: str = "1.0"
    method: VCMethod 
    conversation_id: str
    message_id: str
    token: Optional[str] = ""
    timestamp: Optional[str] = ""
    data: Optional[DataT] = None

    def __str__(self):
        data_str = ""
        if isinstance(self.data, VCReqData):
            data_str = f"content_type: {self.data.content_type} content len: {len(self.data.content)} tts_audio_format: {self.data.tts_audio_format}"
        elif isinstance(self.data, ReportReqData):
            image_data_len = len(self.data.images.data) if self.data and self.data.images and self.data.images.data else 0
            audio_data_len = len(self.data.audio.data) if self.data and self.data.audio and self.data.audio.data else 0
            data_str = f"images: {image_data_len} audio: {audio_data_len} scene_exec_status: {self.data.scene_exec_status}"
        return f"version: {self.version} method: {self.method} conversation_id: {self.conversation_id} message_id: {self.message_id} token: {self.token} timestamp: {self.timestamp} data: {data_str}"

class VCRespData(BaseModel):
    action: Optional[str] = None
    text: Optional[str] = None
    audio_format: Optional[str] = "pcm"
    sample_rate: Optional[int] = None
    channels: Optional[int] = None
    sample_format: Optional[str] = None
    bitrate: Optional[int] = None
    audio_data: Optional[str] = None
    stream_seq: int = 0
    
class Resp(BaseModel, Generic[DataT]):
    version: Optional[str] = ""
    method: Optional[VCMethod] = ""
    conversation_id: Optional[str] = ""
    message_id: Optional[str] = ""
    code: int = 0
    message: str = "success"
    data: Optional[DataT] = None

    def __str__(self):
        data_str = ""
        if isinstance(self.data, VCRespData):
            audio_data_len = len(self.data.audio_data) if self.data.audio_data else 0
            data_str = f"action:{self.data.action} audio_format:{self.data.audio_format} audio_data len: {audio_data_len} text: {self.data.text} stream_seq: {self.data.stream_seq}"
        elif isinstance(self.data, ActionRespData):
            data_str = json.dumps(self.data, default=lambda o: o.__dict__, ensure_ascii=False, indent=2)  
            data_str = self.modify_audio_data_in_json(data_str)                            
        return f"version: {self.version} method: {self.method} conversation_id: {self.conversation_id} message_id: {self.message_id} code: {self.code} message: {self.message} data: {data_str}"
    
    def modify_audio_data_in_json(self, data_str):
        """
        修改 JSON 字符串中所有 'audio_data' key 的 value。

        Args:
            data_str: JSON 格式的字符串。

        Returns:
            修改后的 JSON 字符串。
        """
        try:
            data_dict = json.loads(data_str)
        except json.JSONDecodeError as e:
            print(f"JSON 解析错误: {e}")
            return data_str

        def _modify_value(obj):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    if key == 'audio_data':
                        if isinstance(value, list) or isinstance(value, str) or isinstance(value, tuple):
                            obj[key] = f'<audio_data length: {len(value)}>'
                        else:
                            obj[key] = '<audio_data length: unknown>'
                    else:
                        obj[key] = _modify_value(value)
                return obj
            elif isinstance(obj, list):
                return [_modify_value(item) for item in obj]
            else:
                return obj

        modified_data_dict = _modify_value(data_dict)
        modified_data_str = json.dumps(modified_data_dict, ensure_ascii=False, indent=2)
        return modified_data_str

class Prompt(BaseModel):
    system: Optional[str] = ""
    user: Optional[str] = ""


# Define the Model
class Model(BaseModel):
    name: str

def num_tokens_from_string(string: str, model: str = OpenAILLM.GPT35_TURBO) -> int:
    encoding = tiktoken.encoding_for_model(model)
    num_tokens = len(encoding.encode(string))
    return num_tokens

def get_prompt_length(prompt: str, encoding_name: str = "cl100k_base") -> int:
    # if not str return 0
    if not isinstance(prompt, str):
        return 0
    encoding = tiktoken.get_encoding(encoding_name)
    return len(encoding.encode(prompt))

def trim_prompt_to_length(
        prompt: str, 
        length: int, 
        encoding_name: str = "cl100k_base") -> str:
    encoding = tiktoken.get_encoding(encoding_name)
    tokens = encoding.encode(prompt)

    if len(tokens) > length:
        tokens = tokens[:length]
        trimmed_prompt = encoding.decode(tokens)
    else:
        trimmed_prompt = prompt
    return trimmed_prompt


class Conversation(SQLModel, table=True):
    __tablename__ = "conversations"
    
    id: int = Field(primary_key=True) 
    ts: datetime = Field(nullable=False)
    conversation_id: str = Field(nullable=False)
    role: str = Field(nullable=False)
    content: str = Field(nullable=False)
    question_type: str = Field(nullable=True)
    
    __table_args__ = (
        # 复合索引:对话ID+id
        Index("idx_conv_id", "conversation_id", "id"),\
    )

class HandlerResult:
    def __init__(self, question: str, answer: str, question_type: str):
        self.question = question
        self.answer = answer
        self.question_type = question_type
