import time

class PIDController:
    def __init__(self, Kp, Ki, Kd,integral_limit=None):
        self.Kp = Kp  # 比例增益
        self.Ki = Ki  # 积分增益
        self.Kd = Kd  # 微分增益
        self.prev_error = 0
        self.integral = 0
        self.integral_limit = integral_limit  # 设置积分上限
        self.last_time = time.time()

    def update(self, error):
        # 计算时间差
        current_time = time.time()
        delta_time = current_time - self.last_time
        self.last_time = current_time

        # 计算积分部分
        self.integral += error * delta_time

        if self.integral_limit is not None:
            self.integral = max(min(self.integral, self.integral_limit), -self.integral_limit)

        # 计算微分部分
        derivative = (error - self.prev_error) / delta_time if delta_time > 0 else 0

        # PID输出: 这里的输出是舵机的“速度”调整量
        output = self.Kp * error + self.Ki * self.integral + self.Kd * derivative

        # 保存当前误差
        self.prev_error = error

        return output