import contextlib
import io
import os
import sys
import tempfile
import unittest
from unittest import mock

# the modules import each other by bare name, so src/ has to be on the path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))


class TestEntryPoint(unittest.TestCase):
    def setUp(self):
        # importing the entry point used to run a full session, which writes a
        # file into the working directory, so the import happens inside a
        # throwaway one
        self.originalDirectory = os.getcwd()
        self.temporaryDirectory = tempfile.TemporaryDirectory()
        os.chdir(self.temporaryDirectory.name)
        sys.modules.pop("collide", None)

    def tearDown(self):
        os.chdir(self.originalDirectory)
        self.temporaryDirectory.cleanup()
        sys.modules.pop("collide", None)

    def testImportingDoesNotStartASession(self):
        prompts = []

        # input is patched rather than left alone so that an unguarded main()
        # is observed as a failure instead of blocking the whole test run
        def recordingInput(prompt=""):
            prompts.append(prompt)
            return "keyword"

        with mock.patch("builtins.input", recordingInput):
            with contextlib.redirect_stdout(io.StringIO()):
                import collide

        self.assertEqual(prompts, [])
        self.assertFalse(os.path.exists("ideas"))
        self.assertTrue(callable(collide.main))

    def testMainRunsTheFourSteps(self):
        with mock.patch("builtins.input", lambda prompt="": "keyword"):
            with contextlib.redirect_stdout(io.StringIO()):
                import collide
                with mock.patch("random.shuffle"):
                    collide.main()

        written = os.listdir("ideas")
        self.assertEqual(len(written), 1)
        with open(os.path.join("ideas", written[0])) as f:
            lines = f.readlines()
        self.assertEqual(len(lines), 5)

    def testDirectMainCallDoesNotStartUsageReporting(self):
        with mock.patch("builtins.input", lambda prompt="": "keyword"):
            with contextlib.redirect_stdout(io.StringIO()):
                import collide
                with mock.patch("collide.startUsageReporting") as start:
                    collide.main()

        start.assert_not_called()

    def testCommandLineRunReportsIdeasWrittenAfterSaving(self):
        with mock.patch("builtins.input", lambda prompt="": "keyword"):
            with contextlib.redirect_stdout(io.StringIO()):
                import collide
                with mock.patch("collide.startUsageReporting") as start:
                    collide.main(reportUsage=True)

        start.assert_called_once_with()
        start.return_value.report.assert_called_once_with("ideas-written")
        self.assertEqual(len(os.listdir("ideas")), 1)


if __name__ == "__main__":
    unittest.main()
