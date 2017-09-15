import time

from blessings import Terminal
from progressbar import ProgressBar

term = Terminal()

class Writer(object):
    """Create an object with a write method that writes to a
    specific place on the screen, defined at instantiation.

    This is the glue between blessings and progressbar.
    """
    def __init__(self, location):
        """
        Input: location - tuple of ints (x, y), the position
                        of the bar in the terminal
        """
        self.location = location

    def write(self, string):
        with term.location(*self.location):
            print(string)


writer1 = Writer((0, 10))
writer2 = Writer((0, 20))

pbar1 = ProgressBar(fd=writer1)
pbar2 = ProgressBar(fd=writer2)

pbar1.start()
pbar2.start()

for i in range(100):
    pbar1.update(i)
    pbar2.update(i)
    time.sleep(0.02)

pbar1.finish()
pbar2.finish()
