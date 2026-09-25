import datetime
import random
import os

class IdeaCollisionGenerator:
    def __init__(self, numKeywords=10):
        # keywords are matched in pairs, so the count has to be even
        if numKeywords < 2 or numKeywords % 2 != 0:
            raise ValueError("numKeywords must be a positive even number")
        self.numKeywords = numKeywords
        self.keywords = []
        self.pairs = []
        self.ideas = []

    def ordinal(self, n):
        # 1st, 2nd, 3rd, 4th ... 11th, 12th, 13th ... 21st, 22nd, 23rd
        if n % 100 in (11, 12, 13):
            suffix = "th"
        elif n % 10 == 1:
            suffix = "st"
        elif n % 10 == 2:
            suffix = "nd"
        elif n % 10 == 3:
            suffix = "rd"
        else:
            suffix = "th"
        return str(n) + suffix

    def getKeywords(self):
        # get keywords from user
        for i in range(self.numKeywords):
            keyword = input("Enter " + self.ordinal(i+1) + " keyword: ")
            self.keywords.append(keyword)

        # randomize keywords
        random.shuffle(self.keywords)

    def createPairs(self):
        # an odd keyword would be left without a partner, so it is refused
        # the same way the constructor refuses an odd numKeywords
        if len(self.keywords) % 2 != 0:
            raise ValueError("keywords must have an even count to be paired, got " + str(len(self.keywords)))

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