import asyncio
from notebooklm import NotebookLMClient

async def main():
    try:
        async with NotebookLMClient.from_storage() as client:
            notebooks = await client.notebooks.list()
            print(f"Successfully connected to NotebookLM! Found {len(notebooks)} notebooks:")
            for nb in notebooks:
                # print nb id and title
                print(f"  ID: {nb.id} | Title: {nb.title}")
    except Exception as e:
        print(f"Error connecting to NotebookLM: {type(e).__name__}: {e}")

if __name__ == "__main__":
    asyncio.run(main())
