import logging
from datetime import datetime, time, timedelta
from typing import Optional, List, Dict
import json
import threading
import time as time_module
import os

from common.threading_event import ThreadingEvent
from .task import Task, TaskStatus, TaskScheduleType, TaskType, TaskAction, ActionType, LightCommand, SoundCommand, DisplayCommand
import signal
import sys
from common.code import Code

# 配置日志格式
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

class TaskAction:
    def __init__(self, action_type: ActionType, target: str, parameters: dict = None):
        self.action_type = action_type
        self.target = target
        self.parameters = parameters or {}

    @classmethod
    def create_light_action(cls, mode: str, params: dict) -> 'TaskAction':
        """创建灯光动作"""
        return cls(
            action_type=ActionType.LIGHT,
            target="light",
            parameters={
                "mode": mode,
                "params": params
            }
        )

    @classmethod
    def create_screen_action(cls, mode: str, params: dict) -> 'TaskAction':
        """创建屏幕动作"""
        return cls(
            action_type=ActionType.DISPLAY,
            target="screen",
            parameters={
                "mode": mode,
                "params": params
            }
        )

    @classmethod
    def create_sound_action(cls, file_path: str, volume: int = 100) -> 'TaskAction':
        """创建声音动作"""
        return cls(
            action_type=ActionType.SOUND,
            target="sound",
            parameters={
                "file_path": file_path,
                "volume": volume
            }
        )

    @classmethod
    def create_spray_action(cls, mode: str, duration: int = 5) -> 'TaskAction':
        """创建香氛动作"""
        return cls(
            action_type=ActionType.SPRAY,
            target="spray",
            parameters={
                "mode": mode,
                "duration": duration
            }
        )

class TaskScheduler:
    def __init__(self, storage_file, audioPlayerIns, lightIns, sprayIns):
        self.storage_file = storage_file
        self.running = False
        self.thread = None
        self.lock = threading.Lock()
        self.last_check_time = None

        self.audio_player = audioPlayerIns
        self.light = lightIns
        self.spray = sprayIns

        self.task_threads = {}  # 用于存储任务执行线程
        self.thread_lock = threading.Lock()  # 用于保护task_threads的访问
        self.running_tasks = {}  # 用于存储正在运行的任务及其停止事件
        self.task_stop_events = {}  # 用于存储任务的停止事件

        logging.info(f"初始化任务调度器，存储文件: {storage_file}")
        
    def _load_tasks(self) -> Dict[int, Task]:
        """从文件加载任务"""
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    tasks = {int(k): Task.from_dict(v) for k, v in data.get('tasks', {}).items()}
                    next_id = data.get('next_id', 1)
                logging.debug(f"从文件加载 {len(tasks)} 个任务")
                return tasks, next_id
            except Exception as e:
                logging.error(f"加载任务文件失败: {str(e)}")
                return {}, 1
        else:
            logging.info("任务文件不存在，创建新的任务列表")
            return {}, 1
                
    def _save_tasks(self, tasks: Dict[int, Task], next_id: int):
        """保存任务到文件"""
        try:
            data = {
                'tasks': {str(k): v.to_dict() for k, v in tasks.items()},
                'next_id': next_id
            }
            with open(self.storage_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logging.debug(f"成功保存 {len(tasks)} 个任务到文件")
        except Exception as e:
            logging.error(f"保存任务到文件失败: {str(e)}")
            
    def start(self):
        """启动调度器"""
        if self.running:
            logging.warning("调度器已经在运行中")
            return
            
        self.running = True
        self.thread = threading.Thread(target=self._scheduler_loop)
        self.thread.daemon = True
        self.thread.start()
        logging.info("任务调度器已启动")
        
    def stop(self):
        """停止调度器"""
        if not self.running:
            logging.warning("调度器未在运行")
            return
            
        self.running = False
        
        # 等待所有任务线程完成
        with self.thread_lock:
            for thread in self.task_threads.values():
                thread.join(timeout=5)  # 最多等待5秒
            
        if self.thread:
            self.thread.join()
        logging.info("任务调度器已停止")
            
    def _scheduler_loop(self):
        """调度器主循环"""
        logging.info("开始调度器主循环")
        while self.running:
            try:
                now = datetime.now()
                # 每分钟检查一次
                if (self.last_check_time is None or 
                    (now - self.last_check_time).total_seconds() >= 5):
                    self._check_and_execute_tasks()
                    self.last_check_time = now
                time_module.sleep(1)
            except Exception as e:
                logging.error(f"调度器主循环发生错误: {str(e)}")
                
    def _check_and_execute_tasks(self):
        """检查并执行到期的任务"""
        with self.lock:
            tasks, next_id = self._load_tasks()
            now = datetime.now()
            
            # 查找所有待执行的任务
            tasks_to_execute = []
            for task in tasks.values():
                if (task.status == TaskStatus.PENDING and 
                    task.is_enabled and
                    datetime.fromisoformat(task.next_run_time) <= now):
                    
                    time_diff = (now - datetime.fromisoformat(task.next_run_time)).total_seconds()
                    
                    # 一次性任务：5秒内执行
                    if task.schedule_type == TaskScheduleType.ONCE and time_diff <= 5:
                        tasks_to_execute.append(task)
                    # 周期性任务：1秒内执行
                    elif task.schedule_type in [TaskScheduleType.DAILY, TaskScheduleType.WEEKLY] and time_diff <= 1:
                        tasks_to_execute.append(task)
            
            if tasks_to_execute:
                logging.info(f"发现 {len(tasks_to_execute)} 个待执行任务")
                for task in tasks_to_execute:
                    logging.info(f"准备执行任务: ID={task.id}, 名称={task.name}, "
                               f"类型={task.task_type}, 计划执行时间={task.next_run_time}")
                    self._execute_task_concurrent(task, tasks, next_id)
            else:
                # 显示下一个要执行的任务
                next_tasks = sorted(
                    [(task, datetime.fromisoformat(task.next_run_time)) 
                     for task in tasks.values() 
                     if task.status == TaskStatus.PENDING and task.is_enabled],
                    key=lambda x: x[1]
                )
                if next_tasks:
                    next_task, next_time = next_tasks[0]
                    # 检查是否有过期未执行的任务
                    if (now - next_time).total_seconds() > 5:
                        logging.warning(f"任务已过期未执行: ID={next_task.id}, 名称={next_task.name}, "
                                      f"计划执行时间={next_time.isoformat()}, "
                                      f"已过期 {(now - next_time).total_seconds()/60:.1f} 分钟")
                        # 如果是单次任务，直接禁用
                        if next_task.schedule_type == TaskScheduleType.ONCE:
                            next_task.is_enabled = False
                            tasks[next_task.id] = next_task
                            self._save_tasks(tasks, next_id)
                            logging.info(f"单次任务已过期，已禁用: ID={next_task.id}, 名称={next_task.name}")
                    else:
                        logging.debug(f"下一个待执行任务: ID={next_task.id}, 名称={next_task.name}, "
                                    f"计划执行时间={next_time.isoformat()}")
                
    def _execute_task_concurrent(self, task: Task, tasks: Dict[int, Task], next_id: int):
        """并发执行任务"""
        def task_execution():
            try:
                # 创建停止事件
                stop_event = threading.Event()
                with self.thread_lock:
                    self.task_stop_events[task.id] = stop_event
                    self.running_tasks[task.id] = task

                # 更新任务状态为执行中
                with self.lock:
                    task.status = TaskStatus.RUNNING
                    task.last_run_time = datetime.now().isoformat()
                    tasks[task.id] = task
                    self._save_tasks(tasks, next_id)
                logging.debug(f"任务状态已更新为执行中: ID={task.id}")
                
                # 执行所有动作
                actions = task.get_actions()
                for action in actions:
                    if action.action_type == ActionType.LIGHT:
                        self._execute_light_action(action)
                    elif action.action_type == ActionType.SOUND:
                        self._execute_sound_action(action)
                    elif action.action_type == ActionType.DISPLAY:
                        self._execute_display_action(action)
                    elif action.action_type == ActionType.SPRAY:
                        self._execute_spray_action(action)
                
                # 如果设置了持续时间，等待指定时间后停止
                if task.duration is not None:
                    if stop_event.wait(timeout=task.duration):
                        logging.info(f"任务被手动停止: ID={task.id}")
                    else:
                        logging.info(f"任务达到持续时间自动停止: ID={task.id}")
                    self.stop_task(task.id)
                
                # 更新任务状态和结果
                with self.lock:
                    task.last_run_result = json.dumps({"success": True, "message": "Task executed"})
                    task.status = TaskStatus.COMPLETED
                    
                    # 如果是单次任务，执行完成后禁用
                    if task.schedule_type == TaskScheduleType.ONCE:
                        task.is_enabled = False
                        logging.info(f"单次任务执行完成，已禁用: ID={task.id}, 名称={task.name}")
                    else:
                        # 计算下次执行时间
                        self._calculate_next_run_time(task)
                        logging.debug(f"任务下次执行时间已更新: ID={task.id}, 时间={task.next_run_time}")
                    
                    tasks[task.id] = task
                    self._save_tasks(tasks, next_id)
                
            except Exception as e:
                logging.error(f"任务执行失败: ID={task.id}, 错误={str(e)}")
                with self.lock:
                    task.status = TaskStatus.FAILED
                    task.last_run_result = json.dumps({
                        "success": False,
                        "error": str(e)
                    })
                    tasks[task.id] = task
                    self._save_tasks(tasks, next_id)
            finally:
                # 清理任务记录
                with self.thread_lock:
                    if task.id in self.task_stop_events:
                        del self.task_stop_events[task.id]
                    if task.id in self.running_tasks:
                        del self.running_tasks[task.id]
                    if task.id in self.task_threads:
                        del self.task_threads[task.id]

        # 创建并启动任务执行线程
        thread = threading.Thread(target=task_execution)
        thread.daemon = True
        with self.thread_lock:
            self.task_threads[task.id] = thread
        thread.start()

    def _run_task(self, task: Task) -> dict:
        """运行具体任务"""
        try:
            actions = task.get_actions()
            results = []
            
            for action in actions:
                result = self._execute_action(action)
                results.append(result)
                
            return {
                "success": all(r.get("success", False) for r in results),
                "message": "Task executed successfully",
                "results": results
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def _execute_action(self, action: TaskAction) -> dict:
        """执行具体动作"""
        try:
            if action.action_type == ActionType.LIGHT:
                return self._execute_light_action(action)
            elif action.action_type == ActionType.SOUND:
                return self._execute_sound_action(action)
            elif action.action_type == ActionType.DISPLAY:
                return self._execute_display_action(action)
            elif action.action_type == ActionType.SPRAY:
                return self._execute_spray_action(action)
            elif action.action_type == ActionType.COMBINED:
                return self._execute_combined_action(action)
            else:
                raise ValueError(f"未知的动作类型: {action.action_type}")
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def _execute_light_action(self, action: TaskAction) -> dict:
        """执行灯光控制动作"""
        try:
            params = action.parameters
            mode = params.get("mode")
            light_params = params.get("params", {})
            
            if not mode:
                raise ValueError("无效的灯光模式")
            
            self.light.start(mode, light_params, Code.LIGHT_TYPE_TEMP)
            
            return {
                "success": True,
                "message": f"灯光模式已设置为: {mode}",
                "parameters": params
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def _execute_sound_action(self, action: TaskAction) -> dict:
        """执行声音播放动作"""
        try:
            params = action.parameters
            file_path = params.get("file_path")
            volume = params.get("volume", 100)
            
            if not file_path:
                raise ValueError("无效的声音文件路径")
            
            self.audio_player.play_music_with_file(file_path)
            # 设置音量
            self.audio_player.set_volume(volume)
            
            return {
                "success": True,
                "message": f"开始播放: {file_path}",
                "parameters": params
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def _execute_display_action(self, action: TaskAction) -> dict:
        """执行屏幕显示动作"""
        try:
            params = action.parameters
            mode = params.get("mode")
            display_params = params.get("params", {})
            
            if not mode:
                raise ValueError("无效的显示模式")
            
            # 根据模式执行不同的显示效果
            if mode == "animation":
                # 播放动画
                pass
            elif mode == "text":
                # 显示文本
                pass
            elif mode == "image":
                # 显示图片
                pass
            
            return {
                "success": True,
                "message": f"显示模式已设置为: {mode}",
                "parameters": params
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def _execute_spray_action(self, action: TaskAction) -> dict:
        """执行香氛动作"""
        try:
            params = action.parameters
            mode = params.get("mode")
            duration = params.get("duration", 5)
            
            if not mode:
                raise ValueError("无效的香氛模式")
            
            self.spray.start(mode, duration)
            
            return {
                "success": True,
                "message": f"开始喷香: {mode}",
                "parameters": params
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def _execute_combined_action(self, action: TaskAction) -> dict:
        """执行组合动作"""
        # TODO: 实现组合动作的执行逻辑
        return {
            "success": True,
            "message": "组合动作执行成功",
            "parameters": action.parameters
        }
        
    def _calculate_next_run_time(self, task: Task):
        """计算下次执行时间"""
        now = datetime.now()
        
        if task.schedule_type == TaskScheduleType.ONCE:
            task.next_run_time = None
        elif task.schedule_type == TaskScheduleType.DAILY:
            # 计算明天的执行时间
            next_time = datetime.combine(now.date(), time.fromisoformat(task.execution_time))
            if next_time <= now:
                next_time += timedelta(days=1)
            task.next_run_time = next_time.isoformat()
        elif task.schedule_type == TaskScheduleType.WEEKLY:
            weekdays = json.loads(task.weekdays)
            current_weekday = now.weekday() + 1  # 1-7
            
            # 找到下一个执行日期
            next_weekday = None
            for day in sorted(weekdays):
                if day > current_weekday:
                    next_weekday = day
                    break
                    
            if next_weekday is None:
                next_weekday = min(weekdays)
                days_ahead = 7 - current_weekday + next_weekday
            else:
                days_ahead = next_weekday - current_weekday
                
            next_time = datetime.combine(now.date(), time.fromisoformat(task.execution_time))
            next_time += timedelta(days=days_ahead)
            task.next_run_time = next_time.isoformat()
            
    def add_task(self, task: Task) -> Task:
        """添加新任务"""
        with self.lock:
            tasks, next_id = self._load_tasks()
            task.id = next_id
            next_id += 1
            tasks[task.id] = task
            self._save_tasks(tasks, next_id)
            logging.info(f"添加新任务成功: ID={task.id}, 名称={task.name}, "
                        f"类型={task.task_type}, 计划执行时间={task.next_run_time}")
            return task
            
    def remove_task(self, task_id: int) -> bool:
        """移除任务"""
        with self.lock:
            tasks, next_id = self._load_tasks()
            if task_id in tasks:
                task = tasks[task_id]
                del tasks[task_id]
                self._save_tasks(tasks, next_id)
                logging.info(f"移除任务成功: ID={task_id}, 名称={task.name}")
                return True
            logging.warning(f"移除任务失败: ID={task_id} 不存在")
            return False
            
    def get_task(self, task_id: int) -> Optional[Task]:
        """获取任务"""
        tasks, _ = self._load_tasks()
        task = tasks.get(task_id)
        if task:
            logging.debug(f"获取任务: ID={task_id}, 名称={task.name}, 状态={task.status}")
        else:
            logging.debug(f"获取任务失败: ID={task_id} 不存在")
        return task
        
    def get_pending_tasks(self) -> List[Task]:
        """获取所有待执行的任务"""
        tasks, _ = self._load_tasks()
        pending_tasks = [task for task in tasks.values() if task.status == TaskStatus.PENDING]
        logging.debug(f"当前待执行任务数量: {len(pending_tasks)}")
        for task in pending_tasks:
            logging.debug(f"待执行任务: ID={task.id}, 名称={task.name}, "
                        f"计划执行时间={task.next_run_time}")
        return pending_tasks

    def stop_task(self, task_id: int) -> bool:
        """手动停止任务"""
        with self.thread_lock:
            if task_id in self.task_stop_events:
                # 设置停止事件
                self.task_stop_events[task_id].set()
                
                # 停止相关的硬件操作
                if task_id in self.running_tasks:
                    task = self.running_tasks[task_id]
                    actions = task.get_actions()
                    for action in actions:
                        if action.action_type == ActionType.LIGHT:
                            self.light.start_prev()
                        elif action.action_type == ActionType.SOUND:
                            self.audio_player.stop_music()
                            ThreadingEvent.audio_play_event.set()
                        elif action.action_type == ActionType.DISPLAY:
                            # 实现显示停止逻辑
                            pass
                        elif action.action_type == ActionType.SPRAY:
                            self.spray.stop()
                
                logging.info(f"已发送停止信号到任务: ID={task_id}")
                return True
            return False

    def get_running_tasks(self) -> List[Task]:
        """获取当前正在运行的任务列表"""
        with self.thread_lock:
            return list(self.running_tasks.values())

    def enable_task(self, task_id: int) -> bool:
        """启用任务
        
        Args:
            task_id: 任务ID
            
        Returns:
            bool: 是否成功启用任务
        """
        with self.lock:
            tasks, next_id = self._load_tasks()
            if task_id not in tasks:
                logging.warning(f"启用任务失败: ID={task_id} 不存在")
                return False
                
            task = tasks[task_id]
            if task.is_enabled:
                logging.info(f"任务已经是启用状态: ID={task_id}")
                return True
                
            task.is_enabled = True
            task.status = TaskStatus.PENDING
            # 更新下次执行时间
            if task.execution_time:
                task.next_run_time = self._calculate_next_run_time(task)
                
            tasks[task_id] = task
            self._save_tasks(tasks, next_id)
            logging.info(f"任务启用成功: ID={task_id}, 名称={task.name}")
            return True

    def disable_task(self, task_id: int) -> bool:
        """禁用任务
        
        Args:
            task_id: 任务ID
            
        Returns:
            bool: 是否成功禁用任务
        """
        with self.lock:
            tasks, next_id = self._load_tasks()
            if task_id not in tasks:
                logging.warning(f"禁用任务失败: ID={task_id} 不存在")
                return False
                
            task = tasks[task_id]
            if not task.is_enabled:
                logging.info(f"任务已经是禁用状态: ID={task_id}")
                return True
                
            task.is_enabled = False
            task.status = TaskStatus.DISABLED
            tasks[task_id] = task
            self._save_tasks(tasks, next_id)
            logging.info(f"任务禁用成功: ID={task_id}, 名称={task.name}")
            return True

    def get_task_status(self, task_id: int) -> Optional[dict]:
        """获取任务状态信息
        
        Args:
            task_id: 任务ID
            
        Returns:
            Optional[dict]: 任务状态信息字典，如果任务不存在则返回None
        """
        with self.lock:
            tasks, _ = self._load_tasks()
            if task_id not in tasks:
                logging.warning(f"获取任务状态失败: ID={task_id} 不存在")
                return None
                
            task = tasks[task_id]
            status = {
                "id": task.id,
                "name": task.name,
                "type": task.task_type,
                "status": task.status,
                "is_enabled": task.is_enabled,
                "execution_time": task.execution_time,
                "next_run_time": task.next_run_time,
                "created_at": task.created_at,
                "last_run_time": task.last_run_time,
                "last_run_result": task.last_run_result,
                "schedule_type": task.schedule_type,
                "weekdays": task.weekdays,
                "duration": task.duration
            }
            
            # 根据任务类型添加特定信息
            if task.task_type == TaskType.ALARM:
                status["actions"] = task.actions
            elif task.task_type == TaskType.SYSTEM:
                status["content"] = task.content
                
            logging.debug(f"获取任务状态成功: ID={task_id}, 名称={task.name}")
            return status

    def get_all_tasks_status(self) -> List[dict]:
        """获取所有任务的状态信息
        
        Returns:
            List[dict]: 包含所有任务状态信息的字典列表
        """
        with self.lock:
            tasks, _ = self._load_tasks()
            status_list = []
            
            for task in tasks.values():
                status = {
                    "id": task.id,
                    "name": task.name,
                    "type": task.task_type,
                    "status": task.status,
                    "is_enabled": task.is_enabled,
                    "execution_time": task.execution_time,
                    "next_run_time": task.next_run_time,
                    "created_at": task.created_at,
                    "last_run_time": task.last_run_time,
                    "last_run_result": task.last_run_result,
                    "schedule_type": task.schedule_type,
                    "weekdays": task.weekdays,
                    "duration": task.duration
                }
                
                # 根据任务类型添加特定信息
                if task.task_type == TaskType.ALARM:
                    status["actions"] = task.actions
                elif task.task_type == TaskType.SYSTEM:
                    status["content"] = task.content
                    
                status_list.append(status)
                
            # 按创建时间排序
            status_list.sort(key=lambda x: x["created_at"])
            
            logging.debug(f"获取所有任务状态信息，共 {len(status_list)} 个任务")
            return status_list

    def create_combined_task_example(self) -> Task:
        """创建一个5分钟后执行的组合任务示例
        
        这个示例将同时执行：
        1. 灯光效果：呼吸模式
        2. 声音播放：播放指定音频文件
        3. 屏幕显示：显示动画效果
        
        Returns:
            Task: 创建的任务对象
        """
        # 计算5分钟后的时间
        now = datetime.now()
        execution_time = (now + timedelta(minutes=5)).time()
        
        # 创建各种动作
        light_action = TaskAction.create_light_action(
            mode="breath",
            params={
                "color": "#FF0000",
                "speed": 2
            }
        )
        
        sound_action = TaskAction.create_sound_action(
            file_path="/path/to/your/music.mp3",
            volume=80
        )
        
        display_action = TaskAction.create_screen_action(
            mode="animation",
            params={
                "animation_type": "welcome",
                "duration": 30
            }
        )
        
        # 将所有动作组合在一起
        actions = [light_action, sound_action, display_action]
        
        # 创建任务
        task = Task.create(
            name="5分钟后的组合任务",
            task_type=TaskType.ALARM,
            schedule_type=TaskScheduleType.ONCE,
            execution_time=execution_time.isoformat(),
            duration=30,  # 任务持续30秒
            actions=json.dumps(actions)
        )
        
        # 添加到调度器
        return self.add_task(task)

class TaskDaemon:
    def __init__(self, storage_file: str, audioPlayerIns, lightIns, sprayIns):
        self.scheduler = TaskScheduler(storage_file, audioPlayerIns, lightIns, sprayIns)
        self.running = False
        
    def start(self):
        """启动守护进程"""
        if self.running:
            return
            
        # 设置信号处理
        # signal.signal(signal.SIGTERM, self._handle_signal)
        # signal.signal(signal.SIGINT, self._handle_signal)
        
        self.running = True
        logging.info("Task daemon started")
        
        try:
            # 启动调度器
            self.scheduler.start()
            
            # 保持进程运行
            while self.running:
                signal.pause()
                
        except Exception as e:
            logging.error(f"Daemon error: {str(e)}")
            self.stop()
            
    def stop(self):
        """停止守护进程"""
        if not self.running:
            return
            
        self.running = False
        self.scheduler.stop()
        logging.info("Task daemon stopped")
        
    def _handle_signal(self, signum, frame):
        """处理信号"""
        logging.info(f"Received signal {signum}")
        self.stop()
        sys.exit(0)
        
    def _is_duplicate_task(self, task_type: TaskType, schedule_type: TaskScheduleType, 
                          execution_time: str, weekdays: str, actions: str) -> Optional[Task]:
        """检查是否存在完全相同的任务"""
        tasks, _ = self.scheduler._load_tasks()
        for task in tasks.values():
            if (task.task_type == task_type and
                task.schedule_type == schedule_type and
                task.execution_time == execution_time and
                task.weekdays == weekdays and
                task.actions == actions):
                return task
        return None

    def create_alarm_task(self, name: str, execution_time: time, parameters: dict, duration: int, weekdays: list = None) -> Task:
        """创建闹钟任务"""
        # 检查是否存在完全相同的任务
        schedule_type = TaskScheduleType.WEEKLY if weekdays else TaskScheduleType.ONCE
        execution_time_str = execution_time.isoformat()
        weekdays_str = json.dumps(weekdays) if weekdays else None
        actions_str = json.dumps(parameters)

        existing_task = self._is_duplicate_task(
            TaskType.ALARM,
            schedule_type,
            execution_time_str,
            weekdays_str,
            actions_str
        )

        if existing_task:
            # 如果任务存在但被禁用，则启用它
            if not existing_task.is_enabled:
                existing_task.is_enabled = True
                existing_task.status = TaskStatus.PENDING
                # 更新下次执行时间
                existing_task.next_run_time = self._calculate_initial_run_time(
                    time.fromisoformat(existing_task.execution_time),
                    json.loads(existing_task.weekdays) if existing_task.weekdays else None
                ).isoformat()
                # 保存更新后的任务
                tasks, next_id = self.scheduler._load_tasks()
                tasks[existing_task.id] = existing_task
                self.scheduler._save_tasks(tasks, next_id)
                logging.info(f"启用已存在的任务: ID={existing_task.id}, 名称={existing_task.name}")
            else:
                logging.info(f"任务已存在且处于启用状态: ID={existing_task.id}, 名称={existing_task.name}")
            return existing_task

        # 如果不存在相同任务，则创建新任务
        task = Task.create(
            name=name,
            task_type=TaskType.ALARM,
            schedule_type=schedule_type,
            execution_time=execution_time_str,
            weekdays=weekdays_str,
            duration=duration,
            actions=actions_str,
            next_run_time=self._calculate_initial_run_time(execution_time, weekdays).isoformat()
        )
        return self.scheduler.add_task(task)
        
    def create_system_task(self, name: str, content: dict, schedule_type: TaskScheduleType,
                          execution_time: time = None, weekdays: list = None, duration: int = None) -> Task:
        """创建系统任务"""
        # 检查是否存在完全相同的任务
        execution_time_str = execution_time.isoformat() if execution_time else None
        weekdays_str = json.dumps(weekdays) if weekdays else None
        content_str = json.dumps(content)

        existing_task = self._is_duplicate_task(
            TaskType.SYSTEM,
            schedule_type,
            execution_time_str,
            weekdays_str,
            content_str
        )

        if existing_task:
            # 如果任务存在但被禁用，则启用它
            if not existing_task.is_enabled:
                existing_task.is_enabled = True
                existing_task.status = TaskStatus.PENDING
                # 更新下次执行时间
                if execution_time:
                    existing_task.next_run_time = self._calculate_initial_run_time(
                        time.fromisoformat(existing_task.execution_time),
                        json.loads(existing_task.weekdays) if existing_task.weekdays else None
                    ).isoformat()
                # 保存更新后的任务
                tasks, next_id = self.scheduler._load_tasks()
                tasks[existing_task.id] = existing_task
                self.scheduler._save_tasks(tasks, next_id)
                logging.info(f"启用已存在的任务: ID={existing_task.id}, 名称={existing_task.name}")
            else:
                logging.info(f"任务已存在且处于启用状态: ID={existing_task.id}, 名称={existing_task.name}")
            return existing_task

        # 如果不存在相同任务，则创建新任务
        task = Task.create(
            name=name,
            task_type=TaskType.SYSTEM,
            schedule_type=schedule_type,
            execution_time=execution_time_str,
            weekdays=weekdays_str,
            duration=duration,
            content=content_str,
            next_run_time=self._calculate_initial_run_time(execution_time, weekdays).isoformat() if execution_time else None
        )
        return self.scheduler.add_task(task)
        
    def _calculate_initial_run_time(self, execution_time: time, weekdays: list = None) -> datetime:
        """计算初始执行时间"""
        now = datetime.now()
        if weekdays:
            current_weekday = now.weekday() + 1
            next_weekday = None
            for day in sorted(weekdays):
                if day == current_weekday and execution_time > now.time():
                    next_weekday = day
                    break
                if day > current_weekday:
                    next_weekday = day
                    break
            if next_weekday is None:
                next_weekday = min(weekdays)
                days_ahead = 7 - current_weekday + next_weekday
            else:
                days_ahead = next_weekday - current_weekday
                
            next_time = datetime.combine(now.date(), execution_time)
            next_time += timedelta(days=days_ahead)
            return next_time
        else:
            next_time = datetime.combine(now.date(), execution_time)
            if next_time <= now:
                next_time += timedelta(days=1)
            return next_time

    def enable_task(self, task_id: int) -> bool:
        """启用任务"""
        return self.scheduler.enable_task(task_id)

    def disable_task(self, task_id: int) -> bool:
        """禁用任务"""
        return self.scheduler.disable_task(task_id)

    def get_task_status(self, task_id: int) -> Optional[dict]:
        """获取任务状态信息"""
        return self.scheduler.get_task_status(task_id)

    def get_all_tasks_status(self) -> List[dict]:
        """获取所有任务的状态信息"""
        return self.scheduler.get_all_tasks_status()

    def update_task(self, task_id: int, **kwargs) -> Optional[Task]:
        """更新任务数据
        
        Args:
            task_id: 任务ID
            **kwargs: 要更新的字段，可以包括：
                - name: 任务名称
                - execution_time: 执行时间
                - weekdays: 执行星期
                - duration: 持续时间
                - parameters: 任务参数
                - content: 任务内容（系统任务）
        
        Returns:
            更新后的任务对象，如果任务不存在则返回None
        """
        tasks, next_id = self.scheduler._load_tasks()
        if task_id not in tasks:
            logging.warning(f"更新任务失败: ID={task_id} 不存在")
            return None
            
        task = tasks[task_id]
        
        # 更新任务字段
        if 'name' in kwargs:
            task.name = kwargs['name']
        if 'execution_time' in kwargs:
            task.execution_time = kwargs['execution_time'].isoformat()
        if 'weekdays' in kwargs:
            task.weekdays = json.dumps(kwargs['weekdays']) if kwargs['weekdays'] else None
        if 'duration' in kwargs:
            task.duration = kwargs['duration']
        if 'parameters' in kwargs and task.task_type == TaskType.ALARM:
            task.actions = json.dumps(kwargs['parameters'])
        if 'content' in kwargs and task.task_type == TaskType.SYSTEM:
            task.content = json.dumps(kwargs['content'])
            
        # 更新下次执行时间
        if 'execution_time' in kwargs or 'weekdays' in kwargs:
            task.next_run_time = self._calculate_initial_run_time(
                time.fromisoformat(task.execution_time),
                json.loads(task.weekdays) if task.weekdays else None
            ).isoformat()
            
        # 保存更新后的任务
        tasks[task_id] = task
        self.scheduler._save_tasks(tasks, next_id)
        
        logging.info(f"任务更新成功: ID={task_id}, 名称={task.name}")
        return task

    def toggle_task(self, task_id: int, enable: bool = None) -> Optional[Task]:
        """切换任务的启用状态
        
        Args:
            task_id: 任务ID
            enable: 是否启用，如果为None则切换当前状态
        
        Returns:
            更新后的任务对象，如果任务不存在则返回None
        """
        tasks, next_id = self.scheduler._load_tasks()
        if task_id not in tasks:
            logging.warning(f"切换任务状态失败: ID={task_id} 不存在")
            return None
            
        task = tasks[task_id]
        
        # 如果enable为None，则切换当前状态
        if enable is None:
            enable = not task.is_enabled
            
        # 更新任务状态
        task.is_enabled = enable
        task.status = TaskStatus.PENDING if enable else TaskStatus.DISABLED
        
        # 如果启用任务，更新下次执行时间
        if enable:
            task.next_run_time = self._calculate_initial_run_time(
                time.fromisoformat(task.execution_time),
                json.loads(task.weekdays) if task.weekdays else None
            ).isoformat()
            
        # 保存更新后的任务
        tasks[task_id] = task
        self.scheduler._save_tasks(tasks, next_id)
        
        status = "启用" if enable else "禁用"
        logging.info(f"任务{status}成功: ID={task_id}, 名称={task.name}")
        return task

    def get_tasks(self, task_type: Optional[TaskType] = None) -> List[Task]:
        """获取任务列表
        
        Args:
            task_type: 任务类型，可选值：
                - None: 获取所有任务
                - TaskType.ALARM: 只获取闹钟任务
                - TaskType.SYSTEM: 只获取系统任务
        
        Returns:
            任务列表
        """
        tasks, _ = self.scheduler._load_tasks()
        
        if task_type is None:
            # 获取所有任务
            task_list = list(tasks.values())
            logging.debug(f"获取所有任务，共 {len(task_list)} 个")
        else:
            # 根据类型筛选任务
            task_list = [task for task in tasks.values() if task.task_type == task_type]
            type_name = "闹钟" if task_type == TaskType.ALARM else "系统"
            logging.debug(f"获取{type_name}任务，共 {len(task_list)} 个")
            
        # 按创建时间排序
        task_list.sort(key=lambda x: x.created_at)
        
        # 记录每个任务的详细信息
        for task in task_list:
            logging.debug(
                f"任务详情: ID={task.id}, 名称={task.name}, "
                f"类型={task.task_type}, 状态={task.status}, "
                f"启用状态={'启用' if task.is_enabled else '禁用'}, "
                f"执行时间={task.execution_time}, "
                f"下次执行={task.next_run_time}"
            )
            
        return task_list

    def get_alarm_tasks(self) -> List[Task]:
        """获取所有闹钟任务"""
        return self.get_tasks(TaskType.ALARM)

    def get_system_tasks(self) -> List[Task]:
        """获取所有系统任务"""
        return self.get_tasks(TaskType.SYSTEM)

