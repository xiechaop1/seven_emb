import logging
from datetime import datetime, time, timedelta
from typing import Optional, List, Dict
import json
import threading
import time as time_module
import os
from .task import Task, TaskStatus, TaskScheduleType, TaskType
import signal
import sys

# 配置日志格式
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

class TaskScheduler:
    def __init__(self, storage_file: str):
        self.storage_file = storage_file
        self.tasks: Dict[int, Task] = {}
        self.next_id = 1
        self.running = False
        self.thread = None
        self.lock = threading.Lock()
        logging.info(f"初始化任务调度器，存储文件: {storage_file}")
        self._load_tasks()
        
    def _load_tasks(self):
        """从文件加载任务"""
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.tasks = {int(k): Task.from_dict(v) for k, v in data.get('tasks', {}).items()}
                    self.next_id = data.get('next_id', 1)
                logging.info(f"成功从文件加载 {len(self.tasks)} 个任务")
                for task_id, task in self.tasks.items():
                    logging.debug(f"加载任务: ID={task_id}, 名称={task.name}, 类型={task.task_type}, "
                                f"状态={task.status}, 下次执行时间={task.next_run_time}")
            except Exception as e:
                logging.error(f"加载任务文件失败: {str(e)}")
                self.tasks = {}
                self.next_id = 1
        else:
            logging.info("任务文件不存在，创建新的任务列表")
                
    def _save_tasks(self):
        """保存任务到文件"""
        try:
            data = {
                'tasks': {str(k): v.to_dict() for k, v in self.tasks.items()},
                'next_id': self.next_id
            }
            with open(self.storage_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logging.debug(f"成功保存 {len(self.tasks)} 个任务到文件")
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
        if self.thread:
            self.thread.join()
        self._save_tasks()
        logging.info("任务调度器已停止")
            
    def _scheduler_loop(self):
        """调度器主循环"""
        logging.info("开始调度器主循环")
        while self.running:
            try:
                self._check_and_execute_tasks()
                time_module.sleep(1)
            except Exception as e:
                logging.error(f"调度器主循环发生错误: {str(e)}")
                
    def _check_and_execute_tasks(self):
        """检查并执行到期的任务"""
        with self.lock:
            now = datetime.now()
            # 查找所有待执行的任务，增加时间检查
            tasks_to_execute = [
                task for task in self.tasks.values()
                if task.status == TaskStatus.PENDING and 
                task.is_enabled and  # 只执行启用状态的任务
                datetime.fromisoformat(task.next_run_time) <= now and
                # 只执行未超过1分钟的任务
                (now - datetime.fromisoformat(task.next_run_time)).total_seconds() <= 60
            ]
            
            if tasks_to_execute:
                logging.info(f"发现 {len(tasks_to_execute)} 个待执行任务")
                for task in tasks_to_execute:
                    logging.info(f"准备执行任务: ID={task.id}, 名称={task.name}, "
                               f"类型={task.task_type}, 计划执行时间={task.next_run_time}")
                    self._execute_task(task)
            else:
                # 显示下一个要执行的任务
                next_tasks = sorted(
                    [(task, datetime.fromisoformat(task.next_run_time)) 
                     for task in self.tasks.values() 
                     if task.status == TaskStatus.PENDING and task.is_enabled],
                    key=lambda x: x[1]
                )
                if next_tasks:
                    next_task, next_time = next_tasks[0]
                    # 检查是否有过期未执行的任务
                    if (now - next_time).total_seconds() > 60:
                        logging.warning(f"任务已过期未执行: ID={next_task.id}, 名称={next_task.name}, "
                                      f"计划执行时间={next_time.isoformat()}, "
                                      f"已过期 {(now - next_time).total_seconds()/60:.1f} 分钟")
                        # 如果是单次任务，直接禁用
                        if next_task.schedule_type == TaskScheduleType.ONCE:
                            next_task.is_enabled = False
                            self._save_tasks()
                            logging.info(f"单次任务已过期，已禁用: ID={next_task.id}, 名称={next_task.name}")
                    else:
                        logging.debug(f"下一个待执行任务: ID={next_task.id}, 名称={next_task.name}, "
                                    f"计划执行时间={next_time.isoformat()}")
                
    def _execute_task(self, task: Task):
        """执行任务"""
        logging.info(f"开始执行任务: ID={task.id}, 名称={task.name}")
        try:
            # 更新任务状态为执行中
            task.status = TaskStatus.RUNNING
            task.last_run_time = datetime.now().isoformat()
            self._save_tasks()
            logging.debug(f"任务状态已更新为执行中: ID={task.id}")
            
            # 执行任务
            result = self._run_task(task)
            logging.info(f"任务执行完成: ID={task.id}, 结果={result}")
            
            # 更新任务状态和结果
            task.last_run_result = json.dumps(result)
            task.status = TaskStatus.COMPLETED if result.get("success") else TaskStatus.FAILED
            
            # 如果是单次任务，执行完成后禁用
            if task.schedule_type == TaskScheduleType.ONCE:
                task.is_enabled = False
                logging.info(f"单次任务执行完成，已禁用: ID={task.id}, 名称={task.name}")
            else:
                # 计算下次执行时间
                self._calculate_next_run_time(task)
                logging.debug(f"任务下次执行时间已更新: ID={task.id}, 时间={task.next_run_time}")
            
            self._save_tasks()
            
        except Exception as e:
            logging.error(f"任务执行失败: ID={task.id}, 错误={str(e)}")
            task.status = TaskStatus.FAILED
            task.last_run_result = json.dumps({
                "success": False,
                "error": str(e)
            })
            self._save_tasks()
            
    def _run_task(self, task: Task) -> dict:
        """运行具体任务"""
        # 这里需要根据task_type和content来实现具体的任务执行逻辑
        return {
            "success": True,
            "message": "Task executed successfully"
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
            task.id = self.next_id
            self.next_id += 1
            self.tasks[task.id] = task
            self._save_tasks()
            logging.info(f"添加新任务成功: ID={task.id}, 名称={task.name}, "
                        f"类型={task.task_type}, 计划执行时间={task.next_run_time}")
            return task
            
    def remove_task(self, task_id: int) -> bool:
        """移除任务"""
        with self.lock:
            if task_id in self.tasks:
                task = self.tasks[task_id]
                del self.tasks[task_id]
                self._save_tasks()
                logging.info(f"移除任务成功: ID={task_id}, 名称={task.name}")
                return True
            logging.warning(f"移除任务失败: ID={task_id} 不存在")
            return False
            
    def get_task(self, task_id: int) -> Optional[Task]:
        """获取任务"""
        task = self.tasks.get(task_id)
        if task:
            logging.debug(f"获取任务: ID={task_id}, 名称={task.name}, 状态={task.status}")
        else:
            logging.debug(f"获取任务失败: ID={task_id} 不存在")
        return task
        
    def get_pending_tasks(self) -> List[Task]:
        """获取所有待执行的任务"""
        pending_tasks = [task for task in self.tasks.values() if task.status == TaskStatus.PENDING]
        logging.debug(f"当前待执行任务数量: {len(pending_tasks)}")
        for task in pending_tasks:
            logging.debug(f"待执行任务: ID={task.id}, 名称={task.name}, "
                        f"计划执行时间={task.next_run_time}")
        return pending_tasks

class TaskDaemon:
    def __init__(self, storage_file: str):
        self.scheduler = TaskScheduler(storage_file)
        self.running = False
        
    def start(self):
        """启动守护进程"""
        if self.running:
            return
            
        # 设置信号处理
        signal.signal(signal.SIGTERM, self._handle_signal)
        signal.signal(signal.SIGINT, self._handle_signal)
        
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
        
    def create_alarm_task(self, name: str, execution_time: time, weekdays: list = None) -> Task:
        """创建闹钟任务"""
        task = Task.create(
            name=name,
            task_type=TaskType.ALARM,
            schedule_type=TaskScheduleType.WEEKLY if weekdays else TaskScheduleType.ONCE,
            execution_time=execution_time.isoformat(),
            weekdays=json.dumps(weekdays) if weekdays else None,
            content=json.dumps({
                "type": "alarm",
                "action": "play_sound"
            }),
            next_run_time=self._calculate_initial_run_time(execution_time, weekdays).isoformat()
        )
        return self.scheduler.add_task(task)
        
    def create_system_task(self, name: str, content: dict, schedule_type: TaskScheduleType,
                          execution_time: time = None, weekdays: list = None) -> Task:
        """创建系统任务"""
        task = Task.create(
            name=name,
            task_type=TaskType.SYSTEM,
            schedule_type=schedule_type,
            execution_time=execution_time.isoformat() if execution_time else None,
            weekdays=json.dumps(weekdays) if weekdays else None,
            content=json.dumps(content),
            next_run_time=self._calculate_initial_run_time(execution_time, weekdays).isoformat()
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

