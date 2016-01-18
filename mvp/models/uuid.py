import uuid

from sqlalchemy.dialects.postgresql import UUID as pg_UUID
from sqlalchemy.types import TypeDecorator, CHAR


class UUID(TypeDecorator):
    impl = CHAR

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(pg_UUID())
        else:
            return dialect.type_descriptor(CHAR(32))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return str(value)
        else:
            if not isinstance(value, uuid.UUID):
                return "%.32x" % uuid.UUID(value)
            else:
                # hexstring
                return "%.32x" % value

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        else:
            return uuid.UUID(value)
