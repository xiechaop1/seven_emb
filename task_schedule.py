from datetime import time
from model.scheduler import TaskDaemon
import threading
import signal
import sys
import time as time_module

def main():
    # 创建任务守护进程实例
    task_daemon = TaskDaemon("tasks.json")
    
    # 创建闹钟任务
    alarm_time = time(20, 39)  # 每天晚上20:39
    weekdays = None  # 单次执行
    alarm_task = task_daemon.create_alarm_task("Evening Alarm", alarm_time, weekdays)
    
    # 创建并启动守护进程线程
    daemon_thread = threading.Thread(target=task_daemon.start)
    daemon_thread.daemon = True  # 设置为守护线程
    daemon_thread.start()
    
    # 信号处理函数
    def signal_handler(sig, frame):
        print("\n正在优雅退出...")
        task_daemon.stop()  # 停止任务守护进程
        sys.exit(0)
    
    # 注册信号处理器
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    print("任务调度器已启动，按 Ctrl+C 退出...")
    
    try:
        # 主线程保持运行
        while True:
            time_module.sleep(1)
    except KeyboardInterrupt:
        signal_handler(signal.SIGINT, None)

if __name__ == "__main__":
    main()

# # 创建系统任务
# system_task = daemon.create_system_task(
#     name="Daily Backup",
#     content={"type": "backup", "target": "/data"},
#     schedule_type=TaskScheduleType.DAILY,
#     execution_time=time(2, 0)  # 每天凌晨2点
# )

# 启动守护进程
# daemon.start()