from datetime import datetime, time
from enum import Enum
from typing import Optional, Dict, Any
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

class TaskScheduleType(str, Enum):
    ONCE = "once"  # 一次性任务
    DAILY = "daily"  # 每日任务
    WEEKLY = "weekly"  # 每周任务

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

    execution_time: Optional[str] = None
    weekdays: Optional[str] = None
    parameters: Optional[str] = None
    status: TaskStatus = TaskStatus.PENDING
    last_run_time: Optional[str] = None
    last_run_result: Optional[str] = None
    is_enabled: bool = True  # 新增字段，正确放在有默认值字段区

    @classmethod
    def create(cls, **kwargs) -> 'Task':
        """创建新任务"""
        now = datetime.now().isoformat()
        return cls(
            id=kwargs.get('id', 0),
            created_at=now,
            updated_at=now,
            **kwargs
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
