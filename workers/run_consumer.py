import asyncio
import logging

from workers.kafka_consumer import start_consumer

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


def main() -> None:
    asyncio.run(start_consumer())


if __name__ == "__main__":
    main()
