import sys
import asyncio

from game.game import Game


async def main():
    """Main entry point for pygbag"""
    game = Game()
    await game.run()


if __name__ == "__main__":
    asyncio.run(main())
