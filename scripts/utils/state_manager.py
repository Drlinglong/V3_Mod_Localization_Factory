"""简单的状态管理器，用于跨回调传递重启命令"""

import time


class StateManager:
    """维护需要执行的命令"""

    def __init__(self):
        self.command = None

    def set_command(self, cmd: str):
        self.command = cmd

    def get_command(self):
        return self.command

    def wait_for_command(self, timeout: float = 5.0):
        """阻塞等待命令直到超时

        Args:
            timeout: 超时时间（秒）
        Returns:
            获取到的命令字符串，若在超时时间内未收到命令则返回 None
        """
        start = time.time()
        while self.command is None:
            if timeout is not None and time.time() - start > timeout:
                return None
            time.sleep(0.1)
        return self.command

    def clear(self):
        self.command = None
