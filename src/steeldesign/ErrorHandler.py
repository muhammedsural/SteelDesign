
class DefaultError(Exception):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)

class ShapeError(Exception):
    """"""
    def __init__(self, future_index: int, target_index: int, message: str) -> None:
        self.first_shape = future_index
        self.second_shape = target_index
        self.message = message
        super().__init__(message)
