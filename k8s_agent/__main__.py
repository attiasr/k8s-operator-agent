from typing import Any
import asyncio
import signal

from . import webapp

if __name__ == '__main__':
  shutdown_event = asyncio.Event()

  def _signal_handler(*_: Any) -> None:
    shutdown_event.set()

  loop = asyncio.get_event_loop_policy().get_event_loop()

  loop.add_signal_handler(signal.SIGTERM, _signal_handler)
  loop.add_signal_handler(signal.SIGINT, _signal_handler)

  loop.run_until_complete(asyncio.gather(
          webapp.start(shutdown_event)
  ))
