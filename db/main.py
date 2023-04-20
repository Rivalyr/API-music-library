import motor.motor_asyncio


client = motor.motor_asyncio.AsyncIOMotorClient(
    "Mongo Atlas connection info on Base64 encoded")

db = client["musicSuggestions"]