from ideaCollisionGenerator import IdeaCollisionGenerator

def main():
    generator = IdeaCollisionGenerator()
    generator.getKeywords()
    generator.createPairs()
    generator.promptForIdeas()
    generator.writeToFile()

if __name__ == "__main__":
    main()