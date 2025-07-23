import asyncio
from sqlmodel.ext.asyncio.session import AsyncSession
from app.core.db import engine, init_db


async def main():
    async with AsyncSession(engine) as session:
        await init_db(session)

if __name__ == '__main__':
    asyncio.run(main())