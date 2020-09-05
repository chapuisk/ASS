from PyASS import ass_abstractions as ass
import pprint


class ASSScreener:
    """
    The object to screen a corpus of text
    """
    _corp: ass.ASSCorpus
    _validated_corp = ass.ASSCorpus()

    def __init__(self, corpus: ass.ASSCorpus):
        _corp = corpus

    def ask_validation(self, entry: ass.ASSItem) -> bool:
        inp = input(validation_rules('help'))
        if inp == 'abs':
            print("\n" + (entry.abstract() if entry.abstract() else "No abstract available") + "\n")
        elif inp == 'ext':
            pprint.PrettyPrinter(indent=4).pprint(entry.raw().items())
        elif inp == 'a':
            self._validated_corp.add_item(entry)
        return True if inp in validation_rules('next') else False

    def tag_entry(self, entry: ass.ASSItem) -> bool:
        inp = input(self.tag_rules('help'))
        valid_inp = input("Is " + inp + " validate ? (o / n)")
        if valid_inp == 'o':
            entry.labels().append(inp.split(';').strip())
            return True
        elif valid_inp == 'n':
            return False

    def tag_rules(self, element: str):
        arg1 = dict(
            help="Tag the entry with any vocab, separate them with ';'. Enter 'tags' to see already screened tags",
            tags=[lab for item in self._validated_corp for lab in item.labels()],
            ext="'ext' = extended description of the item",
            abs="'abs' = abstract of the item"
        )


def validation_rules(element: str):
    var = dict(
        help="Type 'a' to accept or 's' to skip the entry - if you want to have the abstract input 'abs', "
             "'ext' for full description ",
        next=('a', 's', 'r'),
        a="'a' = to validate an item",
        s="'s' = to skip an item",
        ext="'ext' = extended description of the item",
        abs="'abs' = abstract of the item"
    )
    return var.get(element, "None valid element rules: ".join(var.keys()))
