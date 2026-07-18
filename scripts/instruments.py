#!/usr/bin/python
# -*- coding: utf-8 -*-

INSTRUMENTS = {
"flute": ("DO","SOL","0","BOIS"),
"flute_piccolo": ("DO","SOL","1","BOIS"),
"flute_piccolo_reb": ("REb","SOL","1","BOIS"),
"flute_alto": ("SOL","SOL","0","BOIS"),
"recorder": ("DO","SOL","0","BOIS"),
"recorder_alto": ("FA","SOL","0","BOIS"),
"recorder_tenor": ("DO","SOL","0","BOIS"),
"clarinette": ("SIb","SOL","0","BOIS"),
"clarinette_mib": ("MIb","SOL","0","BOIS"),
"clarinette_alto": ("MIb","SOL","-1","BOIS"),
"clarinette_basse": ("SIb","SOL","-1","BOIS"),
"sax_soprano": ("SIb","SOL","0","BOIS"),
"sax_alto": ("MIb","SOL","0","BOIS"),
"sax_tenor": ("SIb","SOL","-1","BOIS"),
"sax_baryton": ("MIb","SOL","-1","BOIS"),
"sax_melody": ("DO","SOL","-1","BOIS"),
"hautbois": ("DO","SOL","0","BOIS"),
"basson": ("DO","FA","-1","BOIS"),
"accordeon": ("DO","SOL","0","HANCHES_LIBRES"),
"bandoneon": ("DO","SOL","0","HANCHES_LIBRES"),
"harmonica_chromatique": ("DO","SOL","0","HANCHES_LIBRES"),
"melodica": ("DO","SOL","0","HANCHES_LIBRES"),
"horn_alto": ("MIb","SOL","0","CUIVRES"),
"horn_tenor": ("SIb","SOL","-1","CUIVRES"),
"horn_tenor_do_keyF": ("DO","FA","-1","CUIVRES"),
"horn_baryton": ("SIb","SOL","-1","CUIVRES"),
"horn_baryton_sib_keyF": ("SIb","FA","-1","CUIVRES"),
"horn_baryton_do_keyF": ("DO","FA","-1","CUIVRES"),
"horn_baryton_do": ("DO","SOL","-1","CUIVRES"),
"horn_baryton_do_keyF": ("DO","FA","-1","CUIVRES"),
"horn_baryton_keyF": ("SIb","FA","-1","CUIVRES"),
"baryton": ("SIb","SOL","-1","CUIVRES"),
"euphonium": ("SIb","SOL","-1","CUIVRES"),
"euphonium_keyF": ("SIb","FA","-1","CUIVRES"),
"euphonium_do_keyG": ("DO","SOL","-1","CUIVRES"),
"euphonium_do_keyF": ("DO","FA","-1","CUIVRES"),
"cor_mib": ("MIb","SOL","0","CUIVRES"),
"cor_fa": ("FA","SOL","0","CUIVRES"),
"cor_sib": ("SIb", "SOL", "-1", "CUIVRES"),
"cornet": ("SIb","SOL","0","CUIVRES"),
"bugle": ("SIb","SOL","0","CUIVRES"),
"bugle_do": ("DO","SOL","0","CUIVRES"),
"clairon": ("SIb","SOL","0","CUIVRES"),
"trompette_de_cavalerie": ("MIb","SOL","0","CUIVRES"),
"trompette": ("SIb","SOL","0","CUIVRES"),
"trompette_piccolo": ("SIb","SOL","1","CUIVRES"),
"trompette_do": ("DO","SOL","0","CUIVRES"),
"trompette_la": ("LA","SOL","0","CUIVRES"),
"trompette_mib": ("MIb","SOL","0","CUIVRES"),
"trombone": ("DO","FA","-1","CUIVRES"),
"trombone_keyG": ("DO","SOL","-1","CUIVRES"),
"trombone_sib": ("SIb","SOL","-1","CUIVRES"),
"trombone_sib_keyF": ("SIb","FA","-1","CUIVRES"),
"easytrombone": ("DO","SOL","-1","CUIVRES"),
"trombone_tenor": ("DO","FA","-1","CUIVRES"),
"trombone_basse": ("DO","FA","-1","CUIVRES"),
"trombone_basse_sib": ("SIb","FA","-1","CUIVRES"),
"trombone_basse_sib_keyG": ("SIb","SOL","-1","CUIVRES"),
"basse_fretless": ("DO","FA","-2","CORDES_PINCEES"),
"basse": ("DO","FA","-2","CORDES_PINCEES"),
"basse_keyG": ("DO","SOL","-2","CORDES_PINCEES"),
"contrebasse": ("DO","FA","-2","CORDES_FROTTEES"),
"mandocello": ("DO","FA","-2","CORDES_PINCEES"),
"basse_sib": ("SIb","FA","-1","CUIVRES"),
"basse_sib_keyG": ("SIb","SOL","-1","CUIVRES"),
"basse_mib": ("MIb","FA","-1","CUIVRES"),
"basse_mib_keyG": ("MIb","SOL","-1","CUIVRES"),
"tuba": ("DO","FA","-2","CUIVRES"),
"tuba_keyG": ("DO","SOL","-2","CUIVRES"),
"tuba_sib": ("SIb","FA","-2","CUIVRES"),
"tuba_sib_keyG": ("SIb","SOL","-2","CUIVRES"),
"tuba_mib": ("MIb","FA","-2","CUIVRES"),
"tuba_mib_keyG": ("MIb","SOL","-2","CUIVRES"),
"soubassophone": ("DO","FA","-2","CUIVRES"),
"soubassophone_keyG": ("DO","SOL","-2","CUIVRES"),
"helicon": ("DO","FA","-2","CUIVRES"),
"alphorn": ("DO","FA","0","CUIVRES"),
"steel_drum": ("DO","SOL","0","PERCUSSIONS_MELODIQUES"),
"xylophone": ("DO","SOL","1","PERCUSSIONS_MELODIQUES"),
"marimba": ("DO","SOL","0","PERCUSSIONS_MELODIQUES"),
"vibraphone": ("DO","SOL","0","PERCUSSIONS_MELODIQUES"),
"carillon": ("DO","SOL","2","PERCUSSIONS_MELODIQUES"),
"glockenspiel": ("DO","SOL","2","PERCUSSIONS_MELODIQUES"),
"percussions": ("NP","NP","0","PERCUSSIONS"),
"tambourin": ("NP","NP","0","PERCUSSIONS"),
"tom_basse": ("NP","NP","0","PERCUSSIONS"),
"bongos": ("NP","NP","0","PERCUSSIONS"),
"congas": ("NP","NP","0","PERCUSSIONS"),
"tablas": ("NP","NP","0","PERCUSSIONS"),
"claves": ("NP","NP","0","PERCUSSIONS"),
"guiro": ("NP","NP","0","PERCUSSIONS"),
"triangle": ("NP","NP","0","PERCUSSIONS"),
"shaker": ("NP","NP","0","PERCUSSIONS"),
"maracas": ("NP","NP","0","PERCUSSIONS"),
"cymbales": ("NP","NP","0","PERCUSSIONS"),
"caisse_claire": ("NP","NP","0","PERCUSSIONS"),
"grosse_caisse": ("NP","NP","0","PERCUSSIONS"),
"batterie": ("NP","NP","0","PERCUSSIONS"),
"timbales": ("NP","NP","0","PERCUSSIONS"),
"timbales_latines": ("NP","NP","0","PERCUSSIONS"),
"cuica": ("NP","NP","0","PERCUSSIONS"),
"cloche": ("NP","NP","0","PERCUSSIONS"),
"bell_tree": ("NP","NP","0","PERCUSSIONS"),
"castagnettes": ("NP","NP","0","PERCUSSIONS"),
"wood_block": ("NP","NP","0","PERCUSSIONS"),
"cabasa": ("NP","NP","0","PERCUSSIONS"),
"tambourin": ("NP","NP","0","PERCUSSIONS"),
"vibraslap": ("NP","NP","0","PERCUSSIONS"),
"homme_soprano": ("DO","SOL","0","VOIX_HOMME"),
"homme_mezzo_soprano": ("DO","SOL","0","VOIX_HOMME"),
"homme_contre_tenor": ("DO","SOL","0","VOIX_HOMME"),
"homme_alto": ("DO","SOL","0","VOIX_HOMME"),
"homme_contre_alto": ("DO","SOL","0","VOIX_HOMME"),
"homme_baryton": ("DO","FA","-1","VOIX_HOMME"),
"homme_choeur": ("DO","SOL","0","VOIX_HOMME"),
"femme_soprano": ("DO","SOL","0","VOIX_FEMME"),
"femme_mezzo_soprano": ("DO","SOL","0","VOIX_FEMME"),
"femme_contre_tenor": ("DO","SOL","0","VOIX_FEMME"),
"femme_alto": ("DO","SOL","0","VOIX_FEMME"),
"femme_contre_alto": ("DO","SOL","0","VOIX_FEMME"),
"femme_baryton": ("DO","FA","-1","VOIX_FEMME"),
"femme_choeur": ("DO","SOL","0","VOIX_FEMME"),
"clavinet": ("DO","SOL","0","CLAVIERS"),
"clavecin": ("DO","SOL","0","CLAVIERS"),
"piano": ("DO","SOL","0","CLAVIERS"),
"piano_electrique": ("DO","SOL","0","CLAVIERS"),
"orgue_lithurgique": ("DO","SOL","0","CLAVIERS"),
"orgue": ("DO","SOL","0","CLAVIERS"),
"harmonium": ("DO","SOL","0","CLAVIERS"),
"synthetiseur": ("DO","SOL","0","CLAVIERS"),
"nappes": ("DO","SOL","0","CLAVIERS"),
"lead": ("DO","SOL","0","CLAVIERS"),
"theremin": ("DO","SOL","0","VOIX_FEMME"),
"harpe": ("DO","SOL","0","CORDES_PINCEES"),
"cavaquinho": ("DO","SOL","0","CORDES_PINCEES"),
"strings": ("DO","SOL","0","CORDES_FROTTEES"),
"violon": ("DO","SOL","0","CORDES_FROTTEES"),
"violon_alto_keyG": ("DO","SOL","0","CORDES_FROTTEES"),
"violon_alto": ("DO","UT3_","0","CORDES_FROTTEES"),
"violoncelle": ("DO","UT4_","-1","CORDES_FROTTEES"),
"violoncelle_keyG": ("DO","SOL","-1","CORDES_FROTTEES"),
"mandoline": ("DO","SOL","0","CORDES_PINCEES"),
"banjoline": ("DO","SOL","0","CORDES_PINCEES"),
"mandole": ("DO","SOL","-1","CORDES_PINCEES"),
"guitare": ("DO","SOL","-1","CORDES_PINCEES"),
"guitare_classique": ("DO","SOL","-1","CORDES_PINCEES"),
"guitare_electrique": ("DO","SOL","-1","CORDES_PINCEES"),
"guitare_folk": ("DO","SOL","-1","CORDES_PINCEES"),
"banjo_4_cordes": ("DO","SOL","0","CORDES_PINCEES"),
"banjo_5_cordes": ("DO","SOL","0","CORDES_PINCEES"),
"ukulele": ("DO","SOL","1","CORDES_PINCEES"),
"ukulele_baryton": ("DO","SOL","0","CORDES_PINCEES"),
"balalaika": ("DO","SOL","1","CORDES_PINCEES"),
"guitare_portugaise": ("DO", "SOL", "0", "CORDES_PINCEES"),
"chant": ("DO", "SOL", "0", "VOIX"), # Générique, pour homme ou femme
"choeurs": ("DO", "SOL", "0", "VOIX"), # Générique, pour homme ou femme
"paroles": ("NP", "NP", "0", "TEXTE"), # Pas de tonalité ni de clef
"grille": ("DO", "NP", "0", "HARMONIE"),
"grille_sib": ("SIb", "NP", "0", "HARMONIE"),
"grille_mib": ("MIb", "NP", "0", "HARMONIE"),
"grille_fa": ("FA", "NP", "0", "HARMONIE"),
"grille_sol": ("SOL", "NP", "0", "HARMONIE"),
}

TONALITES = ("DO", "REb", "RE", "MIb", "MI", "FA", "SOLb", "SOL", "LAb", "LA", "SIb", "SI", "NP")
FAMILIES = ("BOIS", "CUIVRES", "CORDES_PINCEES", "CORDES_FROTTEES", "HANCHES_LIBRES", "CLAVIERS", "PERCUSSIONS_MELODIQUES", "PERCUSSIONS", "VOIX_HOMME", "VOIX_FEMME", "VOIX", "TEXTE", "HARMONIE")
CLEFS = ("FA", "SOL", "UT3_", "UT4_", "NP")
MODE_POPULAR = 1
MODE_CLASSIQUE = 2

# On génère automatiquement les métadonnées pour ces "instruments" de secours
VIRTUAL_INSTRUMENTS = {t: (t, "SOL", "0", "VIRTUAL") for t in TONALITES + ("tutti", "conducteur")}
# Cas particulier : Le Trombone dans le Real Book. On l'ajoute manuellement car c'est du "DO" mais en clef de "FA"
VIRTUAL_INSTRUMENTS["trombone_virtual"] = ("DO", "FA", "-1", "VIRTUAL")

GROUP_BASSE = ("basse", "contrebasse", "tuba", "basse_keyG")
GROUP_POMPE = ("guitare", "banjo_4_cordes", "piano", "synthesiseur", "accordeon", "harmonium", "orgue")

def getFirstVoice(instrument):
    """ [easy]instrument_name[voice][solo] """
    # 1. Préfixe
    if instrument.startswith("easy") and len(instrument) > 4:
        instrument = instrument[4:]
    
    # 2. Suffixe Solo
    if instrument.endswith("solo") and len(instrument) > 4:
        instrument = instrument[:-4]
    
    # 3. Suffixe Voix
    if instrument and instrument[-1] in "234":
        instrument = instrument[:-1]
        
    return instrument

def isKnownInstrument(name):
    # Ici, on ne rappelle pas getFirstVoice car c'est le rôle de l'appelant 
    # de savoir ce qu'il veut tester (la racine ou le nom complet).
    return name in INSTRUMENTS or name in VIRTUAL_INSTRUMENTS

def isValidInstrument(name):
    if name.startswith("easy"):
        name = name[len("easy"):]
    if name[-1].isdigit():
        name = name[:-1]
    if name.endswith("solo"):
        name = name[:-len("solo")]
    return isKnownInstrument(name)

if __name__ == "__main__":

    """
pas d'espace
pas de majuscule sauf après key
caractères a:z 1:9 et '_' uniquement
pour les alias on recopie les données de l'instrument original et on change le nom
baryton a toujours un "y" en français
NP (not pitched) est une tonalité virtuelle pour les percussions
"""

    VALID_CHARACTERS = "abcdefghijklmnopqrstuvwxyz0123456789_"
    

    def validateInstrument(name, data):
        # 1. Validation du NOM
        # Si c'est une tonalité (MIb, SIb...), on ne valide pas les caractères (car ils ont des Maj)
        if name not in TONALITES:
            for car in name:
                if car not in VALID_CHARACTERS:
                    # Seule exception : on tolère les majuscules SI '_key' est dans le nom
                    if '_key' not in name:
                        raise Exception(f"ERREUR Nom: Caractère ou Majuscule interdite '{car}' dans {name}")

        # 2. Validation des DONNÉES
        if len(data) != 4:
            raise Exception(f"ERREUR Structure dans {name}: {data}")

        tonality, clef, octave, family = data

        # 3. Validation des listes (Pense à ajouter "VIRTUAL" et "HARMONIE" etc. dans FAMILIES)
        if tonality not in TONALITES:
            raise Exception(f"ERREUR Tonalité inconnue: {tonality} pour {name}")
            
        if family not in FAMILIES:
            raise Exception(f"ERREUR Famille inconnue: {family} pour {name}")

        if clef not in CLEFS:
            raise Exception(f"ERREUR Clef inconnue: {clef} pour {name}")

        # Validation Octave
        try:
            nbr = int(octave)
            if not (-2 <= nbr <= 2):
                raise Exception(f"ERREUR Octave hors limites (-2,2): {nbr} pour {name}")
        except:
            raise Exception(f"ERREUR Octave non-numérique: {octave} pour {name}")

    def utestInstruments():
        for instrument, data in INSTRUMENTS.items():
            validateInstrument(instrument, data)

    utestInstruments()

    print("A L L   I N S T R U M E N T S   P A S S E D !")
    
    