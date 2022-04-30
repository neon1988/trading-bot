from app.trading.management.commands.download_data import Command
import unittest


class DownloadDataBatchTimeTest(unittest.TestCase):

    def test(self):
        command = Command()

        self.assertEqual([[10, 35], [35, 60], [60, 84]],
                         command.batch_time(10, 84, 25))

    def test2(self):
        command = Command()

        self.assertEqual([[1650380845, 1650985645]],
                         command.batch_time(1650380845, 1650985645, 3596400))


