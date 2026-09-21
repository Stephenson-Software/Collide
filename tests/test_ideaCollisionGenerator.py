import contextlib
import io
import os
import sys
import tempfile
import unittest
from unittest import mock

# the modules import each other by bare name, so src/ has to be on the path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

from ideaCollisionGenerator import IdeaCollisionGenerator


class TestGetKeywords(unittest.TestCase):
    def testCollectsTenKeywords(self):
        generator = IdeaCollisionGenerator()
        with mock.patch("builtins.input", side_effect=[str(i) for i in range(10)]):
            with mock.patch("random.shuffle"):
                generator.getKeywords()
        self.assertEqual(generator.keywords, [str(i) for i in range(10)])

    def testPromptsUseOrdinalLadder(self):
        generator = IdeaCollisionGenerator()
        prompts = []

        def recordingInput(prompt):
            prompts.append(prompt)
            return "keyword"

        with mock.patch("builtins.input", recordingInput):
            with mock.patch("random.shuffle"):
                generator.getKeywords()

        self.assertEqual(prompts[0], "Enter 1st keyword: ")
        self.assertEqual(prompts[1], "Enter 2nd keyword: ")
        self.assertEqual(prompts[2], "Enter 3rd keyword: ")
        self.assertEqual(prompts[3], "Enter 4th keyword: ")
        self.assertEqual(prompts[9], "Enter 10th keyword: ")

    def testPromptsAreCorrectPastTwenty(self):
        generator = IdeaCollisionGenerator(numKeywords=23)
        prompts = []

        def recordingInput(prompt):
            prompts.append(prompt)
            return "keyword"

        with mock.patch("builtins.input", recordingInput):
            with mock.patch("random.shuffle"):
                generator.getKeywords()

        self.assertEqual(prompts[20], "Enter 21st keyword: ")
        self.assertEqual(prompts[21], "Enter 22nd keyword: ")
        self.assertEqual(prompts[22], "Enter 23rd keyword: ")

    def testKeywordCountIsConfigurable(self):
        generator = IdeaCollisionGenerator(numKeywords=4)
        with mock.patch("builtins.input", side_effect=["a", "b", "c", "d"]):
            with mock.patch("random.shuffle"):
                generator.getKeywords()
        self.assertEqual(generator.keywords, ["a", "b", "c", "d"])

    def testKeywordCountDefaultsToTen(self):
        self.assertEqual(IdeaCollisionGenerator().numKeywords, 10)

    def testKeywordsAreShuffled(self):
        generator = IdeaCollisionGenerator()
        with mock.patch("builtins.input", side_effect=[str(i) for i in range(10)]):
            with mock.patch("random.shuffle") as shuffle:
                generator.getKeywords()
        shuffle.assert_called_once_with(generator.keywords)

    def testEmptyKeywordsAreAccepted(self):
        # current behaviour: no validation, an empty line becomes a keyword
        generator = IdeaCollisionGenerator()
        with mock.patch("builtins.input", side_effect=[""] * 10):
            with mock.patch("random.shuffle"):
                generator.getKeywords()
        self.assertEqual(generator.keywords, [""] * 10)


class TestOrdinal(unittest.TestCase):
    def testSuffixes(self):
        generator = IdeaCollisionGenerator()
        expected = {
            1: "1st", 2: "2nd", 3: "3rd", 4: "4th", 10: "10th",
            11: "11th", 12: "12th", 13: "13th", 14: "14th",
            21: "21st", 22: "22nd", 23: "23rd", 24: "24th",
            101: "101st", 111: "111th", 112: "112th", 113: "113th", 121: "121st",
        }
        for n, text in expected.items():
            self.assertEqual(generator.ordinal(n), text)


class TestCreatePairs(unittest.TestCase):
    def testPairsAdjacentKeywords(self):
        generator = IdeaCollisionGenerator()
        generator.keywords = ["a", "b", "c", "d"]
        generator.createPairs()
        self.assertEqual(generator.pairs, [["a", "b"], ["c", "d"]])

    def testTenKeywordsProduceFivePairs(self):
        generator = IdeaCollisionGenerator()
        generator.keywords = [str(i) for i in range(10)]
        generator.createPairs()
        self.assertEqual(len(generator.pairs), 5)

    def testNoKeywordsProduceNoPairs(self):
        generator = IdeaCollisionGenerator()
        generator.createPairs()
        self.assertEqual(generator.pairs, [])

    def testOddKeywordCountRaisesIndexError(self):
        # current behaviour: keywords[i+1] is unguarded, so the final iteration
        # indexes past the end (unreachable through the CLI, where the count is 10)
        generator = IdeaCollisionGenerator()
        generator.keywords = ["a", "b", "c"]
        with self.assertRaises(IndexError):
            generator.createPairs()


class TestPromptForIdeas(unittest.TestCase):
    def testCollectsOneIdeaPerPair(self):
        generator = IdeaCollisionGenerator()
        generator.pairs = [["a", "b"], ["c", "d"]]
        with mock.patch("builtins.input", side_effect=["first", "second"]):
            # promptForIdeas() prints each pair, which would otherwise be
            # interleaved with the test runner's own output
            with contextlib.redirect_stdout(io.StringIO()):
                generator.promptForIdeas()
        self.assertEqual(generator.ideas, ["first", "second"])

    def testPromptsUseInputPrompt(self):
        generator = IdeaCollisionGenerator()
        generator.pairs = [["a", "b"]]
        prompts = []

        def recordingInput(prompt):
            prompts.append(prompt)
            return "idea"

        with mock.patch("builtins.input", recordingInput):
            with contextlib.redirect_stdout(io.StringIO()):
                generator.promptForIdeas()

        self.assertEqual(prompts, ["Enter an idea: "])

    def testEachPairIsPrintedBeforeItsPrompt(self):
        generator = IdeaCollisionGenerator()
        generator.pairs = [["a", "b"], ["c", "d"]]
        printed = io.StringIO()

        with mock.patch("builtins.input", side_effect=["first", "second"]):
            with contextlib.redirect_stdout(printed):
                generator.promptForIdeas()

        self.assertEqual(printed.getvalue(), (
            "Enter an idea based off of these keywords: ['a', 'b']\n"
            "Enter an idea based off of these keywords: ['c', 'd']\n"
        ))


class TestWriteToFile(unittest.TestCase):
    def setUp(self):
        # writeToFile() resolves its output path against the current working
        # directory, so every case runs inside a throwaway one
        self.originalDirectory = os.getcwd()
        self.temporaryDirectory = tempfile.TemporaryDirectory()
        os.chdir(self.temporaryDirectory.name)

    def tearDown(self):
        os.chdir(self.originalDirectory)
        self.temporaryDirectory.cleanup()

    def testWritesOneLinePerPair(self):
        generator = IdeaCollisionGenerator()
        generator.pairs = [["a", "b"], ["c", "d"]]
        generator.ideas = ["first", "second"]
        generator.writeToFile()

        written = os.listdir("ideas")
        self.assertEqual(len(written), 1)
        with open(os.path.join("ideas", written[0])) as f:
            lines = f.readlines()
        self.assertEqual(lines, ["['a', 'b']: first\n", "['c', 'd']: second\n"])

    def testCreatesIdeasDirectoryRelativeToWorkingDirectory(self):
        generator = IdeaCollisionGenerator()
        generator.pairs = [["a", "b"]]
        generator.ideas = ["first"]
        self.assertFalse(os.path.exists("ideas"))
        generator.writeToFile()
        self.assertTrue(os.path.isdir("ideas"))

    def testSameTimestampReplacesRatherThanAppends(self):
        # the timestamp has one-second resolution, so two runs can land on the
        # same filename; the second one replaces the first
        generator = IdeaCollisionGenerator()
        generator.pairs = [["a", "b"]]
        generator.ideas = ["first"]

        frozenClock = mock.Mock()
        frozenClock.datetime.now.return_value.strftime.return_value = "frozen"
        with mock.patch("ideaCollisionGenerator.datetime", frozenClock):
            generator.writeToFile()

            second = IdeaCollisionGenerator()
            second.pairs = [["c", "d"]]
            second.ideas = ["second"]
            second.writeToFile()

        self.assertEqual(os.listdir("ideas"), ["ideas-frozen.txt"])
        with open(os.path.join("ideas", "ideas-frozen.txt")) as f:
            self.assertEqual(f.readlines(), ["['c', 'd']: second\n"])

    def testOutputFileIsOpenedAsUtf8(self):
        # the written bytes are the same under the platform default on every
        # machine the tests run on, so the encoding is observed on the call
        generator = IdeaCollisionGenerator()
        generator.pairs = [["café", "b"]]
        generator.ideas = ["résumé"]

        realOpen = open
        recorded = {}

        def recordingOpen(path, *args, **kwargs):
            recorded["args"] = args
            recorded["kwargs"] = kwargs
            return realOpen(path, *args, **kwargs)

        with mock.patch("builtins.open", recordingOpen):
            generator.writeToFile()

        self.assertEqual(recorded["args"], ("w",))
        self.assertEqual(recorded["kwargs"], {"encoding": "utf-8"})

        written = os.listdir("ideas")[0]
        with open(os.path.join("ideas", written), "rb") as f:
            self.assertEqual(f.read().decode("utf-8"), "['café', 'b']: résumé\n")

    def testFilenameIsTimestamped(self):
        generator = IdeaCollisionGenerator()
        generator.pairs = [["a", "b"]]
        generator.ideas = ["first"]
        generator.writeToFile()

        written = os.listdir("ideas")[0]
        self.assertTrue(written.startswith("ideas-"))
        self.assertTrue(written.endswith(".txt"))


if __name__ == "__main__":
    unittest.main()
