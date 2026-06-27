#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
scripts_path = os.path.join(parent_dir, "scripts")
if scripts_path not in sys.path:
    sys.path.insert(0, scripts_path)

def genericTests(database):
    # mauvais dossier
    assert None == getScoreName(database + 'azerty', 'violon')
    #mauvais instrument
    assert None == getScoreName(database + 'balladeSurUneClaveAfricaine', 'azerty')
    # aucune partition dans le track
    assert None == getScoreName(database + 'utest', 'trompette')

def testgetSubstituedComboInstrument(database):
    index = 1
    for trackname, instrument, vn, substitued, in (
        ("balladeSurUneClaveAfricaine", "basse", 1, "basse"),
        ("balladeSurUneClaveAfricaine", "DO", 1,  "DO"),
        ("balladeSurUneClaveAfricaine", "MIb", 1,  "MIb"),
        ("balladeSurUneClaveAfricaine", "SIb", 1,  "SIb"),
        ("balladeSurUneClaveAfricaine", "trombone",  1, "trombone"),
        ("balladeSurUneClaveAfricaine", "cor_fa",  1, None),
        ("balladeSurUneClaveAfricaine", "piano",  1, "piano"),
        ("balladeSurUneClaveAfricaine", "sax_alto",  1, "MIb"),
        ("balladeSurUneClaveAfricaine", "sax_baryton",  1, "MIb"),
        ("balladeSurUneClaveAfricaine", "clarinette_mib",  1, "MIb"),
        ("balladeSurUneClaveAfricaine", "batterie",  1, "batterie"),
        ("balladeSurUneClaveAfricaine", "claves",  1, "claves"),
        ("balladePourAmira","piano", 1, "piano"),
        ("balladePourAmira","guitare", 1, "piano"),
        ("balladePourAmira","clarinette", 1, None),
        ("funDingo","flute", 1, "DO"),
        ("funDingo","flute", 2, "DO2"),
        ("funDingo","guitare", 1, "piano"),
        ("funDingo","guitare", 2, "piano"),
        ("funDingo","guitare", 2, "piano"),
        ):
        
        result = getScoreName(database + trackname, instrument, voice=vn, mode=MODE_POPULAR,)
        if result != substitued:
            print("ERROR testing", trackname, instrument, "voice", vn, "attendu:", substitued, "reçu:",result, "ligne:", index)
            print(getScoreNameError())
            sys.exit(1)

        index += 1

def testgetSubstituedOrchestreInstrument(database):
    index = 1
    for trackname, instrument, vn, substitued, in (
        ("balladeSurUneClaveAfricaine", "basse", 1, "basse"),
        ("balladeSurUneClaveAfricaine", "DO", 1,  "DO"),
        ("balladeSurUneClaveAfricaine", "MIb", 1,  "MIb"),
        ("balladeSurUneClaveAfricaine", "SIb", 1,  "SIb"),
        ("balladeSurUneClaveAfricaine", "trombone",  1, "trombone"),
        ("balladeSurUneClaveAfricaine", "cor_fa",  1, None),
        ("balladeSurUneClaveAfricaine", "piano",  1, "piano"),
        ("balladeSurUneClaveAfricaine", "sax_alto",  1, "MIb"),
        ("balladeSurUneClaveAfricaine", "sax_baryton",  1, "MIb"),
        ("balladeSurUneClaveAfricaine", "clarinette_mib",  1, "MIb"),
        ("balladeSurUneClaveAfricaine", "batterie",  1, "batterie"),
        ("balladeSurUneClaveAfricaine", "claves",  1, "claves"),
        ("balladePourAmira","piano", 1, "piano"),
        ("balladePourAmira","guitare", 1, None), #pas d'instrument à part piano, remplacement impossible en classique
        ("balladePourAmira","clarinette", 1, None),
        ("funDingo","DO", 1, "DO"),
        ("funDingo","DO", 2, "DO2"),
        ("elSextoCubano","flute", 1, "flute"),
        ("elSextoCubano","flute", 2, "flute2"),
        ("elSextoCubano","flute", 4, "flute2"),
        ("crocheManquanteLa","contrebasse", 1, "basse"),
        ):
        
        result = getScoreName(database + trackname, instrument, voice=vn, mode=MODE_CLASSIQUE,)
        if result != substitued:
            print("ERROR testing", trackname, instrument, "voice", vn, "attendu:", substitued, "reçu:",result, "ligne:", index)
            print(getScoreNameError())
            sys.exit(1)

        index += 1

if __name__ == "__main__":

    print("U N I T A R Y    T E S T")

    from getScoreName import getScoreName, MODE_POPULAR, MODE_CLASSIQUE, getScoreNameError, GROUP_BASSE, GROUP_POMPE
    DATABASE = "../../backNScoreData/database/bands/pierreFaller/"
    
    genericTests(DATABASE)

    testgetSubstituedComboInstrument(DATABASE)
    
    testgetSubstituedOrchestreInstrument(DATABASE)
    
    print("\n\nA L L   U N I T A R Y    T E S T S   P A S S E D !")
