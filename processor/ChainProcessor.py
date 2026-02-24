from processor import AbstractProcessor


class ChainProcessor(AbstractProcessor):
    def __init__(self, *processors: AbstractProcessor):
        super().__init__()
        self.processors = processors

    def __call__(self, data) -> None:
        for processor in self.processors:
            processor(data)
