
import nGrammBuilder_unit
import kaWikipedia

if __name__ == "__main__":
    text2refer = kaWikipedia.WikipediaReader().take_rnd().take_random_pages().texts[0]
    ngramm_tree = nGrammBuilder_unit.NGrammsBuilder(text2refer, 1)
    nGrammBuilder_unit.briefer.Briefer(ngramm_tree, 4)

    print('\n\nrefered text:\n', text2refer)