import motor.motor_asyncio
import uuid

class MongoDB:
    _instances = {}

    def __new__(cls, uri: str, db_name: str):
        if (uri, db_name) not in cls._instances:
            instance = super().__new__(cls)
            instance.client = motor.motor_asyncio.AsyncIOMotorClient(uri)
            instance.db = instance.client[db_name]
            instance.user_data = instance.db["users"]
            instance.channel_data = instance.db["channels"]
            instance.bot_settings = instance.db["bot_settings"]
            instance.batch_data = instance.db["batch_links"]
            cls._instances[(uri, db_name)] = instance
        return cls._instances[(uri, db_name)]

    # New function to save batch links
    async def save_batch(self, file_ids: list) -> str:
        """Saves a list of file IDs and returns a unique key."""
        key = str(uuid.uuid4().hex[:8])  
        await self.batch_data.insert_one(
            {"_id": key, "ids": file_ids}
        )
        return key

    # New function to retrieve batch links
    async def get_batch(self, key: str) -> list | None:
        """Retrieves a list of file IDs by its unique key."""
        data = await self.batch_data.find_one({"_id": key})
        return data.get("ids") if data else None

    # New function to save settings
    async def save_settings(self, session_name: str, settings: dict):
        """Saves the bot's settings to the database."""
        await self.bot_settings.update_one(
            {"_id": session_name},
            {"$set": {"settings": settings}},
            upsert=True
        )

    # New function to load settings
    async def load_settings(self, session_name: str) -> dict | None:
        """Loads the bot's settings from the database."""
        data = await self.bot_settings.find_one({"_id": session_name})
        return data.get("settings") if data else None
    
    async def set_channels(self, channels: list[int]):
        await self.user_data.update_one(
            {"_id": 1},
            {"$set": {"channels": channels}},
            upsert=True
        )
    
    async def get_channels(self) -> list[int]:
        data = await self.user_data.find_one({"_id": 1})
        return data.get("channels", []) if data else []
    
    async def add_channel_user(self, channel_id: int, user_id: int):
        await self.channel_data.update_one(
            {"_id": channel_id},
            {"$addToSet": {"users": user_id}}, 
            upsert=True
        )

    async def remove_channel_user(self, channel_id: int, user_id: int):
        await self.channel_data.update_one(
            {"_id": channel_id},
            {"$pull": {"users": user_id}}
        )

    async def get_channel_users(self, channel_id: int) -> list[int]:
        doc = await self.channel_data.find_one({"_id": channel_id})
        return doc.get("users", []) if doc else []
        
    async def is_user_in_channel(self, channel_id: int, user_id: int) -> bool:
        doc = await self.channel_data.find_one(
            {"_id": channel_id, "users": {"$in": [user_id]}},
            {"_id": 1}  
        )
        return doc is not None

    async def present_user(self, user_id: int) -> bool:
        found = await self.user_data.find_one({'_id': user_id})
        return bool(found)

    async def add_user(self, user_id: int, ban: bool = False):
        await self.user_data.insert_one({'_id': user_id, 'ban': ban})

    async def full_userbase(self) -> list[int]:
        user_docs = self.user_data.find()
        return [doc['_id'] async for doc in user_docs]

    async def del_user(self, user_id: int):
        await self.user_data.delete_one({'_id': user_id})

    async def ban_user(self, user_id: int):
        await self.user_data.update_one({'_id': user_id}, {'$set': {'ban': True}})

    async def unban_user(self, user_id: int):
        await self.user_data.update_one({'_id': user_id}, {'$set': {'ban': False}})

    async def is_banned(self, user_id: int) -> bool:
        user = await self.user_data.find_one({'_id': user_id})
        return user.get('ban', False) if user else False
