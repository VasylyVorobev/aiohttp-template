import os
from gino import Gino

db = Gino()


async def setup_db(app):
    await db.set_bind(os.environ.get("PG_URL"))
    print("connect to database")


async def close_db(app):
    await db.pop_bind().close()
    print("disconnect")
