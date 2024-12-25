
import motor.motor_asyncio
from config import DB_NAME, DB_URI

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
            id = id,
            name = name,
            ban_status=dict(
                is_banned=False,
                ban_reason="",
            ),
        )

    def new_group(self, id, title):
        return dict(
            id = id,
            title = title,
            chat_status=dict(
                is_disabled=False,
                reason="",
            ),
        )

    
    async def add_user(self, id, name):
        user = self.new_user(id, name)
        await self.col.insert_one(user)

    
    async def is_user_exist(self, id):
        user = await self.col.find_one({'id':int(id)})
        return bool(user)


    async def total_users_count(self):
        count = await self.col.count_documents({})
        return count

    
    async def get_all_users(self):
        return self.col.find({})



    async def delete_user(self, user_id):
        await self.col.delete_many({'id': int(user_id)})


# Add these methods to Database class

    async def set_caption(self, user_id, caption):
        """Set a custom caption for a user."""
        await self.col.update_one(
            {'id': int(user_id)},
            {'$set': {'custom_caption': caption}},
            upsert=True
        )

    async def get_caption(self, user_id):
        """Get the custom caption for a user."""
        user = await self.col.find_one({'id': int(user_id)})
        return user.get('custom_caption') if user else None

    async def delete_caption(self, user_id):
        """Delete the custom caption for a user."""
        await self.col.update_one(
            {'id': int(user_id)},
            {'$unset': {'custom_caption': ""}}
        )



db = Database(DATABASE_URI, DATABASE_NAME)
