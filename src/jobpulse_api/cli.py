"""CLI for manual imports"""
import asyncio
import sys
from sqlmodel import create_engine, Session
from jobpulse_api.importers.pipeline import ImportPipeline
DATABASE_URL = "postgresql://jobpulse:jobpulse@localhost:5435/jobpulse_dev"
async def import_greenhouse(org: str):
    """Import from Greenhouse"""
    engine = create_engine(DATABASE_URL)
    with Session(engine) as session:
        pipeline = ImportPipeline(session)
        result = await pipeline.import_greenhouse_org(org)
        print(f"\nStatus: {result['status']}")
        print(f"Stats: {result['stats']}")
        if result['status'] == 'failed':
            print(f"Error: {result.get('error')}")
            sys.exit(1)
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python -m jobpulse_api.cli <org>")
        print("Example: python -m jobpulse_api.cli airbnb")
        sys.exit(1)
    org = sys.argv[1]
    asyncio.run(import_greenhouse(org))
