import asyncio


# Why async? LangGraph workflows are async by default. Agents run concurrently
# using asyncio.gather, so we set up the async structure from the start.
async def main():
    """Run the due diligence workflow."""
    print("Workflow will run here")


if __name__ == "__main__":
    asyncio.run(main())
