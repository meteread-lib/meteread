from processor import AbstractProcessor


class NoneProcessor(AbstractProcessor):
    def __call__(self, data) -> None:
        return None