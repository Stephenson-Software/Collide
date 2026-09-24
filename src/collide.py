from ideaCollisionGenerator import IdeaCollisionGenerator
from usage_reporting import startUsageReporting

def main(reportUsage=False):
    # usage reporting is started only from the command line (below), so a
    # direct main() call - the test suite's, for one - reports nothing
    usage = startUsageReporting() if reportUsage else None
    generator = IdeaCollisionGenerator()
    generator.getKeywords()
    generator.createPairs()
    generator.promptForIdeas()
    generator.writeToFile()
    if usage is not None:
        usage.report("ideas-written")

if __name__ == "__main__":
    main(reportUsage=True)