from PyASS.ass_abstractions import ASSCorpus
from PyASS.ass_abstractions import ASSArticle
from PyASS.ass_screening.ass_screen import ASSScreener
from PyASS import ass_constant as constant
import json

screener: ASSScreener

##
# Cells to screen a bibliography
#
while True:
    prompt = input("\n Hello to ASS screening process,"
                   "\n \n Please type in the path to your corpus (bib, raw text, etc.) and press 'Enter': ")
    try:
        if prompt.endswith(".bib"):
            bib_file = open(prompt)
            the_corpus: ASSCorpus = ASSCorpus(**{constant.BIB_ENTRY: bib_file})
        elif prompt.endswith(".json"):
            json_file = json.load(prompt)
            the_corpus: ASSCorpus = ASSCorpus(**{constant.BIB_JSON: json_file})
        screener = ASSScreener(the_corpus)
    except FileNotFoundError:
        print("Wrong file or file path")
    else:
        break

if any(not (type(entry) is ASSArticle) for entry in the_corpus.corpus()):
    raise ValueError("Provided corpus should contains ASSArticles but contains: "
                     + ''.join(list(dict.fromkeys([type(item) for item in the_corpus.corpus()]))))

for entry in the_corpus.corpus():
    while True:
        print(''.join(["ENTRY: ", entry.title()]))
        if screener.ask_validation(entry):
            break
        else:
            continue


##
# Cell to tag bibliogrphic ressources
#