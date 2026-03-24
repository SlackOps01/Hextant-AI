from redis.asyncio import Redis

REVOKED_TOKEN_PREFIX = "revoked:"


async def revoke_tokens(redis: Redis, jti: str, exp: int):
    await redis.set(
        f"{REVOKED_TOKEN_PREFIX}:{jti}",
        "1",
        ex=exp,
    )

async def is_token_revoked(redis: Redis, jti: str) -> bool:
    return await redis.exists(
        f"{REVOKED_TOKEN_PREFIX}:{jti}"
    ) > 0