class JournalSetup(object):
    def __init__(self):
        self.journal = ""
        #list from https://www.english-grammar-revolution.com/list-of-conjunctions.html
        self.coordinatingConjunctions = ['for', 'and','nor', 'but', 'or', 'yet', 'so']
        self.subordinatingConjunctions = ['after', 'although', 'because', 'before', 'lest', 'once', 'only', 'since', 'than', 'that', 'though', 'till', 'unless', 'until', 'when', 'whenever', 'where', 'wherever', 'while']
        self.correlativeConjunctions = ['both', 'either', 'neither', 'nor', 'only', 'also', 'whether']
        #list from https://www.talkenglish.com/vocabulary/top-50-prepositions.aspx
        self.popularPrepositions = ['with', 'from', 'into', 'during', 'including', 'against', 'among', 'throughout', 'despite', 'towards', 'toward', 'upon', 'about', 'through', 'between', 'without', 'along', 'except', 'out']
        self.nonwords = self.coordinatingConjunctions + self.subordinatingConjunctions + self.correlativeConjunctions + self.popularPrepositions
        self.relevantWords = []
        self.songScores = []
    
    #modified from https://www.cs.cmu.edu/~112/notes/notes-strings.html#basicFileIO
    def readSingleEntry(self, path):
        try:
            with open(path, "rt") as f:
                self.journal = f.read()
                if len(self.journal) < 10:
                    self.journal = ""
        except:
            self.journal = ""

    def getRelevantWords(self):
        self.journal = self.journal.lower()
        for word in self.journal.split():
            cleanWord = ""
            for letter in word:
                if letter.isalnum():
                    cleanWord += letter
            if cleanWord not in self.nonwords and len(cleanWord) >= 3 and cleanWord not in self.relevantWords:
                self.relevantWords.append(cleanWord)
        return self.relevantWords

    def countWordOccurrencesInSong(self, lyricsDict):
        self.wordCountsDict = dict()
        for song in lyricsDict:
            self.wordCountsDict[song] = dict()
            wordCounts = self.wordCountsDict[song]
            for word in self.relevantWords:
                count = 0
                lyrics = lyricsDict[song]
                for lyric in lyrics.split():
                    if lyric == word:
                        count += 1
                wordCounts[word] = count
            self.wordCountsDict[song] = wordCounts
        return self.wordCountsDict

    def getKeywordsUsed(self):
        keywords = []
        for song in self.wordCountsDict:
            wordCounts = self.wordCountsDict[song]
            for word in wordCounts:
                if word not in keywords:
                    keywords.append(word)
        return keywords

    def scoreSongs(self):
        for song in self.wordCountsDict:
            totalScore = 0
            title = song[0]
            url = song[1]
            wordCounts = self.wordCountsDict[song]
            for word in wordCounts:
                totalScore += wordCounts[word]
            self.songScores.append((title, url, totalScore))
        return self.songScores
        
    #modified from https://www.cs.cmu.edu/~112/notes/notes-recursion-part1.html#mergesort
    def merge(self, A, B):
        C = [ ]
        i = j = 0
        while ((i < len(A)) or (j < len(B))):
            if ((j == len(B)) or ((i < len(A)) and (A[i][2] >= B[j][2]))):
                C.append(A[i])
                i += 1
            else:
                C.append(B[j])
                j += 1
        return C

    #uses common mergeSort function
    def rankSongs(self, songScores):
        if len(songScores) < 2:
            return songScores
        else:
            mid = len(songScores)//2
            left = self.rankSongs(songScores[:mid])
            right = self.rankSongs(songScores[mid:])
            return self.merge(left, right)

    def eliminateNonMatches(self, rankedSongs, maxSongs=None):
        updatedSongs = []
        for song in rankedSongs:
            if maxSongs == None:
                if song[2] > 0:
                    updatedSongs.append(song)
            else:
                if song[2] > 0 and len(updatedSongs) < maxSongs:
                    updatedSongs.append(song)
        return updatedSongs