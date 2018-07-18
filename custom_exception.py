class BalanceParenthesesException(Exception):
    def __init__(self, msg):
        self.message = msg

class OperatorException(Exception):
    def __init__(self, msg):
        self.message = msg

class NegativeWindowSizException(Exception):
    def __init__(self, msg):
        self.message = msg

class WindowTooSmallException(Exception):
    def __init__(self, msg):
        self.message = msg

class HasParenthesesException(Exception):
    def __init__(self, msg):
        self.message = msg