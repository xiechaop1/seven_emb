from datetime import datetime, time
from enum import Enum
from typing import Optional, Dict, Any, List
import json
from dataclasses import dataclass, asdict
from dataclasses_json import dataclass_json

class TaskType(str, Enum):
    ALARM = "alarm"  # 闹钟任务
    SYSTEM = "system"  # 系统任务
    CUSTOM = "custom"  # 自定义任务

class TaskStatus(str, Enum):
    PENDING = "pending"  # 等待执行
    RUNNING = "running"  # 执行中
    COMPLETED = "completed"  # 已完成
    FAILED = "failed"  # 执行失败
    CANCELLED = "cancelled"  # 已取消
    DISABLED = "disabled"

class TaskScheduleType(str, Enum):
    ONCE = "once"  # 一次性任务
    DAILY = "daily"  # 每日任务
    WEEKLY = "weekly"  # 每周任务

class ActionType(str, Enum):
    LIGHT = "light"  # 灯光控制
    SOUND = "sound"  # 声音播放
    DISPLAY = "display"  # 屏幕显示
    SPRAY = "spray"
    COMBINED = "combined"  # 组合动作
    MODULE = "module"
    PYTHON = "python"
    SHELL = "shell"

class LightCommand(str, Enum):
    TURN_ON = "turn_on"
    TURN_OFF = "turn_off"
    SET_BRIGHTNESS = "set_brightness"
    SET_COLOR = "set_color"
    SET_SCENE = "set_scene"

class SoundCommand(str, Enum):
    PLAY = "play"
    STOP = "stop"
    PAUSE = "pause"
    SET_VOLUME = "set_volume"
    SET_LOOP = "set_loop"

class DisplayCommand(str, Enum):
    SHOW_TEXT = "show_text"
    SHOW_IMAGE = "show_image"
    SHOW_ANIMATION = "show_animation"
    CLEAR = "clear"

@dataclass_json
@dataclass
class LightParameters:
    """灯光控制参数"""
    mode: str  # 灯光模式
    params: Dict[str, Any]  # 可变参数表
    # command: LightCommand
    # brightness: Optional[int] = None  # 0-100
    # color: Optional[str] = None  # RGB或色温
    # scene: Optional[str] = None  # 场景名称
    # duration: Optional[int] = None  # 持续时间（秒）
    # transition: Optional[int] = None  # 过渡时间（毫秒）

@dataclass_json
@dataclass
class SoundParameters:
    """声音控制参数"""
    command: SoundCommand
    file_path: Optional[str] = None  # 音频文件路径
    volume: Optional[int] = None  # 0-100
    loop: Optional[bool] = None  # 是否循环
    duration: Optional[int] = None  # 播放时长（秒）

@dataclass_json
@dataclass
class DisplayParameters:
    """显示控制参数"""
    command: DisplayCommand
    content: Optional[str] = None  # 显示内容
    image_path: Optional[str] = None  # 图片路径
    animation_type: Optional[str] = None  # 动画类型
    duration: Optional[int] = None  # 显示时长（秒）
    position: Optional[Dict[str, int]] = None  # 显示位置
    style: Optional[Dict[str, Any]] = None  # 显示样式

@dataclass_json
@dataclass
class TaskAction:
    """任务执行动作"""
    action_type: ActionType
    target: str  # 目标ID或路径
    parameters: Optional[Dict[str, Any]] = None  # 动作参数

    def get_light_params(self) -> Optional[LightParameters]:
        """获取灯光参数"""
        if self.action_type == ActionType.LIGHT and self.parameters:
            return LightParameters.from_dict(self.parameters)
        return None

    def get_sound_params(self) -> Optional[SoundParameters]:
        """获取声音参数"""
        if self.action_type == ActionType.SOUND and self.parameters:
            return SoundParameters.from_dict(self.parameters)
        return None

    def get_display_params(self) -> Optional[DisplayParameters]:
        """获取显示参数"""
        if self.action_type == ActionType.DISPLAY and self.parameters:
            return DisplayParameters.from_dict(self.parameters)
        return None

@dataclass_json
@dataclass
class Task:
    id: int
    name: str
    task_type: TaskType
    schedule_type: TaskScheduleType
    next_run_time: str
    content: str
    created_at: str
    updated_at: str
    actions: str  # 新增：任务执行动作列表（JSON字符串）

    execution_time: Optional[str] = None
    weekdays: Optional[str] = None
    parameters: Optional[str] = None
    status: TaskStatus = TaskStatus.PENDING
    last_run_time: Optional[str] = None
    last_run_result: Optional[str] = None
    is_enabled: bool = True
    duration: Optional[int] = None  # 任务持续时间（秒），None表示持续执行直到手动停止

    @classmethod
    def create(cls, **kwargs) -> 'Task':
        """创建新任务"""
        now = datetime.now().isoformat()
        # 确保actions字段存在
        if 'actions' not in kwargs:
            kwargs['actions'] = json.dumps([])
        return cls(
            id=kwargs.get('id', 0),
            name=kwargs.get('name', ''),
            task_type=kwargs.get('task_type', TaskType.CUSTOM),
            schedule_type=kwargs.get('schedule_type', TaskScheduleType.ONCE),
            next_run_time=kwargs.get('next_run_time', now),
            content=kwargs.get('content', ''),
            created_at=now,
            updated_at=now,
            actions=kwargs.get('actions', json.dumps([])),
            execution_time=kwargs.get('execution_time'),
            weekdays=kwargs.get('weekdays'),
            parameters=kwargs.get('parameters'),
            status=kwargs.get('status', TaskStatus.PENDING),
            last_run_time=kwargs.get('last_run_time'),
            last_run_result=kwargs.get('last_run_result'),
            is_enabled=kwargs.get('is_enabled', True),
            duration=kwargs.get('duration')
        )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Task':
        """从字典创建任务对象"""
        return cls(**data)

    def update(self, **kwargs):
        """更新任务属性"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.updated_at = datetime.now().isoformat()

    def get_actions(self) -> List[TaskAction]:
        """获取任务动作列表"""
        return [TaskAction.from_dict(action) for action in json.loads(self.actions)]

    def set_actions(self, actions: List[TaskAction]):
        """设置任务动作列表"""
        self.actions = json.dumps([action.to_dict() for action in actions])
