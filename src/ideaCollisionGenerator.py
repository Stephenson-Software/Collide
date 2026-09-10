import datetime
import random
import os

class IdeaCollisionGenerator:
    def __init__(self):
        self.keywords = []
        self.pairs = []
        self.ideas = []

    def getKeywords(self):
        # get 10 keywords from user
        numKeywords = 10
        for i in range(numKeywords):
            if i == 0:
                keyword = input("Enter 1st keyword: ")
                self.keywords.append(keyword)
            elif i == 1:
                keyword = input("Enter 2nd keyword: ")
                self.keywords.append(keyword)
            elif i == 2:
                keyword = input("Enter 3rd keyword: ")
                self.keywords.append(keyword)
            else:
                keyword = input("Enter " + str(i+1) + "th keyword: ")
                self.keywords.append(keyword)

        # randomize keywords
        random.shuffle(self.keywords)

    def createPairs(self):
        # match keywords in pairs
        for i in range(0, len(self.keywords), 2):
            pair = []
            pair.append(self.keywords[i])
            pair.append(self.keywords[i+1])
            self.pairs.append(pair)

    def promptForIdeas(self):
        # show pairs to user and prompt for ideas
        for i in range(len(self.pairs)):
            print("Enter an idea based off of these keywords: " + str(self.pairs[i]))
            idea = input("Enter an idea: ")
            self.ideas.append(idea)

    def writeToFile(self):
        # make folder if nonexistent
        if not os.path.exists("ideas"):
            os.makedirs("ideas")

        # get timestamp for filename
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H.%M.%S")
        filename = "ideas/ideas-" + timestamp + ".txt"

        # write idea to file
        with open(filename, "w", encoding="utf-8") as f:
            for i in range(len(self.pairs)):
                f.write(str(self.pairs[i]) + ": " + self.ideas[i] + "\n")