import click

class EnumType(click.Choice):
    def __init__(self, enum):
        self.__enum = enum
        super().__init__(enum.__members__)

    def convert(self, value, param, ctx):
        return self.__enum[super().convert(value, param, ctx)]