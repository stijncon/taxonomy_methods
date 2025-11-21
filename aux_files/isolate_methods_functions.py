import pickle
import nltk
english_vocab = set(w.lower() for w in nltk.corpus.words.words())
import json
from lxml import etree
import spacy
from langdetect import detect, LangDetectException


nlp = spacy.load(r"C:\Users\conix\en_core_web_lg", exclude = ['NER','parse'])

nlp.add_pipe('sentencizer')

## function to open a file from the corpus

def view_paper(paper_id, kind):

    # kind should be: 'fullText', or 'date', or 'journal' or anything else in the json file
    # type 'all' for just the file
    
    filepath = r"C:\Users\conix\Documents" + paper_id[1:]
    
    try:
        file = open(filepath,'r',encoding = 'utf8')
        file = json.load(file)
        if kind == 'all':
            return file
        else:   
            return file[kind]
    except:
        print('error: no such file')

## function to access the methods that were isolated from a paper
def view_methods(paper_id):
    
    # paper_id is the id of the paper in the full corpus
    
    filepath = r"C:\Users\conix\Documents" + paper_id.split('.json')[0][1:] +"_methods.txt"
    
    try:
        with open(filepath,'r',encoding = 'utf8') as file:
            text = file.read()
            return text
    except Exception as e:
        print(paper_id)
        print(e)

## list of all taxa in the corpus

with open(r"C:\Users\conix\Documents\Corpus\taxaset.pickle", "rb") as fp:   # Unpickling
    taxa_set = pickle.load(fp)

taxa_set.remove('1')
taxa_set.remove('min')
taxa_set = set(taxa_set)

## to get zootaxa methods

# list of section titles that sometimes follow the methods
other_titles = [	'Taxonomy',
			'TAXONOMY',
			'Species',
			'Discussion',
			'Results',
			'Discussion and results',
			'Diagnosis',
			'Table',
			'TABLE',
			'Descriptions',
			'Description',
			'Species accounts',
			'SYSTEMATICS',
			'Systematics',
			'Systematic',
			'Keys',
			'Key',
			'Taxonomic']

# list of method section titles

methods_titles = ['Material and methods\n',
			'Materials and methods\n',
			'Materials and Methods\n',
			'Material and Methods\n',
			'MATERIALS AND METHODS\n', 
			'Methods and Materials\n',
			'Methods and materials\n',
			'Methods and terminology\n',
			'Methods and Terminology\n' ,
			'Material & methods\n',
			"Methods & material\n",
			"Materials & methods\n",
			"Materials & Methods\n",
			"Methods & Materials\n",
			'Methods\n', 
			'Meterial and methods\n',
           'Methods and abbreviations\n']

    

def get_zootaxa_methods(paper_id):

    # get the txt file
    fulltext = view_paper(paper_id, 'fullText')

    # these are the relevant section headings
    

    # check if any are in the txt, and use that one
    for i in methods_titles:
   
        split = fulltext.split(i)
        if len(split) > 1:
          
            break
            
    # if a methods section is found, run the function to extract the methods text, with the part of the text that starts with the methods 	section

    if len(split) > 1:
        return isolate_methods_zootaxa(split[1],paper_id)
        
    else:
        pass

        
def isolate_methods_zootaxa(split_text, paper_id):
    
    
    # if there is a methods section, then split on double whiteline, as all sections end like that
    # it gives a list of things in the paper separated by double whitelines, and we have to select from those the ones that are methods
    split = split_text.split('\n\n')


   

    if len(split) < 2:
        print('there is only one chunk of text after materials and methods is mentioned, better check manually...')
        print(paper_id)
        return None
    
    # check if there is a whiteline pretty quickly in the element after the first (which is def methods), which is the case for all section titles
    # also check if the first part is long enough to plausibly be a methods section, e.g. len = 200
    # if not long enough, it might be a subtitle of the methods section
    # also check if that supposed title of the next section is either an english word or a taxon. Other words probably aren't titles, and then this wouldnt be a title after all
    if (('\n' in split[1]) & (len(split[1].split('\n')[0]) <100) ) & (len(split[0]) > 200) & (((split[1].split('\n')[0]) in english_vocab) or ((split[1].split('\n')[0]) in taxa_set)):

        # if it is, then we have our methods section, and can return it
        return split[0]
        
    # if not, then there are pagebreaks in the methods, figures, subtitles,...
    
    else:
        # store the first bit after the title as definitely part of the methods section
        methods = split[0]

        # this is stuff that is often in the running head of the papers; those lines should be removed, as should figure captions.
        irrelevant_stuff = ['Accepted by','Zootaxa ', 'Magnolia Press', 'FIGURE']
        drop_irrelevant_stuff = [paragraph for paragraph in split[1:] if not any(word in paragraph for word in irrelevant_stuff)]

        
        # only keep stuff that is in english, this removed gibberish (tables etc)
        relevant_stuff = []
        for i in drop_irrelevant_stuff:
            
            count = 0
            for word in i.split(' '):
                if (word in english_vocab) or (word.lower() in taxa_set):
                    count += 1
            # remove the paragraph if less than 20% of its words are english words
            if count / len(i.split(' ')) > 0.05:
                # print(i)
                # print(count / len(i.split(' ')))
                # print(' ')
                relevant_stuff.append(i)
            else:
                # print(i)
                # print(count / len(i.split(' ')))
                # print(' ')
                pass
                
        # loop over the remaining and... 
        for i in relevant_stuff:

            # print(i)
            # print(i.split('\n'))
            # print(len(i))
            # # print(len(i.split('\n')))
            # print(' ')

            # catch common titles
            if ('\n' in i) and (any(word in i.split('\n')[0] for word in other_titles)):
                
                break

            # catch taxon titles
            elif (('\n' in i) and (len(i.split('\n')[0]) < 50) and (any(word in i.split('\n')[0].split(' ') for word in taxa_set))):

                
                
                break

            # throw away the very short ones -- these are author names, other running heads,...
            elif (len(i) < 160) : #&  any(author in i for author in authors)
                continue

            # keep full text paragraphs if they are not preceded by a title with linebreak
            # this one risks skipping over subsections of the methods if the titles are part of the text!!
            elif ('\n' not in i) & (len(i) > 160):
                
                methods += '\n\n' + i

            # keep lists of stuff in the methods
            # this one risks including stuff that shouldn't be there, like certain tables with results
            elif (i.count('\n') > 1) & ((len(i) / i.count('\n')) < 100):
 
                
                methods += '\n\n' + i

            # keep full text paragraphs if there is whitespace or a linebreak but there is enough text before it (i.e. not a title)
            # PROBLEM: I haven't encountered any methods sections with subtitles, but if there are they would be cut short.
            # I don't really see a solution for this apart from compiling a list of methods subtitles. Will do random checks and see if there are any.
            elif  (len(i.split('\n')[0]) > 80)   & (len(i) > 100):

                methods += '\n\n' + i
                
            # in all other cases, this is probably the start of the next section, and we don't need to keep it
            else:
                
                
                
                

                break
                
        return methods


## get pensoft methods

def get_pensoft_methods(paper_id):
    
    filepath = get_pensoft_xml(paper_id)
    tree = etree.parse(filepath)
    root = tree.getroot()

    methods = []

    # get all the section elements
    for sec in root.iter('sec'):
        
        if (sec[0].text != None):

            # get all the sections with 'method' in their title
            # allow for multiple as in some cases there are separate sections
            # for sampling, phylogenetic analysis, etc.
            if ('method' in sec[0].text.lower()):

                # get the text and store it
                a = (sec.xpath("string()"))
                methods.append(a)

    # if there are no methods, the list is empty
    if len(methods) > 0:
    
        return ['\n\n' + i  for i in methods][0]
    else:
        pass

# function to get the pensoft xml file from a different folder on my laptop
def get_pensoft_xml(paper_id):

    papername = paper_id[1:].split('json')[0].split('Pensoft')[1]

    # check which journal it is in, and direct to the correct folder
    
    if 'phytokeys' in paper_id:
        
        filepath = r"C:\Users\conix\Documents\Corpus\PensoftXML\pensoft journals\pk" + papername + "xml"
        
    elif 'zookeys' in paper_id:

        filepath = r"C:\Users\conix\Documents\Corpus\PensoftXML\pensoft journals\zk" + papername + "xml"
    

    elif 'hymenoptera' in paper_id:
    
        filepath = r"C:\Users\conix\Documents\Corpus\PensoftXML\pensoft journals\jhr" + papername + "xml"
      

    elif 'mycokeys' in paper_id:

        filepath = r"C:\Users\conix\Documents\Corpus\PensoftXML\pensoft journals\mk" + papername + "xml"
        
    else:
        
        filepath = r"C:\Users\conix\Documents\Corpus\PensoftXML\pensoft journals\zse" + papername + "xml"
        
    return filepath

## get ejt methods

def get_ejt_methods(paper_id):

    # get the txt file
    fulltext = view_paper(paper_id, 'fullText')


        # check whcih method title is used
    for i in methods_titles:

        
        split = fulltext.split(i)
        if len(split) > 1:
            break
            
    # if it is used, then run to function to get the methods with the part of the text that starts with the material and methods section
    if len(split) > 1:
        return isolate_methods_ejt(split[1],paper_id)
        
    else:
        print(f"{paper_id} is not a monograph or research article")
        pass

def isolate_methods_ejt(split_text, paper_id):

    # split the text on whitelines, as these are typically associated with sections
    split = split_text.split('\n\n')

    # keep the first bit as the start of the methods section
    methods = split[0]

    # loop over the other paragraphs, and append to methods unless the results section starts
    # this works because EJT has a fixed methods -- results -- discussion structure
    for i in split[1:]:
        if i.split('\n')[0] == 'Results':
            break
        # don't include page headings with the journal name
        elif (len(i) < 100) & ('European Journal of Taxonomy' in i.split(':')[0]):
            pass
            
        # don't include figure captions
        elif i.split('.')[0] == 'Fig':
            pass

        # dont include page numbers:
        elif i.isdigit():
            pass
        
        else:
            methods += '\n\n' + i

       
    return methods

## combine these to get the methods for the entire corpus without insectamundi

def get_methods(paper_id): 
    if 'Zootaxa' in paper_id:
        methods = get_zootaxa_methods(paper_id)
    elif 'Pensoft' in paper_id:
        methods = get_pensoft_methods(paper_id)
    elif 'EJT' in paper_id:
        methods = get_ejt_methods(paper_id)
    else:
        
        return 'insectamundi'

    return methods


### Functions to split the fulltext up into paragraphs

# function to cut the start off the fulltext
def cut_start(text):
    if 'Introduction\n' in text:
        ret = ' '.join(text.split('Introduction\n')[1:])
    elif 'Abstract\n' in text:
        ret = ' '.join(text.split('Abstract\n')[1:])
    else:
        ret = text[200:]
    return ret


# function to cut the end off the fulltext

def cut_end(text):
    endings = ["Acknowledgements\n","Acknowledgments\n","References\n","Bibliography\n"]
    for i in endings:
        if i in text:
            ret = text.split(i)[0]
            break
    try:
        ret
    except NameError:
        ret = text[:-200]
    return ret

# Function to get rid of whitespace at the start and end of spacy sentence objects

def cut_whitespace(nlp_sent):
    # If nlp_sent is a string, tokenize it back into a spacy Doc object
    if isinstance(nlp_sent, str):
        nlp_sent = nlp(nlp_sent)

    # Remove whitespace at the end of a sentence if the sentence doesn't end with punctuation
    if (sum(1 for char in nlp_sent[-1].text if char.isalpha()) < 1) and not (nlp_sent[-1].is_punct):
        a = nlp_sent[-1].text
        nlp_sent = ' '.join(nlp_sent.text.split(a)[:-1])

    # Re-tokenize if needed after whitespace adjustment
    return nlp(nlp_sent.text) if isinstance(nlp_sent, spacy.tokens.Doc) else nlp_sent

        
# a function to test if a sentence is really a sentence
# checks for capital, punctuation, verb and two nouns
# returns True if no sentence

def not_sentence(nlp_sent, debugging):
    if debugging:
        print(nlp_sent[0])
        print('********')
        print(nlp_sent[-1])


    nlp_sent = cut_whitespace(nlp_sent)

    # Check if it's still a spacy Doc or Span object
    if isinstance(nlp_sent, str):
        nlp_sent = nlp(nlp_sent)

    # check if the sentence starts with a capital and ends with punctuation
    # is_title doesn't work because too many sentences start with DNA, which is not titlecase
    if nlp_sent[0].text[0].isupper() and nlp_sent[-1].is_punct:
        if debugging:
            print('title case and punct ok')
        
        # check if the sentence has at least two nouns and a verb
        has_noun = 2
        has_verb = 1
        for token in nlp_sent:
            if token.pos_ in ["NOUN", "PROPN", "PRON"]:
                has_noun -= 1
            elif token.pos_ in ["VERB","AUX"]:
                has_verb -= 1
        if debugging:
            print(has_noun)
            print(has_verb)
        
        # return False if it doesn't have nouns and verb
        if has_noun < 1 and has_verb < 1:
            return False
        else:
            return True
    
    # return false if it doesn't have punctuation and capital
    else:
        return True


# function to check if a sentence is in english
def not_english(nlp_sent):
    
    try:
        if detect(nlp_sent.text) != "en":
            return True
        else:
            return False
    except LangDetectException:
        # langdetect choked while trying to parse this, that almost certainly
        # means that we don't have anything here that we want
        return True
    

# check whether 0.6 of all characters are letters
def not60_alpha(text):
    # Count the number of alphabetic characters
    alpha_count = sum(1 for char in text if char.isalpha())
    

    # Check if at least half of the characters are letters
    return alpha_count /  len(text) <= 0.6



# function that combines the other functions
# splits a methods section or full paper into paragraphs
# returns a list of paragraphs for the document

def extract_paragraphs(fulltext, document_kind, debugging):
    
    # I used the function for fulltexts and for methods sections
    # for methods, make 'document_kind' 'method', for fulltext use 'fulltext
    
    if document_kind == 'fulltext':
        
        text = cut_start(fulltext)
        text = cut_end(text)
        
    elif document_kind == 'method':
        
        text = fulltext

    # start by splitting on escapes
    split_text = text.split("\n\n")
    
    # append good paragraphs to this list
    paras = []
    
    for paragraph in split_text:

        # cut out single lines that were preceded and succeeded by escape
        if len(paragraph) < 200:
            if debugging:
                print(paragraph)
                print('short')
                print('...///'*30)
            continue

        # cut out whatever is not at least 60% letters
        if not60_alpha(paragraph):
            if debugging:
                print(paragraph)
                print('nonalpha')
                print('...///'*30)
            continue

        # process with spacy and do further checks on separate sentences
        doc = nlp(paragraph)
        para = ""
        
        for sentence in doc.sents:

            # again remove anything that is not 60% letters
            if not60_alpha(sentence.text):
                if debugging:
                    print(sentence)
                    print('notalpha sent')
                    print('...///'*30)
                continue
            
            # remove sentences that are not sentences
            if not_sentence(sentence, False):
                if debugging:
                    print(sentence)
                    print('no sent')
                    print('...///'*30)
                continue

            # remove sentences in other languages
            if not_english(sentence):
                if debugging:
                    print(sentence)
                    print('not eng')
                    print('...///'*30)
                continue


            if debugging:
                print(sentence)
                print('sentence ok')
                print('...///'*30)
                
            # combine all good sentences into a paragraph
            para += sentence.text + " "

        # throw out documents or methods sections that have less than 200 characters actual text
        if len(para) < 200:
            continue

        #ultra-long paragraphs typically means the split is "\n"
        # still doesn't work for some of the pensoft papers (they remain too long)
        elif len(para) > 5000:
            para_split = para.split("\n")
            if len(para_split) > 1:
                for subpara in para_split:
                    if (len(subpara) > 200) & (len(subpara) < 5000):
                        paras.append(subpara)
                    else:
                        continue
            
        else:
            para_split = para.split(".\n") 
            if (len(para_split) > 1) & all(len(item) > 200 for item in para_split):

                
                
                

                for subpara in para_split:
                    paras.append(subpara)

            else:
                paras.append(para)
        

    if debugging:
        print("-----END OF DOC---"*20)
    #☻ return the list of all paragraphs in the document
    return paras
