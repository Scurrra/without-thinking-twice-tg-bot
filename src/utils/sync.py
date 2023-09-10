def make_async(x):
    async def wrapper():
        return x
    return wrapper