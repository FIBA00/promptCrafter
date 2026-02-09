import redis.asyncio as aioredis
from core.config import settings

# we can use the redis config
token_blacklist = aioredis.from_url(settings.REDIS_URL)


async def add_jit_to_blocklist(jti: str) -> None:
    """
    Adds a JTI (JWT ID) to the Redis blacklist.

    This function marks a token (specifically its JTI) as invalid or revoked
    by storing it in Redis with an expiration time.

    Args:
        jti (str): The unique identifier of the JWT (JTI) to be blacklisted.
    """
    await token_blacklist.set(
        name=jti,
        value="true",
        ex=settings.JTI_EXPIRY_SECONDS,
    )


async def token_in_blocklist(jti: str) -> bool:
    """
    Checks if a JTI (JWT ID) is present in the Redis blacklist.

    This function queries Redis to see if the token's JTI has been stored,
    indicating that the token has been revoked.

    Args:
        jti (str): The unique identifier of the JWT (JTI) to check.

    Returns:
        bool: True if the JTI is in the blacklist, False otherwise.
    """
    jti = await token_blacklist.get(name=jti)
    return jti is not None
