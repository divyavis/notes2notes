import module_manager
module_manager.review()
import nltk
import re
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.stem import PorterStemmer
from nltk.stem.wordnet import WordNetLemmatizer
import math

class JournalSetup(object):
    def __init__(self):
        self.journal = []
        #list from https://www.english-grammar-revolution.com/list-of-conjunctions.html
        self.coordinatingConjunctions = ['for', 'and','nor', 'but', 'or', 'yet', 'so']
        self.subordinatingConjunctions = ['after', 'although', 'because', 'before', 'lest', 'once', 'only', 'since', 'than', 'that', 'though', 'till', 'unless', 'until', 'when', 'whenever', 'where', 'wherever', 'while']
        self.correlativeConjunctions = ['both', 'either', 'neither', 'nor', 'only', 'also', 'whether']
        #list from https://www.talkenglish.com/vocabulary/top-50-prepositions.aspx
        self.popularPrepositions = ['with', 'from', 'into', 'during', 'including', 'against', 'among', 'throughout', 'despite', 'towards', 'toward', 'upon', 'about', 'through', 'between', 'without', 'along', 'except', 'out']
        #list from https://www.enchantedlearning.com/grammar/contractions/list.shtml
        self.contractions = set(["i'm", "i'll", "i'd", "i've", "you're", "you'll", "you'd", "you've", "he's", "he'll", "he'd", "he's", "she's", "she'll", "she'd", "it's", "'tis", "it'll", "it'd", "we're", "we'll", "we'd", "we've", "they're", "they'll", "they'd", "they've", "that's", "that'll", "that'd", "who's", "who'll", "who'd", "what's", "what're", "what'll", "what'd", "where's", "where'll", "where'd", "when's", "when'll", "when'd", "why's", "why'll", "why'd", "how's", "how'll", "how'd", "isn't", "aren't", "wasn't", "weren't", "haven't", "hasn't", "hadn't", "won't", "wouldn't", "don't", "doesn't", "didn't", "can't", "couldn't", "shouldn't", "mightn't", "mustn't", "would've", "should've", "could've", "might've", "must've", "'twas"])
        self.nonwords = set(self.coordinatingConjunctions + self.subordinatingConjunctions + self.correlativeConjunctions + self.popularPrepositions + stopwords.words('english'))
        self.docCount = 0
        self.relevantWords = []
        self.songScores = []
        self.tfScoresDict = dict()
        self.idfScoresDict = dict()
        self.tfidfScoresDict = dict()
        self.keywords = set()
    
    #modified from https://www.cs.cmu.edu/~112/notes/notes-strings.html#basicFileIO
    def readSingleEntry(self, path):
        journal = ""
        try:
            with open(path, "rt") as f:
                journal = f.read()
                if len(journal) < 10:
                    return ""
                else:
                    return journal
        except:
            return ""

    def removeWords(self, journal):
        if isinstance(journal, list):
            newJournal = []
            for entry in journal:
                entryList = []
                entry = entry.lower()
                for word in entry.split():
                    if word not in self.contractions and word not in self.nonwords and len(word) >= 3:
                        entryList.append(word)
                newJournal.append(" ".join(entryList))
            return newJournal
        elif isinstance(journal, str):
            newJournal = []
            journal = journal.lower()
            for word in journal.split():
                if word not in self.contractions and word not in self.nonwords and len(word) >= 3:
                    newJournal.append(word)
            return " ".join(newJournal)
    
    def cleanJournal(self, journal):
        if isinstance(journal, list):
            self.docCount = len(journal)
            self.journal = journal
            self.journal = [self.removeSpecialCharacters(s) for s in journal]
            for elem in self.journal:
                self.relevantWords += elem.split()
            self.relevantWords = set(self.relevantWords)
        elif isinstance(journal, str):
            journal = sent_tokenize(journal)
            self.docCount = len(journal)
            self.journal = journal
            self.journal = [self.removeSpecialCharacters(s) for s in journal]
            for elem in self.journal:
                self.relevantWords += elem.split()
            self.relevantWords = set(self.relevantWords)

    #from https://towardsdatascience.com/tfidf-for-piece-of-text-in-python-43feccaa74f8
    def removeSpecialCharacters(self, s):
        stripped = re.sub('[^\w\s]', '', s)
        stripped = re.sub('_', '', stripped)
        stripped = re.sub('\s+', ' ', stripped)
        stripped = stripped.strip()
        return stripped
    
    def tfPerSentence(self, sentence):
        #tf = (frequency of the term in the doc/total number of terms in the doc)
        sentenceTfScores = dict()
        sentenceList = sentence.split()
        for word in sentenceList:
            sentenceTfScores[word] = sentenceList.count(word)/len(sentenceList)
        return sentenceTfScores
    
    def normalizingTfScores(self):
        #normalization of tf(average of duplicate tf scores/absolute word count in all docs)
        addedTfScores = dict()
        wordCounts = dict()
        totalWords = 0
        for doc in self.journal:
            totalWords += len(doc.split())
        for doc in self.journal:
            sentenceTfDict = self.tfPerSentence(doc)
            for key in sentenceTfDict:
                if key in addedTfScores:
                    wordScorePrev = addedTfScores[key]
                    wordScoreAdding = sentenceTfDict[key]
                    addedTfScores[key] += wordScoreAdding
                else:
                    addedTfScores[key] = sentenceTfDict[key]
                if key in wordCounts:
                    wordCounts[key] += 1
                else:
                    wordCounts[key] = 1
        for word in addedTfScores:
            wordCount = wordCounts[word]
            self.tfScoresDict[word] = addedTfScores[word] / wordCount
        return self.tfScoresDict
                
    def termInDoc(self, term, doc):
        for word in doc.split():
            if word == term:
                return True
        return False

    def idfScoring(self):
        #idf = ln(total number of docs/number of docs with term in it)
        for word in self.relevantWords:
            docsWithTerm = 0
            for doc in self.journal:
                if self.termInDoc(word, doc):
                    docsWithTerm += 1
            self.idfScoresDict[word] = math.log(self.docCount/docsWithTerm)
        return self.idfScoresDict

    #info on tfidf from http://www.tfidf.com/ but all functions written by me
    def tfidfScoring(self):
        tfScores = self.normalizingTfScores()
        idfScores = self.idfScoring()
        for word1 in tfScores:
            for word2 in idfScores:
                if word1 == word2:
                    tfidfScore = tfScores[word1] * idfScores[word2]
                    self.tfidfScoresDict[word1] = tfidfScore
        return self.tfidfScoresDict

    def stemming(self, journal):
        stemmer = PorterStemmer()
        newJournal = []
        for sentence in journal:
            for word in sentence.split():
                newJournal.append(stemmer.stem(word))
        return newJournal

    def getRelevantWords(self, journal):
        journal = self.removeWords(journal)
        self.cleanJournal(journal)
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
        keywords = set()
        for song in self.wordCountsDict:
            wordCounts = self.wordCountsDict[song]
            for word in wordCounts:
                if wordCounts[word] != 0:
                    keywords.add(word)
        return keywords

    def scoreSongsNLP(self):
        tfidfScores = self.tfidfScoring()
        for song in self.wordCountsDict:
            totalScore = 0
            title = song[0]
            url = song[1]
            wordCounts = self.wordCountsDict[song]
            for word in wordCounts:
                wordScore = 0
                tfidfScore = self.tfidfScoresDict[word]
                if wordCounts[word] == 0:
                    continue
                else:
                    wordScore = tfidfScore * wordCounts[word]
                if wordScore != 0:
                    self.keywords.add(word)
                totalScore += wordScore
            self.songScores.append((title, url, totalScore))
        return self.songScores

    def scoreSongs(self):
        for song in self.wordCountsDict:
            totalScore = 0
            title = song[0]
            url = song[1]
            wordCounts = self.wordCountsDict[song]
            for word in wordCounts:
                totalScore += wordCounts[word]
                self.keywords.add(word)
            self.songScores.append((title, url, totalScore))
        return self.songScores

    #modified from https://www.cs.cmu.edu/~112/notes/notes-recursion-part1.html#mergesort
    def merge(self, A, B):
        C = [ ]
        i = j = 0
        while ((i < len(A)) or (j < len(B))):
            if ((j == len(B)) or ((i < len(A)) and (A[i][2] >= B[j][2]))): #this reverse sorts in the subsequent merge sort function
                C.append(A[i])
                i += 1
            else:
                C.append(B[j])
                j += 1
        return C

    #uses common mergeSort function (but written from memory by me)
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
                #song[2] is song score
                if song[2] > 0:
                    updatedSongs.append(song)
            else:
                if song[2] > 0 and len(updatedSongs) < maxSongs:
                    updatedSongs.append(song)
        return updatedSongs
