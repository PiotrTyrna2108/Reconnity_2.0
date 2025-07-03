import os
from arq.connections import RedisSettings

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")

def parse_redis_url(url: str):
    """Parse Redis URL into components for ARQ RedisSettings"""
    if url.startswith("redis://"):
        url = url[len("redis://"):]
    
    host_port, *rest = url.split("/")
    if ":" in host_port:
        host, port = host_port.split(":")
        port = int(port)
    else:
        host = host_port
        port = 6379
        
    db = int(rest[0]) if rest else 0
    
    return RedisSettings(
        host=host,
        port=port,
        database=db
    )

# Redis settings for ARQ
redis_settings = parse_redis_url(REDIS_URL)
