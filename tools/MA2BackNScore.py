   #!/usr/bin/python
# -*- coding: utf-8 -*-

from MA import *

TRACK_NAME = "trackname.txt"
MP3_EXTENSION = ".mp3"

def createDir(*path):
    new_path = SPACE
    for item in path:
        new_path = os.path.join(new_path, item)
    os.makedirs(new_path, exist_ok=True)
    return new_path

def createStuff(source, target, line):
    textfile_name = os.path.join(target, TRACK_NAME)
    with open(textfile_name, "w") as fp:
        fp.write(line.getTitle())
        tags = line.getTags()
        if len(tags) > 0:
            fp.write(CR + SPACE.join(tags))
        else:
            fp.write(CR)

    for score in line.getScores():
        score_source = score.getFname()
        score_target = os.path.join(target, "%s%s"%(score.getInstrument(), PDF_EXTENSION))
        shutil.copy(score_source, score_target)
        # managing score's pages whose number is not one
        for page_num in range(1, score.getNumberOfPages()):
            filename, ext = os.path.splitext(score.getFname())
            score_source = filename + "%02u"%(page_num + 1) + PDF_EXTENSION
            score_target = os.path.join(target, "%s%02u%s"%(score.getInstrument(), page_num + 1, PDF_EXTENSION))
            if REAL:
                if os.path.isfile(score_source):
                    shutil.copy(score_source, score_target)
                else:
                    raise Exception("score %s doesn't exist"%score_source)
            else:
                print(score_source, score_target)

    for mp3 in line.getMp3s():
        try:
            mp3_source = mp3.getFname()
            mp3_genre = mp3.getGenre()
            if not mp3_genre in ("backtrack", "melody"):
                sys.stdout.write("<%s>"%mp3_genre)
            mp3_target = os.path.join(target, "%s%s"%(mp3.getGenre(), MP3_EXTENSION))
            shutil.copy(mp3_source, mp3_target)
        except:
            print("%s NO MP3"%line.getTitle())

    return line.getTitle()

if __name__ == "__main__":

    REAL = True

    HOME = "/mnt/Data1/Documents/www/free/shared/repertoires/home"
    TARGET = "/mnt/Data1/Documents/backNScore/database"
    folders = FOLDERS(HOME)
    
    nb = 0
    for node in folders:
        createDir(TARGET, node.getDirname())
        for book in node:
            source = createDir(TARGET, node.getDirname(), book.getDirname())
            for line in book:
                target = createDir(TARGET, node.getDirname(), book.getDirname(), line.getShortName())
                createStuff(source, target, line)
                sys.stdout.write(".")
                nb += 1
                if (nb%80) == 0:
                    sys.stdout.write("\n")

    print("Terminated without error", getTimestamp(), " duration :", getDuration())
