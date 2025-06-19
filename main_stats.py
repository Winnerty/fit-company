#!/usr/bin/env python
import threading
from src.stats.app import run_app
from src.stats.queue_consumer import run_consumer

def start_consumer():
    consumer_thread = threading.Thread(target=run_consumer, daemon=True)
    consumer_thread.start()


if __name__ == "__main__":
    start_consumer()

    run_app()
