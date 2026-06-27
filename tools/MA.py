#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
#~ import unidecode
import pathlib
import datetime
import time
import shutil

import tkinter as tk
from tkinter import messagebox

#~ import PyPDF2
#~ from PyPDF2 import pypdf
import PyPDF2 as pypdf

#~ import pypdf
#~ from reportlab.lib.pagesizes import letter
#~ from reportlab.pdfgen import canvas

# BUGS
#
# 'N' for next page doesn't work
# instruments' list is not updated


# defining some constants and other global variables.
if 1:
    MA_VERSION = "1.00"
    TAB_SIZE = 4
    
    PDF_EXTENSION = ".pdf"
    
    TAG_SPLITTER = "#"
    SPACE = " "
    QUOTE = '"'
    MINUS = "-"
    CR = "\n"
    EMPTY_STRING = ""
    COMMENT_QUOTE = ";"
    PARTIAL_SPLIT = "_"
    ASTERISK  = "*"
    UNDERSCORE = "_"
    ESPERLUETTE = "@"
    NONAME = "NONAME"
    HTML_PARAGRAPH_START = "<p>"
    HTML_PARAGRAPH_STOP = "</p>\n"
    HTML_CR = "<br>"
    HTML_SPACE = "&nbsp;"
    JAVASCRIPT_COMMENT = "//"
    RELEASE_SOURCE_NAME = "releaseSkeleton.htm"
    NIGHTLY_BUILD_SOURCE_NAME = "nightlyBuildSkeleton.htm"
    HTML_PAGE_NAME = "index.htm"
    STUFF_TAG = "#STUFF_CREATION#"
    UTF8_TEXT = "# -*- coding: utf-8 -*-"
    TIMESTAMP_TAG = "#TIMESTAMP#"
    #~ TYPE_TAG = "#TYPE#"
    #~ RELEASE = "RELEASE"
    #~ NIGHTLY_BUILD = "NIGHTLY BUILD"
    FULLS_SCREEN_TAG = "#FULL_SCREEN_LIB#"
    
    NIGHTLY_BUILD_CATALOG_SKELETON_NAME = "catalogSkeleton.htm"
    WEB_PAGE_NAME = "index.htm"
    TRACKLIST_NAME = "tracklist.txt"    
    RELEASE_WEB_CATALOG_NAME = "catalog.htm"
    DEV_WEB_CATALOG_NAME = "catalog.htm"
    CATALOG_FNAME = "catalog.htm"
    
    PREVIOUS_FOLDER = "../"
    TEMP_DIR = "temp"
    TEMP_POPULATE_JS_FNAME = os.path.join(TEMP_DIR, "populate.js")
    FULL_SCREEN_LIB_NAME ="fullScreen.js"
    TRACE_FNAME = os.path.join(TEMP_DIR, "trace.txt")
    MA_NAME = "Musician Assistant"

    ICON_SPEAKER = "../img/speaker.gif"
    ICON_MELODY = "../img/ear.gif"
    ICON_PARTIAL = "../img/brackets.gif"
    ICON_GENERIC = "../img/%s.gif"
    CURRENT_FOLDER = "./"
    SCORE_FOLDER = "score"
    SCORE_DEFAULT_TYPES = ("DO", "SIb", "MIb", "basse")
    MP3_FOLDER = "mp3"
    MP3_DEFAULT_TYPES = ("backtrack", "melody", "partial")
    UPDATE_FOLDER = ("update")

    ROOT_DEEP = 0
    NODE_DEEP = 1
    TRACKLIST_DEEP = 2

    BUILDING_MODE = None
    BUILDING_MODE_ALL = "all"
    BUILDING_MODE_NODE = "node"
    BUILDING_MODE_BOOK = "book"

    C_INSTRUMENTS = ["DO", "accordeon", "harmonica", "portugaise", "guitare", "eguitar", "mguitar", "synth", "flute", "flute2", "vocals",
        "grid", "piano", "ukulele", "trombone","guitare", "mandoline","mandoline2","mandole","easytrombone"]
    BB_INSTRUMENTS = ["SIb", "tenor", "trompette", "baryton", "clarinette", "tuba", "bass_SIb"]
    EB_INSTRUMENTS = ["MIb", "alto", "alto2", "alto3"]
    BASS_INSTRUMENTS = ["basse", "basse_keyG", "grid"] + C_INSTRUMENTS
    VOCALS_INSTRUMENTS = ["vocals", "lyrics", "grid"] + ["DO"]
    F_INSTRUMENTS = ["F", "cor_F", "alto_recorder"]
    INSTRUMENTS_FAMILY_NAMES = [C_INSTRUMENTS[0], BB_INSTRUMENTS[0], EB_INSTRUMENTS[0], BASS_INSTRUMENTS[0], F_INSTRUMENTS[0]]
    instruments = list(set(C_INSTRUMENTS + BB_INSTRUMENTS + EB_INSTRUMENTS + BASS_INSTRUMENTS + VOCALS_INSTRUMENTS))
    instruments.sort()

join = os.path.join
isfile = os.path.isfile
isdir = os.path.isdir
listdir = os.listdir
basename = os.path.basename
dirname = os.path.dirname
relpath = os.path.relpath
splitext = os.path.splitext

import unicodedata

def remove_accents(input_str):
    """Remove accents from text."""
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    return ''.join([char for char in nfkd_form if not unicodedata.combining(char)])

import unicodedata

def clean_text(text: str) -> str:
    """Nettoie un texte des caractères typographiques et spéciaux.
    - Remplace les apostrophes typographiques (‘ ’) → '
    - Remplace les tirets longs (– —) → -
    - Remplace les guillemets typographiques (“ ” « ») → "
    - Remplace les espaces insécables → espace normal
    - Supprime les caractères de contrôle invisibles
    - Normalise en NFC (Unicode standard)
    """

    if not isinstance(text, str):
        text = str(text)

    # Normalisation Unicode (ex. lettres accentuées combinées)
    text = unicodedata.normalize("NFC", text)

    # Remplacements typographiques
    replacements = {
        "’": "'", "‘": "'", "‛": "'",  # apostrophes
        "–": "-", "—": "-", "−": "-",  # tirets
        "“": '"', "”": '"', "«": '"', "»": '"',  # guillemets
        "\u00A0": " ",  # espace insécable
        "\u202F": " ",  # espace fine insécable
        "\u200B": "",   # zero-width space
        "\uFEFF": "",   # byte order mark
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    # Supprime les caractères de contrôle non imprimables
    text = ''.join(ch for ch in text if ch.isprintable())

    # Supprime les doubles espaces
    while "  " in text:
        text = text.replace("  ", " ")

    return text.strip()

def toCamelCase(text):
    """Convert a string to camelCase."""
    # Define constants
    SPACE = ' '
    EMPTY_STRING = ''

    # Normalize and remove accents
    text = remove_accents(text).lower()
    text = str(text).replace(SPACE+SPACE, SPACE)
    
    # Initialize variables
    position = text.find('(')
    temp = EMPTY_STRING
    space_flag = False

    #Eszett
    text = text.replace("ß","ss")

    # Convert to camelCase
    for car in text:
        if car in (" /-!,?:+*'’"):
            # these characters need a new word
            space_flag = True
        elif car in "().":
            pass
            # these characters are simply ignored
        else:
            if space_flag:
                temp += car.upper()
            else:
                temp += car.lower()
            space_flag = False
    
    return temp

START_TIME = datetime.datetime.now()

def makeDir(repertoire):
    if not os.path.exists(repertoire):
        os.makedirs(repertoire)  # crée aussi les sous-dossiers si besoin

def istracklist(fullpath):
    if isfile(fullpath):
        if basename(fullpath) == TRACKLIST_NAME:
            return True
    return False

def isbook(fullpath):
    if isdir(fullpath):
        for item in listdir(fullpath):
            fname = join(fullpath, item)
            if istracklist(fname):
                return True
    return False

def isnode(fullpath):
    if isdir(fullpath):
        for item in listdir(fullpath):
            fname = join(fullpath, item)
            if isdir(fname):
                if isbook(fname):
                    return True
    return False

def report(text):
    if "-v" in sys.argv:
        sys.stdout.write(text)
        sys.stdout.write(CR)

def getDuration():
    stop_time = datetime.datetime.now()
    duration = stop_time - START_TIME
    duration = int(duration.total_seconds() + 0.5)
    second = duration % 60
    minute = duration // 60
    return "%u:%02u"%(minute, second)

def listToJavascript(my_list, text_mode=False, header=None, enclosing=("[", "]")):
    text = EMPTY_STRING
    if header != None:
        text = header
    text += enclosing[0]

    if text_mode != False:
        my_list = ['"%s"'% item for item in my_list]
    text += ",".join(my_list)

    text += enclosing[1]
    return text

def tupleToJavascript(items, text_mode=False, header=None):
    return listToJavascript(items, text_mode=text_mode, header=header, enclosing=("(", ")"))

def functionToJavascript(function_name, params, text_mode=False, body=None):
    text = listToJavascript(params, header=function_name, text_mode=text_mode, enclosing=("(", ")"))

    if body != None:
        text += "%s{%s%s}%s"%(CR, CR, body, CR)
    return text

def variableToJavascript(var_name, value, text_mode=False, no_prefix=False):
    value = str(value)
    if text_mode:
        value = ('"%s"'%value)
    if no_prefix:
        text = EMPTY_STRING
    else:
        text = "var "
    return text + "%s = %s;%s"%(var_name, value, CR)

def commentToJavascript(comment):
    return "%s %s%s"%(JAVASCRIPT_COMMENT, comment, CR)

def saveHtmlPage(fname, js_code, tags):
    js_code += variableToJavascript("tagLabel", listToJavascript(tags, text_mode=True))
    js_code += translateInstrumentsToJavascript()
        
    skeleton_name = NIGHTLY_BUILD_SOURCE_NAME        
    with open(skeleton_name, "r", encoding='utf-8') as fp:
        big_text = fp.read(-1)
    big_text = big_text.replace(FULLS_SCREEN_TAG, open(FULL_SCREEN_LIB_NAME, "r", encoding='utf-8').read(-1))
    big_text = big_text.replace(STUFF_TAG, js_code)
    with open(fname, "w", encoding='utf-8') as fp:
        fp.write(big_text)
    report("HTML page '%s' updated"%fname)

class MP3():
    def __init__(self, fname, genre):
        self.__fname = fname
        self.__genre = genre

    def getGenre(self):
        return self.__genre
    
    def getFname(self, root=None):
        if root == None:
            return self.__fname
        else:
            return os.path.relpath(self.__fname, root)
    
    def __str__(self):
        return "%s : %s"%(self.getGenre(), self.getFname())
        
class SCORE():
    def __init__(self, fname, instrument):
        self.__fname = fname
        self.__instrument = instrument
        self.__number_of_pages = 1
        self.countNumberOfPages()

    def getNumberOfPages(self):
        return self.__number_of_pages

    def setNumberOfPages(self, number_of_pages):
        self.__number_of_pages = number_of_pages 

    def countNumberOfPages(self):
        fname = self.getFname()
        folder = dirname(fname)
        prefix_fname = basename(fname)
        prefix_fname, ext = splitext(prefix_fname)
        nb_pages = 1
        
        if not isfile(fname):
            raise Exception("score not found! %s"%fname)
        
        while 1:
            page_name = join(folder, prefix_fname+"%02u%s"%(nb_pages+1, ext))
            if not isfile(page_name):
                self.setNumberOfPages(nb_pages)
                break
            else:
                nb_pages += 1
        return self.getNumberOfPages()

    def getInstrument(self):
        return self.__instrument
    
    def getFname(self, root=None):
        if root == None:
            return self.__fname
        else:
            return os.path.relpath(self.__fname, root)
        
    def __str__(self):
        return "%s(%u) : %s"%(self.getInstrument(), self.getNumberOfPages(), self.getFname())
        
class LINE:
    def __init__(self, line, location, modified_callback=None):
        self.__title = None
        self.__short_name = None
        self.__location = location
        self.__tags = []
        self.__alias = None
        self.__comment = EMPTY_STRING
        self.__modified_callback = modified_callback
        self.__scores = []
        self.__mp3s = []

        if line != None:
            line = line.strip()
            
            if COMMENT_QUOTE in line:
                pos = line.find(COMMENT_QUOTE)
                self.__comment = line[pos+1:].strip()
                line = line[:pos].strip()

            if TAG_SPLITTER in line:
                pos = line.find(TAG_SPLITTER)
                tags = line[pos+1:].strip()
                line = line[:pos].strip()
            
                if len(tags) > 1:
                    tags = [word.strip().lower() for word in tags.split(SPACE)]
                    for tag in tags:
                        if tag != EMPTY_STRING:
                            if not tag in self.__tags:
                                self.__tags.append(tag)

            if ESPERLUETTE in line:
                pos = line.find(ESPERLUETTE)
                self.__alias = line[pos+1:].strip()
                self.__title = line[:pos].strip()
            else:
                self.__title = line
                self.__short_name = toCamelCase(self.__title)
        else:
            raise Exception("line = None!")

        self.scanSubFolders()

    def scanSubFolders(self):
        mp3_location = os.path.join(self.getLocation(), MP3_FOLDER)
        makeDir(mp3_location)
        #~ print(mp3_location)
        for folder in os.listdir(mp3_location):
            sub_dir = os.path.join(mp3_location, folder)
            if os.path.isdir(sub_dir):
                if folder == "partial":
                    for fname in os.listdir(sub_dir):
                        mp3_name = os.path.join(sub_dir, fname)
                        if os.path.isfile(mp3_name):
                            if os.path.splitext(fname)[0].startswith("%s_"%self.getShortName()):
                                words = os.path.splitext(fname)[0].split("_")
                                mp3 = MP3(mp3_name, ":".join(words[1:]))
                                self.addMp3(mp3)
                else:
                    for fname in os.listdir(sub_dir):
                        mp3_name = os.path.join(sub_dir, fname)
                        if os.path.isfile(mp3_name):
                            if os.path.splitext(fname)[0] == self.getShortName():
                                mp3 = MP3(mp3_name, folder)
                                self.addMp3(mp3)

        score_location = os.path.join(self.getLocation(), SCORE_FOLDER)
        self.__instruments = []
        for folder in os.listdir(score_location):
            sub_dir = os.path.join(score_location, folder)
            if os.path.isdir(sub_dir):
                self.__instruments.append(folder)
                for fname in os.listdir(sub_dir):
                    score_name = os.path.join(sub_dir, fname)
                    if os.path.isfile(score_name):
                        if os.path.splitext(fname)[0] == self.getShortName():
                            score = SCORE(score_name, folder)
                            self.addScore(score)

    def setModifiedFlag(self):
        if self.__modified_callback != None:
            self.__modified_callback

    def getModifiedFlag(self):
        if self.__modified_callback != None:
            return self.__modified_callback

    def getsortTitle(self):
        return self.__title.lower()

    def getLine(self):
        line = self.__title
        if self.__alias != None:
            line += " %s%s" %(ESPERLUETTE, self.__alias)
            
        if len(self.__tags):
            line += " %s %s" %(TAG_SPLITTER, SPACE.join(self.__tags))

        if len(self.__comment):
            line += "%s%s" %(COMMENT_QUOTE, self.__comment)
        line += CR
        
        return line

    def __str__(self):
        text = self.getLine()
        text += "    tags : %s%s"%(SPACE.join(self.__tags), CR)
        for mp3 in self.__mp3s:
            text += "    %s%s"%(mp3, CR)
        for score in self.__scores:
            text += "    %s%s"%(score, CR)
        return text

    def getLocation(self, root=None):
        if root == None:
            return self.__location
        else:
            return os.path.relpath(self.__location, root)

    def getShortName(self):
        return self.__short_name

    def addMp3(self, mp3):
        self.__mp3s.append(mp3)

    def getMp3s(self):
        return self.__mp3s
        
    def addScore(self, score):
        self.__scores.append(score)

    def getScores(self):
        return self.__scores

    def hasInstrument(self, instrument):
        for score in self.getScores():
            if score.getInstrument() == instrument:
                return True
        return False

    def getScore(self, instrument):
        for score in self.getScores():
            if score.getInstrument() == instrument:
                return score
        return None
            
    def getTitle(self):
        return self.__title

    def getTags(self):
        return self.__tags

    def isAlias(self):
        return self.__alias != None
        
    def getAlias(self):
        return self.__alias
        
    def hasTag(self, tag):
        return tag in self.__tags

    def hasTags(self):
        return len(self.__tags) > 0

    # methods which set modified_flag
        
    def setTitle(self, title):
        title = title.strip()
        if title != self.getTitle():
            self.__title = title
            self.setModifiedFlag()

    def setTags(self, tags):
        if tags != self.getTags():
            self.__tags = tags
            self.setModifiedFlag()

    def addTag(self, tag):
        tag = tag.lower()
        if not tag in self.getTags():
            self.__tags.append(tag)
            self.__tags.sort()
            self.setModifiedFlag()

    def removeTag(self, tag):
        tag = tag.lower()
        if tag in self.getTags():
            self.__tags.remove(tag)
            self.setModifiedFlag()

    def setAlias(self, alias):
        self.__alias = alias
        self.setModifiedFlag()


class BOOK(list):
    # a list of LINE()
    def __init__(self, home, location, *args, **kwds):
        super().__init__(*args, **kwds)
        self.__home = home# adresse absolue du site
        self.__location = location # adresse absolue du noeud
        self.__fname = join(location, TRACKLIST_NAME) # fname de la tracklist
        self.__dirname = basename(self.__location) # nom du book/répertoire
        self.__label = camelCaseToSentence(basename(self.__location)) # temporaire jusqu'à la lecture de la 1ère ligne de la tracklist
        self.__modified_flag = False
        self.__tags = [] # tags will be populated on lines below
        
        with open(self.__fname, "r", encoding='utf-8') as fp:
            lines = [line.strip() for line in fp.readlines()]
            
            # test première ligne
            line = lines[0]
            if not line.startswith(UTF8_TEXT):
                raise Exception("%s%sis not a %s tracklist!"%(self.__fname, CR, MA_NAME))

            # ajout des lignes suivantes
            for line in lines[1:]:
                objline = LINE(line, location, modified_callback=self.setModifiedFlag)
                self.addLine(objline)
                for tag in objline.getTags():
                    if not tag in self.__tags:
                        self.__tags.append(tag)
            self.__tags.sort()

    def addLine(self, new_line):
        title = new_line.getTitle()
        for line in self:
            if line.getTitle() == title:
                raise Exception("%s already in book %s!"%(title, self.getDirname()))
        self.append(new_line)

    def getHome(self):
        return self.__home
    
    def getLocation(self):
        return self.__location
        
    def getDirname(self):
        return self.__dirname

    def getFname(self):
        return self.__fname
        
    def getLabel(self):
        return self.__label
        
    def setModifiedFlag(self):
        self.__modified_flag = True
        
    def clearModifiedFlag(self):
        self.__modified_flag = False
        
    def isModified(self):
        return self.__modified_flag
    
    def __str__(self):
        text = "BOOK %s '%s'%s"%(self.__location, self.__label, CR)
        return text

    def getLink(self, fname, building_mode=BUILDING_MODE_BOOK):
        if building_mode == BUILDING_MODE_BOOK:
            return relpath(fname, self.__location)
        elif building_mode == BUILDING_MODE_NODE:
            return relpath(fname, dirname(self.__location))
        elif building_mode == BUILDING_MODE_ALL:
            return relpath(fname, self.__home)
        else:
            raise Exception("bad building mode!")

    def getLineTags(self, line, building_mode=BUILDING_MODE_BOOK):
        tags = line.getTags()[:]
        if building_mode == BUILDING_MODE_BOOK:
            pass
        elif building_mode == BUILDING_MODE_NODE or building_mode == BUILDING_MODE_ALL:
            tags.append(basename(self.__location))
        else:
            raise Exception("bad building mode!")
        return tags

    def getTags(self, building_mode=BUILDING_MODE_BOOK):
        if building_mode == BUILDING_MODE_BOOK:
            return self.__tags
        elif building_mode == BUILDING_MODE_NODE or building_mode == BUILDING_MODE_ALL:
            tag = toSnakeCase(basename(self.__location))
            
            
            return self.__tags
            
            
            
            if not tag in self.__tags:
                return self.__tags[:] + [tag]
            else:
                return self.__tags[:]
        else:
            raise Exception("bad building mode!")
        return tags

    def getJsPopulate(self, building_mode=BUILDING_MODE_BOOK):
        text = EMPTY_STRING
        for line in self:
            if line.getTitle() != EMPTY_STRING:
                mp3s = []
                for mp3 in line.getMp3s():
                    mp3name = self.getLink(mp3.getFname(), building_mode=building_mode)
                    tup = tupleToJavascript([mp3name, mp3.getGenre()], header="new mp3File", text_mode=True)
                    mp3s.append(tup)
                js_mp3s = listToJavascript(mp3s, text_mode=False)
                
                scores = []
                for score in line.getScores():
                    scorename = self.getLink(score.getFname(), building_mode=building_mode)
                    nb_pages = score.getNumberOfPages()
                    tup = tupleToJavascript(['"%s"'%scorename, '"%s"'%score.getInstrument(), str(nb_pages)], header="new scoreFile", text_mode=False)
                    scores.append(tup)
                js_scores = listToJavascript(scores, text_mode=False)

                tags = self.getLineTags(line, building_mode=building_mode)
                js_tags = listToJavascript(tags, text_mode=True)
                
                tup = tupleToJavascript([ '"%s"'%line.getTitle(), '"%s"'%line.getShortName(), js_mp3s, js_scores, js_tags], header = "new item")
                
                text += functionToJavascript("addItem", (tup,)) + ";" + CR
        return text

    def createHtmlPage(self):
        js_code = commentToJavascript(getTimestamp())
        js_code += 'document.title = "%s";%s'%(self.getLabel(), CR)
        js_code += self.getJsPopulate(building_mode=BUILDING_MODE_BOOK)
        js_code += variableToJavascript("tagLabel", listToJavascript(self.getTags(building_mode=BUILDING_MODE_BOOK), text_mode=True))

        fname = join(dirname(self.getFname()), WEB_PAGE_NAME)
        saveHtmlPage(fname, js_code, self.getTags())

    def getLines(self):
        text = EMPTY_STRING
        for line in self:
            text += line.getTitle()
            if line.hasTags():
                text += " # " + SPACE.join(line.getTags())
            text += CR
        return text
        
    def removeLinebyTitle(self, title):
        for x, line in enumerate(self):
            if line.getTitle == title:
                #~ print (str(line) + " REMOVED")
                del(self[x])
                self.setModifiedFlag()
                return True
        return False

class NODE(list):
    # a list of BOOK()
    def __init__(self, home, location, *args, **kwds):
        super().__init__(*args, **kwds)
        self.__home = home # adresse absolue du site
        self.__location = location # adresse absolue du noeud
        self.__node_name = basename(location) # nom du noeud
        self.__label = camelCaseToSentence(self.__node_name) # label du noeud
        self.__books = []
        self.__tags = None

    def getHome(self):
        return self.__home
    
    def getLocation(self):
        return self.__location
        
    def getDirname(self):
        return self.__node_name
        
    def getLabel(self):
        return self.__label
        
    def addBook(self, book):
        self.append(book)

    def getLink(self):
        return relpath(self.getLocation(), self.getHome())

    def getTags(self):
        if self.__tags == None:
            self.__tags = []
            for book in self:
                for tag in book.getTags(building_mode=BUILDING_MODE_NODE):
                    if not tag in self.__tags:
                        self.__tags.append(tag)
        return self.__tags

    def createHtmlPage(self):
        js_code = commentToJavascript(getTimestamp())
        js_code += 'document.title = "%s";%s'%(self.getLabel(), CR)
        for book in self:
            js_code += book.getJsPopulate(building_mode=BUILDING_MODE_NODE)
        js_code += "items = sortItems(items);%s"%CR

        fname = join(self.getLocation(), WEB_PAGE_NAME)
        saveHtmlPage(fname, js_code, self.getTags())

    def __str__(self):
        text = "NODE %s (%u)%s"%(self.__location, len(self), CR)
        for book in self:
            text += "    " + str(book)
        return text

class FOLDERS(list):
    # a list of NODES()
    def __init__(self, home, *args, **kwds):
        self.__ignore_prefixed_items = True
        if "ignore_prefixed_items" in kwds:
            self.__ignore_prefixed_items = kwds["ignore_prefixed_items"]
            del kwds["ignore_prefixed_items"]
            if not self.__ignore_prefixed_items:
                #~ print("on ne prend pas les dossiers/fichiers cachés")
                pass
        
        super().__init__(*args, **kwds)
        self.__home = home
        if isbook(self.__home):
            raise Exception("root level can't be a book!")
        self.parseHome(self.__home)
        self.__tags = None
        self.__lines = None

    def hasToBeIgnored(self, fname):
        # si l'utilisateur veut exclure les dossiers/fichiers "perso" (préfixés "_")
        if not self.__ignore_prefixed_items:
            if basename(fname).startswith("_"):
                #~ print("hidden => %s" % fname)
                return True
        # les dossiers Linux "cachés" (commencent par ".") ne sont pas bloqués
        #~ print("not hidden => %s" % fname)
        return False

    def parseHome(self, current_dir, deep=0):
        for item in listdir(current_dir):
            fname = join(current_dir, item)
            if self.hasToBeIgnored(fname):
                continue

            if isnode(fname):
                node = NODE(self.__home, fname)
                self.append(node)
                for subitem in listdir(fname):
                    subpath = join(node.getLocation(), subitem)
                    if self.hasToBeIgnored(subpath):
                        continue
                    if isbook(subpath):
                        book = BOOK(self.__home, subpath)
                        node.addBook(book)
            elif isdir(fname):
                self.parseHome(fname, deep=deep + 1)
                        
    def getFolderByName(self, folder_name):
        for folder in self:
            if os.path.basename(folder.getLocation()) == folder_name:
                return folder

    def getHome(self):
        return self.__home

    def getNodes(self):
        return self.__nodes

    def getInstruments(self):
        instruments = []
        for line in self[1:]:
            for tracklist in self:
                items = tracklist.getInstruments()
                for instrument in items:
                    if not instrument in instruments:
                        instruments.append(instrument)
        instruments.sort()
        return instruments

    def getTags(self):
        if self.__tags == None:
            self.__tags = []
            for node in self:
                #~ if not toSnakeCase(node.getFolderName()) in tags:
                    #~ tags.append(toSnakeCase(folder.getFolderName()))
                for tag in node.getTags():
                    if not tag in self.__tags:
                        self.__tags.append(tag)
            self.__tags.sort()
        return self.__tags

    def getcatalogLinks(self):
        text = EMPTY_STRING
        links = []
        for node in self.getNodes():
            text += os.path.relpath(self.getHome(), os.path.join(node.getLocation(), RELEASE_WEB_PAGE_NAME)) + CR
        return text

    def makeCatalog(self):
        js_code = text = commentToJavascript(getTimestamp())
        js_code += variableToJavascript("document.title", MA_NAME, no_prefix=True, text_mode=True)

        # root level
        link = LINK(MA_NAME, self.getHome(), deep = ROOT_DEEP)
        obj = functionToJavascript("new catalogLink", [link.getLabel(), link.getUrl(), link.getDeep()], text_mode=True)
        js_code += functionToJavascript("addCatalogLink", [obj]) + ";" + CR

        for node in self.getNodes():
            link = node.getLink(self.__home)
            #~ print(link)
            obj = functionToJavascript("new catalogLink", [link.getLabel(), link.getUrl(), link.getDeep()], text_mode=True)
            js_code += functionToJavascript("addCatalogLink", [obj]) + ";" + CR
            #~ stuff += node.getLink(self.getHome()) + HTML_CR
            for tracklist in node.getTracklists():
                #~ stuff += tracklist.getLink(self.getHome()) + HTML_CR
                link = tracklist.getLink()
                #~ print(link)

                obj = functionToJavascript("new catalogLink", [link.getUrl(), link.getLabel(), link.getDeep()], text_mode=True)
                js_code += functionToJavascript("addCatalogLink", [obj]) + ";" + CR

        body = open(NIGHTLY_BUILD_CATALOG_SKELETON_NAME, "r", encoding='utf-8').read(-1)
        body = body.replace(STUFF_TAG, js_code)
        
        #~ fname = WEB_CATALOG_NAME
        fname = os.path.join(self.getHome(), CATALOG_FNAME)
        open(fname, "w", encoding='utf-8').write(body)

    def getPopulateItemsJavascript(self, node=None):
        js_code = EMPTY_STRING
        nodes = self.getNodes()
        if node == None:
            for node in nodes:
                #~ js_code += "%s node: %s%s"%(JAVASCRIPT_COMMENT, node.getLabel(), CR)
                js_code += commentToJavascript("node: %s"%(node.getLabel()))
                for tracklist in node.getTracklists():
                    #~ js_code += "%s tracklist: %s%s"%(JAVASCRIPT_COMMENT, tracklist.getFolderName(), CR)
                    js_code += commentToJavascript("tracklist: %s"%(tracklist.getFolderName()))
                    js_code += tracklist.getPopulateItemsJavascript(node.getLocation(), tags=[toSnakeCase(tracklist.getFolderName())])
        else:
            js_code += "%s node: %s%s"%(JAVASCRIPT_COMMENT, node.getLabel(), CR)
            for tracklist in node.getTracklists():
                js_code += "%s tracklist: %s%s"%(JAVASCRIPT_COMMENT, tracklist.getFolderName(), CR)
                js_code += tracklist.getPopulateItemsJavascript(node.getLocation(), tags=[toSnakeCase(tracklist.getFolderName())])
            #~ if node != None:
                #~ js_code += "items = sortItems(items);%s"%CR
        return js_code

    def getJavascript(self, node=None):
        text = "%s %s%s"%(JAVASCRIPT_COMMENT, getTimestamp(), CR)
        text += 'document.title = "%s";%s'%(MA_NAME, CR)

        text += self.getPopulateItemsJavascript(node)

        text += variableToJavascript("tagLabel", listToJavascript(self.getTags(), text_mode=True))

        text += translateInstrumentsToJavascript()
        return text

    def __str__(self):
        text =  "root:%s"%self.getHome() + CR
        for tracklist in self:
            text += str(tracklist)
        return text

    def createHtmlCatalog(self):
        js_code = commentToJavascript(getTimestamp())

        obj = functionToJavascript("new catalogLink", [MA_NAME, WEB_PAGE_NAME, 0], text_mode=True)
        js_code += functionToJavascript("addCatalogLink", [obj]) + ";" + CR
        
        for node in self:
            link = join(node.getLink(), WEB_PAGE_NAME)
            label = node.getLabel()
            obj = functionToJavascript("new catalogLink", [label, link, 1], text_mode=True)
            js_code += functionToJavascript("addCatalogLink", [obj]) + ";" + CR
            
            for book in node:
                link = join(dirname(book.getLink(book.getFname(), building_mode=BUILDING_MODE_ALL)), WEB_PAGE_NAME)
                label = book.getLabel()
                obj = functionToJavascript("new catalogLink", [label, link, 2], text_mode=True)
                js_code += functionToJavascript("addCatalogLink", [obj]) + ";" + CR
                
        body = open(NIGHTLY_BUILD_CATALOG_SKELETON_NAME, "r", encoding='utf-8').read(-1)
        body = body.replace(STUFF_TAG, js_code)

        fname = join(self.__home, CATALOG_FNAME)
        open(fname, "w", encoding='utf-8').write(body)
        fname = join("temp/test.txt")
        open(fname, "w", encoding='utf-8').write(body)
        report("HTML catalog '%s' created"%fname)

    def createHtmlPage(self, web_page_name=WEB_PAGE_NAME):
        js_code = commentToJavascript(getTimestamp())
        js_code += 'document.title = "%s";%s'%(MA_NAME, CR)
        for node in self:
            for book in node:
                js_code += book.getJsPopulate(building_mode=BUILDING_MODE_ALL)
        js_code += "items = sortItems(items);%s"%CR
        js_code += variableToJavascript("tagLabel", listToJavascript(self.getTags(), text_mode=True))
            
        fname = join(self.getHome(), web_page_name)
        saveHtmlPage(fname, js_code, self.getTags())
        
    def getDoublons(self):
        titles = {}
        doublons = {}
        
        for node in self:
            for book in node:
                for line in book:
                    title = line.getTitle()
                    book = basename(line.getLocation())
                    if title in titles.keys():
                            #doublon!
                            if title in doublons.keys():
                                doublons[title].append(book)
                            else:
                                doublons[title] = [book, titles[title]]
                    else:
                        titles[title] = book
        return doublons

    def createAllHtmlPages(self, web_page_name=WEB_PAGE_NAME):
        self.multiToSinglePdfPage()
        self.createHtmlPage(web_page_name)
        for node in self:
            node.createHtmlPage()
            for book in node:
                scoreUpdate(book.getLocation())
                book.createHtmlPage()
    
    def getLines(self):
        if self.__lines == None:
            lines = []
            for node in self:
                for book in node:
                    for line in book:
                        lines.append(line)
            #~ self.__lines = lines
            self.__lines =  sorted(lines, key=lambda line: line.getTitle().lower())
        return self.__lines

    def makePdfBook(self, instrument="DO", fname=None, family=[], tags=[]):
        #~ if instrument.lower() == "all":
            
        # let's create a book for an instrument or a member of its family if instrument doesn't exists
        if fname == None:
            fname = os.path.join(work_dir, SCORE_FOLDER, "book_%s.pdf"%instrument)
        score_names = []
        for line in self.getLines():
            # lets filter by tags
            if len(tags) != 0:
                for tag in line.getTags():
                    if tag in tags:
                        if line.hasInstrument(instrument):
                            #~ print(line.getTitle(), instrument)
                            score_names.append(line.getScore(instrument).getFname())
                        break
            else:
                # no line is filtered
                if line.hasInstrument(instrument):
                    #~ print(line.getTitle(), instrument)
                    score_names.append(line.getScore(instrument).getFname())
            
        concatenatePdfs(score_names, fname)

    def detectMultiPagespdf(self):
        for line in self.getLines():
            for score in line.getScores():
                pdf_reader = PyPDF2.PdfReader(score.getFname())
                if len(pdf_reader.pages) > 1:
                    #~ print (score.getFname())
                    pass

    def multiToSinglePdfPage(self):
        for line in self.getLines():
            for score in line.getScores():
                #~ print(score.getFname())

                if score.getFname() == None:
                    raise Exception("tu tu tu tut!")
                try:
                    pdf_reader = pypdf.PdfReader(score.getFname())
                except:
                    raise Exception("error reading %s"%score.getFname())
                    continue
                    
                if len(pdf_reader.pages) > 1:
                    for pnum, page in enumerate(pdf_reader.pages):
                        pdf_writer = pypdf.PdfWriter()
                        pdf_writer.add_page(page)
                        
                        #~ output_file_name = f'page_{page_num + 1}.pdf'
                        folder = dirname(score.getFname())
                        fname = basename(score.getFname())
                        fname = fname[:-4] + "%02u"%(pnum+1) + fname[-4:]
                        #~ print(dirname(score.getFname()), fname)
                        output_fname = join(folder,fname)
                        if pnum == 0:
                            default_fname = output_fname

                        with open(output_fname, 'wb') as output_file:
                            pdf_writer.write(output_file)
                    os.remove(score.getFname())
                    shutil.move(default_fname, score.getFname())
                    

    def getBook(self, book_name, node_name=None):
        for node in self:
            for book in node:
                if book.getDirname() == book_name:
                    if node_name == None:
                        return book
                    elif node_name == node.getDirname():
                        return book
        return None

    def getNode(self, node_name):
        for node in self:
            if node_name == node.getDirname():
                return node
        return None

    def createTrace(self, fname="temp/trace.txt"):
        TAB = "    "
        
        text = EMPTY_STRING    
        for node in self:
            deep = 0
            margin = TAB * deep
            text += margin + "<<%s>>"%node.getLabel() +  CR
            for book in node:
                deep = 1
                margin = TAB * deep
                text += margin + "<%s>"%book.getLabel() +  CR

                for line in book:

                    deep = 2
                    margin = TAB * deep
                    text += margin + line.getTitle() +  CR
                    
                    sn = line.getShortName()
                    deep = 3
                    margin = TAB * deep
                    text += margin + "SHORT_NAME : " +  sn + CR

                    if line.isAlias():
                        deep = 3
                        margin = TAB * deep
                        text += margin + "ALIAS : " +  line.getAlias() + CR

                    tags = line.getTags()
                    if len(tags) > 0:
                        deep = 3
                        margin = TAB * deep
                        text += margin + "TAGS : " +  SPACE.join(tags) + CR

                    scores = line.getScores()
                    if len(scores) > 0:
                        deep = 3
                        margin = TAB * deep
                        items = [score.getInstrument() for score in scores]
                        text += margin + "SCORES : " + SPACE.join(items) +  CR

                    mp3s = line.getMp3s()
                    if len(mp3s) > 0:
                        deep = 3
                        margin = TAB * deep
                        items = [mp3.getGenre() for mp3 in mp3s]
                        text += margin + "AUDIO : " + SPACE.join(items) +  CR
            text += CR

        open(fname, "w", encoding="utf-8").write(text)
        return text

def xx_toCamelCase(text):
    """a raw way to get camelCase"""
    text = text.lower()
    text = str(text).replace(SPACE+SPACE, SPACE)
    #~ text = unidecode.unidecode(text).replace(SPACE+SPACE, SPACE)
    position = text.find('(')

    temp = EMPTY_STRING
    space_flag = False
    
    for car in text:
        if car in ("' /-!,?:+"):
            # these characters need a new word
            space_flag = True
        elif car in "().":
            pass
            # these characters are simply ignored
        else:
            if space_flag:
                temp += car.upper()
            else:
                temp += car.lower()
            space_flag = False
    return temp

def camelCaseToSentence(camel):
    sentence = EMPTY_STRING
    for car in camel:
        if car in "ACBDEFGHIJKLMNOPQRSTUVWXYZ":
            sentence += SPACE + car.lower()
        else:
            sentence += car
    sentence = sentence.strip()
    return sentence[0].upper() + sentence[1:]

def toSnakeCase(text):
    # generated by chatty
    result = []
    for i, char in enumerate(text):
        if char.isupper() and i > 0 and text[i-1].islower():
            result.append('_')
        elif not char.isalnum():
            result.append('_')
            continue
        result.append(char.lower())
    return ''.join(result)

def getTimestamp():
    return datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")

def addDirectory(dir_name):
    directory_path = pathlib.Path(dir_name)
    try:
        directory_path.mkdir(parents=True, exist_ok=True)
        #~ print(f"Directory '{directory_path}' created successfully")
    except OSError as error:
        error(f"Error creating directory '{directory_path}': {error}")

def createFolder(location, folder_name, page_name):
    full_folder_name = os.path.join(location, folder_name)
    if os.path.isdir(full_folder_name):
        raise Exception("folder '%s' already exists!"%full_folder_name)
    elif os.path.isfile(full_folder_name):
        raise Exception("unexpected file '%s'!"%full_folder_name)
    else:
        addDirectory(full_folder_name)
        open(os.path.join(full_folder_name, TRACKLIST_NAME), "w", encoding='utf-8').write("%s %s%s"%(UTF8_TEXT, page_name, CR))
        for item in ((os.path.join(full_folder_name, MP3_FOLDER), MP3_DEFAULT_TYPES),
                     (os.path.join(full_folder_name, SCORE_FOLDER), SCORE_DEFAULT_TYPES)):
            addDirectory(item[0])
            for itype in item[1]:
                addDirectory(os.path.join(item[0], itype))

def createAllPages(home):
    # returns anyway an object of class FOLDERS
    folders = FOLDERS(home)
    #~ for node in folders.getNodes():
        #~ folders.makeNodePage(node) # a node of several tracklists
    for tracklist in folders:
        tracklist.makeLocalPage(home) # just a tracklist
    #~ folders.makeGlobalPage() # all what is in Musician Assistant
    
    #~ folders.makeCatalog()
    return folders

def sortLines(lines):
    return sorted(items, key=lambda item: item.getLowerTitle())
    
def concatenatePdfs(input_files, output_file, simul=False):
    if len(input_files) == 0:
        report("no score to make pdf %s"%(output_file))
        return
    
    report("generating %s - %u pages"%(output_file, len(input_files)))
    pdf_writer = PyPDF2.PdfWriter()
    for input_file in input_files:
        # let's add scores one by one
        with open(input_file, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                pdf_writer.add_page(page)

    # let's save the whole book
    if os.path.isfile(output_file):
        os.rename(output_file, "%s.%s"%(output_file, "%d"%time.time()))
    with open(output_file, 'wb') as output:
        pdf_writer.write(output)

def xx_makePdfBook(items, instrument="DO", fname=None, family=[], tags=[]):
    if instrument.lower() != "all":
        # let's create a book for an instrument or a member of its family if instrument doesn't exists
        if fname == None:
            fname = os.path.join(work_dir, SCORE_FOLDER, "book_%s.pdf"%instrument)
        score_names = []
        for item in items:
            # lets filter by tags
            ok = True
            if len(tags) != 0:
                ok = False
                for tag in item.getTags():
                    if tag in tags:
                        ok = True
                        break
            
            if ok:
                if instrument in C_INSTRUMENTS:
                    instrument_to_add = getItemSelectedInstrument(item, instrument, family=C_INSTRUMENTS)
                elif instrument in BB_INSTRUMENTS:
                    instrument_to_add = getItemSelectedInstrument(item, instrument, family=BB_INSTRUMENTS)
                elif instrument in EB_INSTRUMENTS:
                    instrument_to_add = getItemSelectedInstrument(item, instrument, family=BB_INSTRUMENTS)
                else:
                    instrument_to_add = getItemSelectedInstrument(item, instrument, family=family)
                    
                if instrument_to_add != None:
                    score_names.append(item.getScoreName(instrument_to_add))
                else:
                    warning("nothing found for song %s's %s"%(item.getTitle(), instrument))
        concatenatePdfs(score_names, fname)
    else:
        # let's create a book for each instrument
        for instrument in INSTRUMENTS:
            fname = os.path.join(work_dir, SCORE_FOLDER, "book_%s.pdf"%instrument)
            score_names = []
            for item in items:
                instrument_to_add = getItemSelectedInstrument(item, instrument)
                if instrument_to_add != None:
                    score_names.append(item.getScoreName(instrument))
                else:
                    pass # nothing found
            concatenatePdfs(score_names, fname)

# for compatibility with old version
def translateInstrumentsToJavascript():
    text = EMPTY_STRING
    family_names = []
    
    for (family_name, family) in (("C_INSTRUMENTS", C_INSTRUMENTS),
        ("BB_INSTRUMENTS", BB_INSTRUMENTS),
        ("EB_INSTRUMENTS", EB_INSTRUMENTS),
        ("BASS_INSTRUMENTS", BASS_INSTRUMENTS),
        ("VOCALS_INSTRUMENTS", VOCALS_INSTRUMENTS)):
        text += "const %s = [%s];\n"%(family_name, ", ".join(['"%s"'%item for item in family]))
        family_names.append(family_name)
    text += "const %s = [%s];\n"%("INSTRUMENTS_FAMILY_NAMES", ", ".join(family_names))
    text += "const %s = [%s];\n"%("instruments", ", ".join(['"%s"'%item for item in instruments]))
    return text


def updateAccepted(report_text, book):
    root = tk.Tk()
    root.withdraw()  # Cache la fenêtre principale
    reponse = messagebox.askquestion("mise à jour scores '%s'"%book, report_text)
    root.destroy()
    if reponse == 'yes':
        return True
    else:
        return False

def scoreUpdate(book_name):
    """ Mise à jour des fichiers PDF """
    book_location = book_name
    #~ print("---%s---\n\n"%book_location)
    source_folder = os.path.join(book_location, UPDATE_FOLDER)
    report_text = EMPTY_STRING
    nb_files = 0
    for real in (False, True):
        if os.path.isdir(source_folder):
            for filename in os.listdir(source_folder):
                if filename.endswith(PDF_EXTENSION):
                    if "-" in filename:
                        short_title, instrument = os.path.splitext(filename)[0].split("-")
                        instrument = instrument.strip()
                        short_title = short_title.strip()
                        if instrument.startswith("Instrument_"):
                            instrument = instrument[len("Instrument_"):]
                        elif instrument.startswith("Basse_"):
                            instrument = "b" + instrument[1:]
                        else:
                            instrument = instrument.lower()
                        if not real:
                            nb_files += 1
                        
                        instrument_location = os.path.join(book_location, SCORE_FOLDER, instrument)
                        if not os.path.isdir(instrument_location):
                            if not real:
                                report_text += "%s's %s%s"%(short_title, instrument, CR)

                        if real:
                            source = os.path.join(book_location, UPDATE_FOLDER, filename)
                            target_dir = os.path.join(book_location, SCORE_FOLDER, instrument)
                            target = os.path.join(target_dir, short_title+PDF_EXTENSION)
                            
                            #~ print("%s -> %s"%(source, target))
                            os.makedirs(target_dir, exist_ok=True)
                            shutil.copyfile(source, target)
                            
                            #~ print("deleting %s"%(source))
                            os.remove(source)
                    
            if not real:
                if nb_files != 0:
                    if not updateAccepted(report_text, book_name):
                        return

def getInstrumentTrackList(instrument, folders, is_missing=False):
    lines = []
    for folder in folders:
        for book in folder:
            for song in book:
                found = False
                for score in song.getScores():
                    if "easytrombone" in score.getFname():
                        found = True
                        break
                if not found:
                    if is_missing:
                        lines.append(song)
                else:
                    if not is_missing:
                        lines.append(song)
    return lines

if __name__ == "__main__":

    sys.stdout.write("%s - v%s - Please use this script as a library, no interest in launching it.\n"%(MA_NAME, MA_VERSION))

    print(toCamelCase("Grandfather’s Clock"))