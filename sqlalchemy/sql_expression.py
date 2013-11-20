"""
SQLAlchemy Tutorial
- http://docs.sqlalchemy.org/en/rel_0_8/core/tutorial.html
"""

from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey
from sqlalchemy import create_engine
from sqlalchemy.sql import select, and_, or_, not_
from sqlalchemy.sql import bindparam, func

engine = create_engine('sqlite:///:memory:', echo=True)

metadata = MetaData()
users = Table(
    'users', metadata,
    Column('id', Integer, primary_key=True),
    Column('name', String),
    Column('fullname', String)
)

addresses = Table(
    'addresses', metadata,
    Column('id', Integer, primary_key=True),
    Column('user_id', None, ForeignKey('users.id')),
    Column('email_address', String, nullable=False)
)

metadata.create_all(engine)

conn = engine.connect()

conn.execute(users.insert().values(name='jack', fullname='Jack Jones'))
conn.execute(users.insert(), id=2, name='wendy', fullname='Wendy Williams')

conn.execute(addresses.insert(), [
    {'user_id': 1, 'email_address': 'jack@yahoo.com'},
    {'user_id': 1, 'email_address': 'jack@msn.com'},
    {'user_id': 2, 'email_address': 'www@www.org'},
    {'user_id': 2, 'email_address': 'wendy@aol.com'}
])
