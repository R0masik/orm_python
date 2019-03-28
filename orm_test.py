"""ORM"""

import sqlite3


class SQLiteDB:
    def __init__(self, db):
        self.database = db
        self.conn = sqlite3.connect(self.database)
        self.cursor = self.conn.cursor()

    def create_table(self, table_name, fields_dict):
        table_fields = ', '.join([f'"{field}" {value_type.get_db_type()}' for field, value_type in fields_dict.items()])
        query = f'create table "{table_name}" ({table_fields})'
        self.cursor.execute(query)

    def insert(self, table_name, values_list):
        values = ', '.join([f'"{value}"' for value in values_list])
        query = f'insert into "{table_name}" values ({values})'
        self.cursor.execute(query)
        self.conn.commit()

    def update(self):
        pass

    def delete(self):
        pass


# region Fields
class Field:
    db_type = {
        int: 'integer',
        str: 'text',
        float: 'real'
    }

    def __init__(self, f_type, required=True, default=None):
        self.f_type = f_type
        self.required = required
        self.default = default

    def validate(self, value):
        if value is None and self.required:
            return None
        return self.f_type(value)

    def get_db_type(self):
        return self.db_type[self.f_type]


class IntField(Field):
    def __init__(self, required=True, default=None):
        super().__init__(int, required, default)


class StrField(Field):
    def __init__(self, required=True, default=None):
        super().__init__(str, required, default)


class FloatField(Field):
    def __init__(self, required=True, default=None):
        super().__init__(float, required, default)


# endregion

class ModelMeta(type):
    def __new__(mcs, name, bases, namespace):
        if name == 'Model':
            return super().__new__(mcs, name, bases, namespace)

        meta = namespace.get('Meta')
        if meta is None:
            raise ValueError('meta is none')
        if not hasattr(meta, 'database'):
            raise ValueError('database is empty')
        if not hasattr(meta, 'table_name'):
            raise ValueError('table_name is empty')

        # todo: mro

        fields = {k: v for k, v in namespace.items() if isinstance(v, Field)}
        namespace['_fields'] = fields
        namespace['_table_name'] = meta.table_name
        return super().__new__(mcs, name, bases, namespace)


class Manage:
    def __init__(self):
        self.model_cls = None

    def __get__(self, instance, owner):
        if self.model_cls is None:
            self.model_cls = owner
        return self

    def create(self):
        print(self.model_cls)

    def update(self):
        pass

    def delete(self):
        pass

    def filter(self):
        pass


class Model(metaclass=ModelMeta):
    class Meta:
        database = None
        table_name = None

    objects = Manage()

    # todo DoesNotExist

    def __init__(self, *args, **kwargs):
        for field, val in self._fields.items():
            valid_val = val.validate(kwargs.get(field))
            setattr(self, field, valid_val)

    @classmethod
    def create_table(cls):
        db = cls.Meta.database
        table = cls.Meta.table_name
        if db and table:
            db.create_table(table, cls._fields)


if __name__ == '__main__':
    db_path = r'd:\Program Files\DB Browser for SQLite\databases\test.db'
    db = SQLiteDB(db_path)


    class User(Model):
        id = IntField()
        name = StrField()

        class Meta:
            database = db
            table_name = 'User'


    User.create_table()

# user = User()
# User.objects.create(id=1, name='name')
# User.objects.update(id=1)
# User.objects.delete(id=1)
#
# User.objects.filter(id=2).filter(name='kek')
#
# user.name = '2'
# user.save()
