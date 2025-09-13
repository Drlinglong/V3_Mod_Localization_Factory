"""简单的状态管理器，用于跨回调传递重启命令"""
class StateManager:
    """维护需要执行的命令"""
    def __init__(self):
        self.command = None

    def set_command(self, cmd: str):
        self.command = cmd

    def get_command(self):
        return self.command

    def clear(self):
        self.command = None
