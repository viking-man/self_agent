class ParameterException(Exception):
    def __init__(self, parameter_name, message="Invalid parameter"):
        self.parameter_name = parameter_name
        self.message = f'{message}->{parameter_name}'
        super().__init__()


class BizException(Exception):
    def __init__(self, message="Business exception"):
        self.message = message
        super().__init__()
