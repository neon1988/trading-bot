from typing import Callable
import time


class Exchange:

    def try_timeout(self, closure, max_try_count: int = 3, timeout_seconds: int = 60, exception=Exception):

        try_count = 0
        while try_count < max_try_count:
            try_count = try_count + 1
            try:
                return closure()
            except exception:
                print(f"Try {try_count} ..")

                if max_try_count <= try_count:
                    raise

                time.sleep(timeout_seconds)
