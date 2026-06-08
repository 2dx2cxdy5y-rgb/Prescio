from enum import Enum


class DataType(str, Enum):

    STRING = "string"

    INTEGER = "integer"

    FLOAT = "float"

    BOOLEAN = "boolean"

    DATE = "date"

    DATETIME = "datetime"