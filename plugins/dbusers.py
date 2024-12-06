import motor.motor_asyncio, datetime
from config import DB_NAME, DB_URI
from datetime import datetime, timedelta

DATABASE_NAME = DB_NAME
DATABASE_URI = DB_URI


class Database:
    
    def __init__(self, uri, database_name):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.db = self._client[database_name]
        self.col = self.db.users
        self.grp = self.db.groups

    def new_user(self, id, name):
        return dict(
            id=id,
            name=name,
            is_authorized=False,  # Default to unauthorized
            ban_status=dict(
                is_banned=False,
                ban_reason="",
            ),
        )

    def new_group(self, id, title):
        return dict(
            id=id,
            title=title,
            chat_status=dict(
                is_disabled=False,
                reason="",
            ),
        )

    async def add_user(self, id, name):
        user = self.new_user(id, name)
        await self.col.insert_one(user)

    async def is_user_exist(self, id):
        user = await self.col.find_one({'id': int(id)})
        return bool(user)

    async def authorize_user(self, id, duration_days=7):
        expiry_time = datetime.utcnow() + timedelta(days=duration_days)
        await self.col.update_one(
            {'id': int(id)},
            {
                '$set': {
                    'is_authorized': True,
                    'auth_timestamp': datetime.utcnow(),
                    'auth_expiry': expiry_time  # Set authorization expiry
                }
            }
        )

    async def unauthorize_user(self, id):
        await self.col.update_one(
            {'id': int(id)},
            {
                '$set': {
                    'is_authorized': False,
                    'auth_expiry': None,  # Clear expiry time
                    'auth_timestamp': None
                }
            }
        )

    async def is_user_authorized(self, id):
        user = await self.col.find_one({'id': int(id)})
        if user and user.get("is_authorized", False):
            auth_expiry = user.get("auth_expiry")
            if auth_expiry and datetime.utcnow() > auth_expiry:
                # Auto unauthorize if expired
                await self.unauthorize_user(id)
                return False
            return True
        return False

    async def total_users_count(self):
        count = await self.col.count_documents({})
        return count

    async def get_all_users(self):
        return self.col.find({})

    async def delete_user(self, user_id):
        await self.col.delete_many({'id': int(user_id)})


db = Database(DATABASE_URI, DATABASE_NAME)
