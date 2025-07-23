from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import MetaData

# Recommended naming convention for custom types
# see: https://docs.sqlalchemy.org/en/20/orm/declarative_tables.html#declarative-table-with-mapped-column-and-explicit-type-annotations
POSTGRES_INDEXES_NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=POSTGRES_INDEXES_NAMING_CONVENTION)
