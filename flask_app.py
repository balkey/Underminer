#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import random
import json
import urllib2
import datetime
from flask import Flask, request, url_for, redirect, render_template

UPLOAD_FOLDER = '/home/balkey/mysite/static/uploads'
ALLOWED_EXTENSIONS = set(['txt', 'pdf'])

app = Flask(__name__, static_folder='static', static_url_path='')
app.debug = True
app.secret_key = 'some_secret'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/words', methods=['GET'])
def words_autofill():
    query = request.args['term']
    filename_url = request.args['filename']
    filename_decoded = urllib2.unquote(filename_url)
    filename_route ='/home/balkey/mysite/static/uploads/'+filename_decoded
    with app.open_resource(filename_route) as f:
        contents = json.loads(f.read())

    matching = [s['key'] for s in contents if query.lower() in s['key']]
    if len(matching) != 0:
        matching_first = []
        matching_last = []
        for i in matching:
            if i.lower().startswith(query.lower()):
		        matching_first.append(i)
            else:
		        matching_last.append(i)
        matching_first.extend(matching_last)
        return json.dumps(matching_first)
    else:
        return json.dumps(["No results found!"])

@app.route('/words_update', methods=['GET', 'POST'])
def words_update():
    a = request.args.get('a', 0, type=str)
    b= request.args.get('b', 0, type=str)
    filename_decoded = urllib2.unquote(b)
    filename_route ='/home/balkey/mysite/static/uploads/'+filename_decoded

    with app.open_resource(filename_route) as f:
        contents = json.loads(f.read())
    matching = [s for s in contents if a.lower() == s['key']]
    if len(matching) != 0:
        return json.dumps(matching[0])
    else:
        return json.dumps([])

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    now = datetime.datetime.now()
    date_for_folder = str(now.year)+"_"+str(now.month)+"_"+str(now.day)+"_"+str(now.hour)+"_"+str(now.minute)+"_"+str(now.second)+"_"+str(now.microsecond)

    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = file.filename

            file_folder = UPLOAD_FOLDER+"/"+filename[:-4]+"_"+date_for_folder
            file_folder_short = filename[:-4]+"_"+date_for_folder
            if not os.path.exists(file_folder):
                os.makedirs(file_folder)
                file.save(os.path.join(file_folder, filename))
            return redirect(url_for('uploaded_file', filename=filename, file_folder_short=file_folder_short))
        else:
            return render_template("not_valid_extension.html")
    return render_template("index2.html")

@app.route('/analysis_<file_folder_short>_<filename>', methods=['GET', 'POST'])
def uploaded_file(file_folder_short, filename):
    # IMPORTS
    # Modules are available from the default Python 2.7.5 library.
    # Download Snowball Stemmer:
    # http://snowball.tartarus.org/
    # Download TextBlob:
    # https://textblob.readthedocs.org/en/latest/
    import re
    from collections import Counter
    import snowballstemmer
    stemmer = snowballstemmer.stemmer('english')
    from text.blob import TextBlob
    import unicodedata
    #from text.sentiments import NaiveBayesAnalyzer

    # DICTIONARY_WEBSTER
    # The dictionary based on The Webster Unabridged Dictionary, consisting of more than 100.000 distinct words.
    input_file_webster = open ('/home/balkey/mysite/webster_final_work3.csv', 'r+')
    import_string_webster = (input_file_webster.read()).replace('\n', ',')
    import_string2_webster = import_string_webster.split(',')

    word_list_webster = import_string2_webster[0::5]
    style_list_webster = import_string2_webster[1::5]
    stem_list_webster = import_string2_webster[2::5]

    dictionary_webster = {}

    for q, a, v in zip(word_list_webster, style_list_webster, stem_list_webster):
        dictionary_webster[q] = [a, v]

    # OPENING TEXT
    # After opening the text, replaces miscellaneous characters. Then inserts special charachters for "end of the sentence" separators.
    # Then splits text into a list of words.
    corpus_open = open('/home/balkey/mysite/static/uploads/'+file_folder_short+'/'+filename, 'r+')
    textfile_output_count = open('/home/balkey/mysite/static/uploads/'+file_folder_short+'/'+filename[:-4]+'.json', 'w')
    textfile_output_count_display = open('/home/balkey/mysite/static/uploads/'+file_folder_short+'/'+filename[:-4]+'_display.js', 'w')
    textfile_output_speech = open('/home/balkey/mysite/static/uploads/'+file_folder_short+'/'+filename[:-4]+'_speech.tsv', 'w')
    textfile_output_sentiment_by_sentence = open('/home/balkey/mysite/static/uploads/'+file_folder_short+'/'+filename[:-4]+'_sentiment.js', 'w')

    corpus_clean0 = (corpus_open.read()).replace('-', ' ')
    try:
        corpus_clean0.decode('ascii')
        #corpus_clean0.decode('utf-8')
    except UnicodeDecodeError:
        return render_template("non_ascii.html")
    else:
        corpus_open.close()
        corpus_open2 = open('/home/balkey/mysite/static/uploads/'+file_folder_short+'/'+filename, 'r+')
        corpus_lines = corpus_open2.readlines()

    substring_list0 = ['CHAPTER']
    substring_list2 = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']

    def chapter_detector():
        counter_chap = 0
        counter_arab = 0
        counter_roman = 0
        counter_upper = 0
        regex = re.compile("^M{0,4}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})$")
        regex2 = re.compile("^[0-9][0-9.]*$")
        for i in range(0, (len(corpus_lines)-1)):
            line = corpus_lines[i]
            m = re.search(regex, line)
            n = re.search(regex2, line)
            if (corpus_lines[i -1] in ['\n', '\r\n'] and corpus_lines[i +1] in ['\n', '\r\n'] and any(substring in line.upper() for substring in substring_list0)):
                counter_chap += 1
            elif (corpus_lines[i -1] in ['\n', '\r\n'] and corpus_lines[i +1] in ['\n', '\r\n'] and m is not None and m.group() and line):
                counter_roman += 1
            elif (corpus_lines[i -1] in ['\n', '\r\n'] and corpus_lines[i +1] in ['\n', '\r\n'] and n is not None and n.group() and line):
                counter_arab += 1
            elif (corpus_lines[i -1] in ['\n', '\r\n'] and corpus_lines[i +1] in ['\n', '\r\n'] and line.isupper()):
                counter_upper += 1
        #list_of_deliminators = [counter_chap, counter_arab, counter_roman, counter_upper]
        with open('/home/balkey/mysite/static/uploads/'+file_folder_short+'/'+'analysis_'+filename, 'w') as output_file:
            if counter_chap != 0:
                for j in range(0, (len(corpus_lines)-1)):
                    line = corpus_lines[j]
                    if (corpus_lines[j -1] in ['\n', '\r\n'] and corpus_lines[j +1] in ['\n', '\r\n'] and any(substring in line.upper() for substring in substring_list0)):
                        output_file.write('chapterdeliminator ' + line)
                    else:
                        output_file.write(line)
            elif counter_roman != 0:
                for j in range(0, (len(corpus_lines)-1)):
                    line = corpus_lines[j]
                    m = re.search(regex, line.strip("."))
                    if (m is not None and m.group() and line and corpus_lines[j -1] in ['\n', '\r\n'] and corpus_lines[j +1] in ['\n', '\r\n']):
                        output_file.write('chapterdeliminator ' + line)
                    else:
                        output_file.write(line)
            elif counter_arab != 0:
                for j in range(0, (len(corpus_lines)-1)):
                    line = corpus_lines[j]
                    n = re.search(regex2, line)
                    if (corpus_lines[j -1] in ['\n', '\r\n'] and corpus_lines[j +1] in ['\n', '\r\n'] and n is not None and n.group() and line):
                        output_file.write('chapterdeliminator ' + line)
                    else:
                        output_file.write(line)
            elif counter_upper != 0:
                for j in range(0, (len(corpus_lines)-1)):
                    line = corpus_lines[j]
                    if (corpus_lines[j -1] in ['\n', '\r\n'] and corpus_lines[j +1] in ['\n', '\r\n'] and line.isupper()):
                        output_file.write('chapterdeliminator ' + line)
                    else:
                        output_file.write(line)
        output_file.close()
        corpus_open.close()

    chapter_detector()

    corpus_good = open ('/home/balkey/mysite/static/uploads/'+file_folder_short+'/'+'analysis_'+filename, 'rw')

    corpus_clean = corpus_good.read().replace('-', ' ')
    corpus_clean2 = corpus_clean.replace('!', ' kbkbkb ')
    corpus_clean3 = corpus_clean2.replace('?', ' kbkbkb ')
    corpus_clean4 = corpus_clean3.replace('.', ' kbkbkb ')
    corpus_words = corpus_clean4.split()

    corpus_words_clean = []
    corpus_words_clean2 = []
    corpus_words_clean3 = []
    corpus_words_clean4 = []
    corpus_words_clean5 = []
    corpus_words_clean6 = []

    book_by_chapter = []
    book_by_chapter_and_sentence = []
    book_by_chapter_and_sentence_final = []

    book_by_chapter_speech = []
    book_by_chapter_and_sentence_speech = []
    book_by_chapter_and_sentence_final_speech = []

    list_of_speech = []
    chapter_sentence_count = []
    occurance_text = []
    words_on_default_display = []

    # COUNTERS
    # Technical counters for each part of speech / word position.
    noun = 0
    pronoun = 0
    adjective = 0
    verb = 0
    auxiliary_verb = 0
    adverb = 0
    preposition = 0
    conjuction = 0
    interjection = 0
    junk = 0
    word_count = 0

    # ROMAN NUMBERS, STOPWORD LIST
    # Optional, if you want to elimit roman numbers / stopwords supported by predefined lists.
    roman_numbers = open ('/home/balkey/mysite/roman.txt', 'r+')
    import_roman = (roman_numbers.read()).split('\n')
    stopword = open ('/home/balkey/mysite/stopword.txt', 'r+')
    import_stopword = (stopword.read()).split('\n')

    # CLIPPER
    # Clips non abc-characters, removes apostrophes with tailing characters, keeps only words longer than two characters.
    def clipper(word):
      if len(word.strip('()[].!?-,:;/"_ '"'"))>=3 and word.strip('()[].!?-,:;/"_ '"'")[-3] == "'":
        return word.strip('()[].!?-,:;/"_ '"'")[:-3]
      elif len(word.strip('()[].!?-,:;/"_ '"'"))>=2 and word.strip('()[].!?-,:;/"_ '"'")[-2]  == "'":
        return word.strip('()[].!?-,:;/"_ '"'")[:-2]
      elif len(word.strip('()[].!?-,:;/"_ '"'"))>=2 and word.strip('()[].!?-,:;/"_ '"'")[1]  == "'":
        return word.strip('()[].!?-,:;/"_ '"'")[2:]
      elif len(word.strip('()[].!?-,:;/"_ '"'"))>=2:
        return word.strip('()[].!?-,:;/"_ '"'").lower()
      else:
        return "delete_me"

    # LOWER-CASE, CLIPPER
    def text_lower(looped_list, new_list):
      new_list.extend([clipper(s[:].lower()) for s in looped_list])

    # CLEANUP
    def cleanup(looped_list, new_list):
      new_list.extend([word for word in looped_list if word !="delete_me"])

    # ISDIGIT
    # Removes numerical characters.
    def isdigit(looped_list, new_list):
      new_list.extend([x for x in looped_list if not any(re.search(r'\d',c) for c in x)])

    # WORDSTEMMER
    # Looks for all words in the text and tries to match them to the Webster dictionary with growing transformations of the
    # original word in number of characters:
    # 1. Emits roman numbers / stopwords.
    # 2. Checks if the original form of word exists in the Webster dictionary
    # 3. Checks, if the Snowball wordstem exists in the dictionary.
    # 4. Starts simple word transformations, and looks for results in the Webster dictionary.
    # In all cases, if there's a match in the Webster dictionary, the match will be inserted. Otherwise, the original word is kept.
    def wordstem_checker(word):
      if word.upper() in import_roman:
        return ''
      elif word in import_stopword:
        return ''
      elif dictionary_webster.has_key(word):
        return word
      elif dictionary_webster.has_key(stemmer.stemWord(word)):
        return stemmer.stemWord(word)
      elif word[-1] == 'y' and dictionary_webster.has_key(word[:-1]):
        return word[:-1]
      elif word[-1] == 'r' and dictionary_webster.has_key(word[:-1]):
        return word[:-1]
      elif word[-1] == 's' and dictionary_webster.has_key(word[:-1]):
        return word[:-1]
      elif word[-2:] == 'es' and dictionary_webster.has_key(word[:-2]):
        return word[:-2]
      elif word[-2:] == 'er' and dictionary_webster.has_key(word[:-2]):
        return word[:-2]
      elif word[-3:] == 'est' and dictionary_webster.has_key(word[:-2]):
        return word[:-3]
      elif word[-3:] == 'est' and dictionary_webster.has_key(word[:-3]):
        return word[:-3]
      elif word[-1] == 'd' and dictionary_webster.has_key(word[:-1]):
        return word[:-1]
      elif word[-2:] == 'ed' and dictionary_webster.has_key(word[:-2]):
        return word[:-2]
      elif word[-2:] == 'in' and dictionary_webster.has_key(word+'g'):
        return word+'g'
      elif word[-2:] == 'in' and dictionary_webster.has_key(word+'e'):
        return word+'e'
      elif word[-2:] == 'in' and dictionary_webster.has_key(word[:-2]):
        return word[:-2]
      elif word[-3:] == 'ing' and dictionary_webster.has_key(word[:-3]):
        return word[:-3]
      elif word[-3:] == 'ing' and dictionary_webster.has_key(word[:-3]+'e'):
        return word[:-3]+'e'
      elif word[-3:] == 'ing' and dictionary_webster.has_key(word[:-3]+'y'):
        return word[:-3]+'y'
      elif word[-3:] == 'ier' and dictionary_webster.has_key(word[:-3]+'y'):
        return word[:-3]+'y'
      elif word[-3:] == 'ies' and dictionary_webster.has_key(word[:-3]+'y'):
        return word[:-3]+'y'
      elif word[-3:] == 'ied' and dictionary_webster.has_key(word[:-3]+'y'):
        return word[:-3]+'y'
      elif word[-4:] == 'iest' and dictionary_webster.has_key(word[:-4]+'y'):
        return word[:-4]+'y'
      else:
        return word

    # STEM INSERTER
    # Inserts the wordstem-checker() function's result into a final form.
    def stem_insterter(looped_list, new_list):
      new_list.extend([wordstem_checker(x) for x in looped_list])

    # EMPTY SLOT EMITTER
    # Removes empty slots.
    def slot_emitter(looped_list, new_list):
      new_list.extend([x for x in looped_list if x!=''])

    # CHAPTER-SPLITTER
    # Splits the text into sublists by the given separator.
    # This could be improved with RE.
    def chapter_split(looped_list, separator):
      start = 0
      while start < len(looped_list):
        try:
          stop = start + looped_list[start:].index(separator)
          yield looped_list[start:stop]
          start = stop + 1
        except ValueError:
          yield looped_list[start:]
          break

    # COUNTER BY CHAPTER
    # Counts and returns the occurrences of a given word in each chapter.
    # Prints it to the output file in one line.
    def word_counter_chapter(book, word, textfile_output):
      for i in book:
        if book.index(i) < len(book)-1:
          z = i.count(word)
          print >>textfile_output, '['+str(int(book.index(i))+1)+", "+str(z)+'] ,',
          #textfile_output.write('['+str(int(book.index(i))+1)+", "+str(z)+'] ,',)
        else:
          z = i.count(word)
          print >>textfile_output, '['+str(int(book.index(i))+1)+", "+str(z)+'] ',
          #textfile_output.write('['+str(int(book.index(i))+1)+", "+str(z)+'] ',)
      return '] }, '

    def last_word(book, word, textfile_output):
      for i in book:
        if book.index(i) < len(book)-1:
          z = i.count(word)
          print >>textfile_output, '['+str(int(book.index(i))+1)+", "+str(z)+'] ,',
          #textfile_output.write('['+str(int(book.index(i))+1)+", "+str(z)+'] ,',)
        else:
          z = i.count(word)
          print >>textfile_output, '['+str(int(book.index(i))+1)+", "+str(z)+'] ',
          #textfile_output.write('['+str(int(book.index(i))+1)+", "+str(z)+'] ',)
      return '] } '

    #WORDS VOLUME GENERATOR
    #Looks for at least 8 words that have at least 10 occurences in the text.
    #If there are no such 8 words, reduces the number of occurences until at least 8 words are found.
    #From this generated list, takes 8 words randomly, and generates a list from them.
    def words_volume_generator(wordlist, final_list):
      output_list = []
      counter = 50
      for x in wordlist:
        if x[1] > counter:
          output_list.append(x[0])

      while len(output_list) < 8:
        counter -= 1
        for x in wordlist:
          if x[1] > counter and x[0] not in output_list:
            output_list.append(x[0])
      random_words = random.sample(range(len(output_list)), 8)
      for z in random_words:
        y = output_list[z]
        final_list.append(y)

    # TRANSFORMER
    # Replaces the words with their part-of-speech from the Webster dictionary, keeping the
    # sentence and chapter separator special characters. If the word is not listed in the Webster dictionary,
    # it's part-of-speech value will be assigned to 'Not found'.
    def transformer(word):
      if word == 'kbkbkb':
        return 'kbkbkb'
      elif word == 'chapterdeliminator':
        return 'chapterdeliminator'
      elif dictionary_webster.has_key(word):
        return dictionary_webster[word][0]
      else:
        return 'Not found'

    # TRANSFORMER INSERTER
    # Inserts the results of the transormer() function into a final form.
    def transformer_inserter(list1, list2):
      list2.extend([transformer(x) for x in list1])

    # SENTENCE AVERAGE LENGHT
    # Counts the average number of words / sentence / chapter.
    def sentence_average_lenght(chapter):
      counter = 0
      for sentence in chapter:
        counter = counter + len(sentence)
      average = counter / len(chapter)
      return average

    # GET MOST COMMON PART OF SPEECH
    # Returns the most common part of speech for word position / sentence / chapter.
    def speech_count(list_of_values):
      if max(list_of_values) == noun:
        return 'Noun'
      elif max(list_of_values) == pronoun:
        return 'Pronoun'
      elif max(list_of_values) == adjective:
        return 'Adjective'
      elif max(list_of_values) == verb:
        return 'Verb'
      elif max(list_of_values) == auxiliary_verb:
        return 'Auxiliary-verb'
      elif max(list_of_values) == adverb:
        return 'Adverb'
      elif max(list_of_values) == preposition:
        return 'Preposition'
      elif max(list_of_values) == conjuction:
        return 'Conjuction'
      elif max(list_of_values) == interjection:
        return 'Interjection'
      else:
        return 'Unknown'

    # BOOK BY CHAPTER AND BY SENTENCE
    # Compiles the final book, split by chapters and sentences.
    def book_compiler(looped_list, final_book):
      book_by_chapter.extend([i for i in chapter_split(looped_list, 'chapterdeliminator')])
      for chapter in book_by_chapter:
        book_by_chapter_and_sentence.append([word for word in chapter_split(chapter, 'kbkbkb')])
      for chapter in book_by_chapter_and_sentence:
        final_book.append([sentence for sentence in chapter if len(sentence) != 0])

    # BOOK BY CHAPTER AND BY SENTENCE - PART OF SPEECH
    # Compiles the final book, split by chapters and sentences.
    def book_compiler_speech(looped_list, final_book):
      book_by_chapter_speech.extend([i for i in chapter_split(looped_list, 'chapterdeliminator')])
      for chapter in book_by_chapter_speech:
        book_by_chapter_and_sentence_speech.append([word for word in chapter_split(chapter, 'kbkbkb')])
      for chapter in book_by_chapter_and_sentence_speech:
        final_book.append([sentence for sentence in chapter if len(sentence) != 0])


    # PRINTER - WORD OCCURANCE BY CHAPTER
    #Prints the output file, which is a .js file containing a JSON array of the transformed/stemmed word and it's occurrence by chapter.
    def printer_style(book_for_print, wordlist_for_print, textfile_output):
      lista = sorted(wordlist_for_print, key=wordlist_for_print.get, reverse=True)
      print >>textfile_output, '['
      #textfile_output.write('[')
      for word in lista:
        if lista.index(word) < len(lista)-1:
            print >>textfile_output, '{ "key" : '+'"'+word+'"'+' , '+'"values" :'+' [', word_counter_chapter(book_for_print, word, textfile_output)
            #textfile_output.write('{ "key" : '+'"'+word+'"'+' , '+'"values" :'+' [', word_counter_chapter(book_for_print, word, textfile_output))
        else:
            print >>textfile_output, '{ "key" : '+'"'+word+'"'+' , '+'"values" :'+' [', last_word(book_for_print, word, textfile_output)
            #textfile_output.write('{ "key" : '+'"'+word+'"'+' , '+'"values" :'+' [', last_word(book_for_print, word, textfile_output))
            print >>textfile_output, ']'
            #textfile_output.write(']')

      # PRINTER - WORD OCCURANCE BY CHAPTER FOR DISPLAY
      #Prints the output file, which is a .js file containing a JSON array of the transformed/stemmed word and it's occurrence by chapter.
      #There are only 8 words in this list for default display on D3 STACKED chart- generated randomly by WORDS VOLUME GENERATOR.
    def printer_style_display(book_for_print, wordlist_for_print, textfile_output):
        print >>textfile_output, 'histcatexplong = ['
        #textfile_output.write('histcatexplong = [')
        for word in wordlist_for_print:
            if wordlist_for_print.index(word) < len(wordlist_for_print)-1:
                print >>textfile_output, '{ "key" : '+'"'+word+'"'+' , '+'"values" :'+' [', word_counter_chapter(book_for_print, word, textfile_output)
                #textfile_output.write('{ "key" : '+'"'+word+'"'+' , '+'"values" :'+' [', word_counter_chapter(book_for_print, word, textfile_output))
            else:
                print >>textfile_output, '{ "key" : '+'"'+word+'"'+' , '+'"values" :'+' [', last_word(book_for_print, word, textfile_output)
                #textfile_output.write('{ "key" : '+'"'+word+'"'+' , '+'"values" :'+' [', last_word(book_for_print, word, textfile_output))
                print >>textfile_output, '];'
                #textfile_output.write('];')

    # SENTENCE COUNT
    # Counts the number of sentences / chapter.
    def sentence_count(book, sentence_count_list):
      sentence_count_list.extend([len(chapter) for chapter in book])

    # SENTIMENT ANALYZER
    # Calls TextBlob's default sentiment analyzer,
    # and prints each sentence's sentiment in a .js variable.
    def sentimenter(book):
	    print >>textfile_output_sentiment_by_sentence, "var sentiment= ["
	    for chapter in book:
		    for sentence in chapter:
			    sentiment_str = ' '.join(sentence)
			    sentiment_tr = TextBlob (sentiment_str)
			    if sentiment_tr.sentiment[0] != 0.0:
				    print >>textfile_output_sentiment_by_sentence, str(sentiment_tr.sentiment[0])+','
	    print >> textfile_output_sentiment_by_sentence, "];"

    #def sentimenter (book):
    #print >>textfile_output_sentiment_by_sentence, 'CHAPTER'+',', 'INDEX'+',', 'NUMBER OF WORDS'+',', 'SENTENCE'+',', 'POLARITY'+',', 'OBJECTIVITY'+','
    #counter_chapter = 0
    #counter_sentence = 0
    #for chapter in book:
        #for sentence in chapter:
            #sentiment_str = ' '.join(sentence)
            #sentiment_tr = TextBlob (sentiment_str)
            #print >>textfile_output_sentiment_by_sentence, str(counter_chapter)+',', str(counter_sentence)+',', str(len(sentence))+',', str(sentiment_str)+',', str(sentiment_tr.sentiment[0])+',', str(sentiment_tr.sentiment[1])+','
            #counter_sentence +=1
        #counter_chapter +=1

    # SENTIMENT ANALYZIER - NAIVE BAYES
    # Calls TextBlob's Naive Bayes sentiment analyzer.
    # Runs about 2-3 hours...
    '''def sentimenter_naive_bayes (book):
      print >>textfile_output_sentiment_by_sentence, 'CHAPTER'+',', 'INDEX'+',', 'SENTENCE'+',', 'POLARITY'+',', 'OBJECTIVITY'+','
      counter_chapter = 0
      counter_sentence = 0
      for chapter in book:
        for sentence in chapter:
          sentiment_str = ' '.join(sentence)
          sentiment_tr = TextBlob (sentiment_str, analyzer=NaiveBayesAnalyzer())
          print >>textfile_output_sentiment_by_sentence, str(counter_chapter)+',', str(counter_sentence)+',', str(sentiment_str)+',', str(sentiment_tr.sentiment[0])+',', str(sentiment_tr.sentiment[1])+','
          counter_sentence +=1
        counter_chapter +=1'''

    # CALLING MAIN FUNCTIONS
    isdigit(corpus_words, corpus_words_clean)
    text_lower(corpus_words_clean, corpus_words_clean2)
    cleanup(corpus_words_clean2, corpus_words_clean3)
    stem_insterter(corpus_words_clean3, corpus_words_clean4)
    slot_emitter(corpus_words_clean4, corpus_words_clean5)
    transformer_inserter(corpus_words_clean5, corpus_words_clean6)
    book_compiler(corpus_words_clean5, book_by_chapter_and_sentence_final)
    book_compiler_speech(corpus_words_clean6, book_by_chapter_and_sentence_final_speech)
    occurance_text = Counter(corpus_words_clean5)
    occurance_text_sorted = sorted(occurance_text.items(), key=lambda x:x[1], reverse=True)
    words_volume_generator(occurance_text_sorted, words_on_default_display)
    printer_style_display(book_by_chapter, words_on_default_display, textfile_output_count_display)
    printer_style(book_by_chapter, occurance_text, textfile_output_count)
    sentimenter(book_by_chapter_and_sentence_final)
    '''sentimenter_naive_bayes(book_by_chapter_and_sentence_final)'''
    # sentence_count(book_by_chapter_and_sentence_final, chapter_sentence_count)

    # AVERAGE SENTENCE LENGTH BY CHAPTER
    # Takes the "BOOK BY CHAPTER AND BY SENTENCE - PART OF SPEECH" and:
    # 1. Examines only those sentences for each chapter, which at least have the number of words - or more - of the average sentence length/chapter.
    # 2. Counts all "part of speech" for each word position for each sentence in the range of the average sentence length of the examined chapter.
    # 3. Returns the most frequent part of speech for each word position for the average length of sentence for each chapter.
    # 4. Prints all this into a .csv file.
    print >>textfile_output_speech, 'CHAPTER'+'\t', 'WORD_POSITION'+'\t', 'WINNER'+'\t', 'NOUN'+'\t', 'PRONOUN'+'\t', 'ADJECTIVE'+'\t', 'VERB'+'\t', 'AUXILIARY-VERB'+'\t', 'ADVERB'+'\t', 'PREPOSITON'+'\t', 'CONJUCTION'+'\t', 'INTERJECTION'+'\t', 'UNKNOWN'+'\t'
    #textfile_output_speech.write('CHAPTER'+'\t', 'WORD_POSITION'+'\t', 'WINNER'+'\t', 'NOUN'+'\t', 'PRONOUN'+'\t', 'ADJECTIVE'+'\t', 'VERB'+'\t', 'AUXILIARY-VERB'+'\t', 'ADVERB'+'\t', 'PREPOSITON'+'\t', 'CONJUCTION'+'\t', 'INTERJECTION'+'\t', 'UNKNOWN'+'\t')
    for chapter in book_by_chapter_and_sentence_final_speech:
      while word_count <= sentence_average_lenght(chapter):
        for sentence in chapter:
          if len(sentence) >= sentence_average_lenght(chapter):
            if word_count < len(sentence) and sentence[word_count] == 'noun':
              noun +=1
            elif word_count < len(sentence) and sentence[word_count] == 'pronoun':
              pronoun +=1
            elif word_count < len(sentence) and sentence[word_count] == 'adjective':
              adjective +=1
            elif word_count < len(sentence) and sentence[word_count] == 'verb':
              verb +=1
            elif word_count < len(sentence) and sentence[word_count] == 'auxiliary-verb':
              auxiliary_verb +=1
            elif word_count < len(sentence) and sentence[word_count] == 'adverb':
              adverb +=1
            elif word_count < len(sentence) and sentence[word_count] == 'preposition':
              preposition +=1
            elif word_count < len(sentence) and sentence[word_count] == 'conjuction':
              conjuction +=1
            elif word_count < len(sentence) and sentence[word_count] == 'interjection':
              interjection +=1
            elif word_count < len(sentence):
              junk +=1
            else:
              continue
          else:
            continue
        list_of_speech = [noun, pronoun, adjective, verb, auxiliary_verb, adverb, preposition, conjuction, interjection, junk]
        print >>textfile_output_speech, str((book_by_chapter_and_sentence_final_speech.index(chapter))+1)+'\t', str(word_count+1)+'\t', speech_count(list_of_speech)+'\t', str(noun)+'\t', str(pronoun)+'\t', str(adjective)+'\t', str(verb)+'\t', str(auxiliary_verb)+'\t', str(adverb)+'\t', str(preposition)+'\t', str(conjuction)+'\t', str(interjection)+'\t', str(junk)+'\t'
        #textfile_output_speech.write(str((book_by_chapter_and_sentence_final_speech.index(chapter))+1)+'\t', str(word_count+1)+'\t', speech_count(list_of_speech)+'\t', str(noun)+'\t', str(pronoun)+'\t', str(adjective)+'\t', str(verb)+'\t', str(auxiliary_verb)+'\t', str(adverb)+'\t', str(preposition)+'\t', str(conjuction)+'\t', str(interjection)+'\t', str(junk)+'\t')
        noun = 0
        pronoun = 0
        adjective = 0
        verb = 0
        auxiliary_verb = 0
        adverb = 0
        preposition = 0
        conjuction = 0
        interjection = 0
        junk = 0
        word_count +=1
      word_count = 0

    roman_numbers.close()
    stopword.close()
    corpus_good.close()
    textfile_output_count.close()
    textfile_output_count_display.close()
    textfile_output_speech.close()
    textfile_output_sentiment_by_sentence.close()

    # 3D-LIKE VISUALIZATION FOR IMAGE
    # Shows the occurrences of the 5 most frequent words / chapter on 3 axes:
    # Download Matplotlip:
    # http://matplotlib.org
    # Needs to be further tested, the words could be query-based in the final form.
    from mpl_toolkits.mplot3d import Axes3D
    from matplotlib.collections import PolyCollection
    from matplotlib.colors import colorConverter
    import matplotlib.pyplot as plt
    import numpy as np
    import matplotlib
    fig1 = plt.figure()
    fig1.set_size_inches(7, 4.7)
    matplotlib.rcParams.update({'font.size': 6})
    ax = fig1.gca(projection='3d')
    cc = lambda arg: colorConverter.to_rgba(arg, alpha=0.6)

    def chapter_list(book, new_list):
      new_list.extend([book.index(i) for i in book])

    def word_counter_chapter_graph(book, word, new_list):
      for chapter in book:
        y = 0
        for sentence in chapter:
          y += sentence.count(word)
        new_list.append(y)

    chapters = []
    chapters_graph = []
    chapters_graph2 = []
    chapters_graph3 = []
    chapters_graph4 = []
    chapters_graph5 = []

    chapter_list(book_by_chapter_and_sentence_final, chapters)

    most_frequent = []
    topy_scale = occurance_text_sorted[1][1]
    for word, occu in occurance_text_sorted[:20]:
      if word != 'kbkbkb':
        most_frequent.append(word)

    word_counter_chapter_graph(book_by_chapter_and_sentence_final, most_frequent[4], chapters_graph)
    word_counter_chapter_graph(book_by_chapter_and_sentence_final, most_frequent[3], chapters_graph2)
    word_counter_chapter_graph(book_by_chapter_and_sentence_final, most_frequent[2], chapters_graph3)
    word_counter_chapter_graph(book_by_chapter_and_sentence_final, most_frequent[1], chapters_graph4)
    word_counter_chapter_graph(book_by_chapter_and_sentence_final, most_frequent[0], chapters_graph5)

    #ax.text(11, 6,(max(chapters_graph5)/10)*1, most_frequent[4], fontsize=8, style='normal', color='#91E8E8')
    #ax.text(11, 6,(max(chapters_graph5)/10)*3, most_frequent[3], fontsize=8, style='normal', color='#3d797f')
    #ax.text(11, 6,(max(chapters_graph5)/10)*5, most_frequent[2], fontsize=8, style='normal', color='#57af66')
    #ax.text(11, 6,(max(chapters_graph5)/10)*7, most_frequent[1], fontsize=8, style='normal', color='#fddb61')
    #ax.text(11, 6,(max(chapters_graph5)/10)*9, most_frequent[0], fontsize=8, style='normal', color='#f28d2f')

    xs = chapters
    verts = []
    zs = [1, 2, 3, 4, 5]
    for z in zs:
      if z == 1:
        ys = chapters_graph
        ys[0], ys[-1] = 0, 0
        verts.append(list(zip(xs, ys)))
      if z == 2:
        ys = chapters_graph2
        ys[0], ys[-1] = 0, 0
        verts.append(list(zip(xs, ys)))
      if z == 3:
        ys = chapters_graph3
        ys[0], ys[-1] = 0, 0
        verts.append(list(zip(xs, ys)))
      if z == 4:
        ys = chapters_graph4
        ys[0], ys[-1] = 0, 0
        verts.append(list(zip(xs, ys)))
      if z == 5:
        ys = chapters_graph5
        ys[0], ys[-1] = 0, 0
        verts.append(list(zip(xs, ys)))

    poly = PolyCollection(verts, facecolors = [cc('#91E8E8'), cc('#3d797f'), cc('#57af66'), cc('#fddb61'), cc('#f28d2f')])
    poly.set_alpha(0.7)
    ax.add_collection3d(poly, zs=zs, zdir='y')

    ax.set_xlabel('Chapters', fontsize=8)
    ax.set_xlim3d(0, len(chapters))
    ax.set_ylabel('Words', fontsize=8)
    ax.set_ylim3d(0, 6)
    ax.set_zlabel('Occurances', fontsize=8)
    ax.set_zlim3d(0, max(chapters_graph5))
    fig1.tight_layout()
    fig1.savefig('/home/balkey/mysite/static/uploads/'+file_folder_short+'/'+filename[:-4]+'.png', dpi=300, facecolor='none', edgecolor='none',
          orientation='portrait', papertype=None, format=None,
          transparent=True, pad_inches=0,
          frameon=None, bbox_inches='tight')


    # PIECHART IMAGE
    # Drawn with Matplotlib as well

    import matplotlib.pyplot as plt2

    pie_sizes = []
    sentence_speech = corpus_words_clean6.count('kbkbkb') + corpus_words_clean6.count('chapterdeliminator')
    pie_sizes.append(round(corpus_words_clean6.count('noun') / float(len(corpus_words_clean6) - sentence_speech)*100, 2))
    pie_sizes.append(round(corpus_words_clean6.count('pronoun') / float(len(corpus_words_clean6) - sentence_speech)*100, 2))
    pie_sizes.append(round(corpus_words_clean6.count('adjective') / float(len(corpus_words_clean6) - sentence_speech)*100, 2))
    pie_sizes.append(round(corpus_words_clean6.count('verb') / float(len(corpus_words_clean6) - sentence_speech)*100, 2))
    pie_sizes.append(round(corpus_words_clean6.count('auxiliary-verb') / float(len(corpus_words_clean6) - sentence_speech)*100, 2))
    pie_sizes.append(round(corpus_words_clean6.count('adverb') / float(len(corpus_words_clean6) - sentence_speech)*100, 2))
    pie_sizes.append(round((corpus_words_clean6.count('preposition') + corpus_words_clean6.count('conjuction') + corpus_words_clean6.count('interjection')) / float(len(corpus_words_clean6) - sentence_speech)*100, 2))
    pie_sizes.append(round((corpus_words_clean6.count('Not found')  + corpus_words_clean6.count('unknown')) / float(len(corpus_words_clean6) - sentence_speech)*100, 2))

    fig2 = plt2.figure()
    fig2.set_size_inches(6, 4)
    matplotlib.rcParams.update({'font.size': 8})
    matplotlib.rcParams.update({'font.color':'#2F3440'})
    matplotlib.rcParams.update({'font.family':'sans-serif'})

    labels = 'Nouns', 'Pronouns', 'Adjectives', 'Verbs', 'Auxiliary-verbs', 'Adverbs', 'Prep./Conjuction/Interjection', 'Not found'
    sizes = pie_sizes
    colors = ['#E9662C', '#F09871', '#EBAF3C', '#00AC65', '#00DF83', '#068894', '#09CCDE', '#797979']
    explode = (0, 0, 0.1, 0, 0, 0, 0, 0) # only "explode" the 2nd slice (i.e. 'Hogs')

    def my_autopct(pct):
      return '{p:.2f}%'.format(p=pct)

    patches, text, autotexts = plt2.pie(sizes, startangle= 120, colors=colors, explode=explode, autopct=my_autopct, shadow=True)

    for pie_wedge in patches:
      pie_wedge.set_edgecolor('gray')

    legend = plt2.legend(labels, bbox_to_anchor=(0.6, -.1), shadow=False,  ncol=4, loc='center')

    frame = legend.get_frame()
    frame.set_facecolor('none')
    frame.set_edgecolor('none')

    autotexts[4].set_color('none')
    autotexts[6].set_color('none')

    plt2.axis('equal')
    fig2.savefig('/home/balkey/mysite/static/uploads/'+file_folder_short+'/'+filename[:-4]+'_piechart.png', dpi=300, facecolor='none', edgecolor='none',
          orientation='portrait', papertype=None, format=None,
          transparent=True, pad_inches=0.1,
          frameon=None, bbox_inches='tight')

    return render_template("analysis2.html", filename=filename, file_folder_short=file_folder_short, occurance_text_sorted=occurance_text_sorted)

@app.route('/demo.html')
def demo_page():
  return render_template("demo.html")

@app.route('/docs.html')
def docs_page():
  return render_template("docs.html")

@app.route('/about.html')
def about_page():
  return render_template("about.html")

@app.route('/alice.html')
def alice_page():
  return render_template("analysis2.html", filename="alice.txt", file_folder_short="alice_2014_8_16_13_53_50_994901", occurance_text_sorted=[('kbkbkb', 1642), ('alice', 398), ('thing', 80), ('thought', 80), ('time', 77), ('could', 77), ('queen', 76), ('king', 64), ('well', 63), ('don', 61), ('turtle', 61), ('head', 60), ('began', 58), ('hatter', 57), ('mock', 56), ('gryphon', 55), ('rabbit', 52), ('voice', 51), ('cat', 50), ('look', 45), ('mouse', 44), ('duchess', 42), ('round', 41), ('tone', 40), ('large', 40), ('dormouse', 40), ('great', 39), ('eye', 36), ('march', 35), ('reply', 34)])

@app.route('/karamazov.html')
def karamazov_page():
  return render_template("analysis2.html", filename="karamazov.txt", file_folder_short="karamazov_2014_8_16_17_0_33_211792", occurance_text_sorted=[('kbkbkb', 7092), ('alyosha', 448), ('father', 360), ('will', 295), ('time', 235), ('ivan', 230), ('man', 207), ('love', 173), ('elder', 173), ('fyodor', 172), ('could', 167), ('day', 159), ('pavlovitch', 153), ('sudden', 141), ('dmitri', 134), ('hand', 132), ('chapter', 128), ('ill', 121), ('cried', 121), ('god', 117), ('brother', 116), ('well', 114), ('eye', 114), ('thought', 105), ('good', 104), ('face', 102), ('three', 102), ('fyodorovitch', 102), ('monk', 101), ('great', 100)])

@app.route('/frankeinstein.html')
def frankeinstein_page():
  return render_template("analysis2.html", filename="frankeinstein.txt", file_folder_short="frankeinstein_2014_8_16_17_10_52_673754", occurance_text_sorted=[('kbkbkb', 3582), ('will', 201), ('could', 198), ('man', 137), ('father', 134), ('day', 133), ('feel', 128), ('work', 126), ('friend', 125), ('eye', 122), ('life', 116), ('thought', 113), ('time', 109), ('great', 102), ('night', 98), ('return', 96), ('appear', 94), ('elizabeth', 92), ('gutenberg', 92), ('project', 90), ('mind', 90), ('dear', 90), ('love', 89), ('heart', 85), ('pass', 85), ('hope', 85), ('death', 82), ('felt', 80), ('place', 76), ('remain', 74)])

@app.route('/metamorphosis.html')
def metamorphosis_page():
  return render_template("analysis2.html", filename="metamorphosis.txt", file_folder_short="metamorphosis_2014_8_16_17_15_21_176045", occurance_text_sorted=[('kbkbkb', 1057), ('grego', 298), ('room', 133), ('could', 120), ('work', 110), ('father', 102), ('sister', 101), ('door', 97), ('gutenberg', 93), ('mother', 90), ('project', 88), ('time', 74), ('tm', 57), ('open', 52), ('hand', 41), ('head', 39), ('thing', 38), ('chief', 38), ('day', 38), ('clerk', 37), ('thought', 37), ('samsa', 34), ('left', 32), ('family', 32), ('well', 32), ('bed', 31), ('state', 30), ('turn', 29), ('look', 29), ('want', 28)])

@app.route('/mobydick.html')
def mobydick_page():
  return render_template("analysis2.html", filename="mobydick.txt", file_folder_short="mobydick_2014_8_16_17_19_43_737219", occurance_text_sorted=[('kbkbkb', 10684), ('whale', 1501), ('ship', 617), ('sea', 542), ('man', 541), ('ahab', 511), ('boat', 483), ('time', 446), ('ye', 440), ('head', 431), ('will', 401), ('captain', 353), ('hand', 352), ('long', 339), ('great', 331), ('thing', 322), ('white', 282), ('eye', 271), ('day', 262), ('stubb', 257), ('queequeg', 252), ('round', 251), ('three', 248), ('sperm', 245), ('men', 244), ('side', 236), ('well', 231), ('could', 217), ('deck', 217), ('good', 216)])

@app.route('/heartofdarkness.html')
def heartofdarkness_page():
  return render_template("analysis2.html", filename="heartofdarkness.txt", file_folder_short="heartofdarkness_2014_8_16_17_23_0_558471", occurance_text_sorted=[('kbkbkb', 2924), ('kurtz', 122), ('man', 114), ('could', 112), ('work', 109), ('gutenberg', 92), ('project', 90), ('time', 85), ('thing', 72), ('river', 67), ('don', 63), ('head', 59), ('day', 58), ('tm', 57), ('look', 56), ('eye', 53), ('great', 53), ('well', 52), ('men', 51), ('station', 51), ('long', 51), ('heard', 47), ('manager', 46), ('hand', 44), ('will', 44), ('black', 43), ('voice', 42), ('sudden', 42), ('good', 42), ('life', 40)])

@app.route('/wuthering.html')
def wuthering_page():
  return render_template("analysis2.html", filename="wuthering.txt", file_folder_short="wuthering_2014_8_16_17_28_30_297515", occurance_text_sorted=[('kbkbkb', 3210), ('heathcliff', 240), ('linton', 157), ('catherine', 144), ('could', 126), ('will', 103), ('answer', 80), ('master', 80), ('edgar', 78), ('time', 76), ('house', 76), ('hand', 72), ('earnshaw', 72), ('door', 71), ('don', 67), ('joseph', 66), ('hindley', 63), ('well', 60), ('thought', 60), ('reply', 57), ('face', 56), ('till', 55), ('eye', 54), ('nelly', 53), ('love', 51), ('good', 51), ('man', 50), ('cathy', 49), ('cried', 49), ('head', 48)])

@app.route('/treasureisland.html')
def treasureisland_page():
  return render_template("analysis2.html", filename="treasureisland.txt", file_folder_short="treasureisland_2014_8_16_17_33_27_252321", occurance_text_sorted=[('kbkbkb', 4451), ('man', 267), ('captain', 236), ('hand', 230), ('silver', 224), ('doctor', 176), ('could', 175), ('well', 157), ('time', 139), ('ship', 135), ('good', 129), ('sea', 117), ('long', 116), ('work', 111), ('squire', 106), ('cried', 103), ('men', 102), ('sir', 102), ('side', 98), ('jim', 98), ('gutenberg', 92), ('began', 92), ('island', 91), ('lay', 89), ('thought', 88), ('project', 87), ('head', 87), ('john', 86), ('don', 85), ('house', 85)])

@app.route('/dracula.html')
def dracula_page():
  return render_template("analysis2.html", filename="dracula.txt", file_folder_short="dracula_2014_8_16_17_41_20_67784", occurance_text_sorted=[('kbkbkb', 9738), ('could', 493), ('will', 464), ('time', 447), ('night', 332), ('helsing', 322), ('van', 322), ('hand', 317), ('lucy', 299), ('day', 284), ('thing', 274), ('good', 258), ('man', 256), ('room', 253), ('well', 246), ('dear', 240), ('mina', 237), ('work', 236), ('friend', 227), ('face', 214), ('door', 212), ('eye', 210), ('sleep', 204), ('great', 202), ('jonathan', 201), ('count', 200), ('poor', 194), ('open', 188), ('fear', 188), ('look', 186)])

@app.route('/princessofmars.html')
def princessofmars_page():
  return render_template("analysis2.html", filename="princessofmars.txt", file_folder_short="princessofmars_2014_8_16_17_44_31_910364", occurance_text_sorted=[('kbkbkb', 2588), ('could', 210), ('great', 187), ('dejah', 180), ('thoris', 178), ('martian', 172), ('warrior', 165), ('sola', 123), ('day', 116), ('work', 113), ('time', 113), ('city', 109), ('helium', 107), ('green', 105), ('men', 101), ('tarkas', 96), ('tar', 96), ('hand', 92), ('gutenberg', 92), ('project', 91), ('man', 91), ('feet', 89), ('reach', 88), ('will', 86), ('return', 84), ('long', 80), ('mars', 78), ('dead', 77), ('barsoom', 77), ('body', 73)])

@app.route('/dubliners.html')
def dubliners_page():
  return render_template("analysis2.html", filename="dubliners.txt", file_folder_short="dubliners_2014_8_16_17_49_50_795969", occurance_text_sorted=[('kbkbkb', 6093), ('man', 238), ('gabriel', 158), ('time', 140), ('aunt', 134), ('could', 133), ('good', 131), ('ask', 128), ('room', 125), ('hand', 123), ('well', 119), ('young', 118), ('face', 118), ('work', 114), ('eye', 107), ('house', 104), ('night', 102), ('street', 102), ('began', 100), ('head', 95), ('gutenberg', 92), ('friend', 90), ('project', 89), ('life', 83), ('stood', 79), ('door', 77), ('boy', 77), ('kate', 75), ('kernan', 75), ('thought', 75)])

@app.route('/donquixote.html')
def donquixote_page():
  return render_template("analysis2.html", filename="donquixote.txt", file_folder_short="donquixote_2014_8_16_17_53_7_628581", occurance_text_sorted=[('kbkbkb', 9668), ('don', 3021), ('quixote', 2327), ('sancho', 2206), ('will', 1681), ('knight', 897), ('good', 890), ('great', 822), ('time', 773), ('thee', 764), ('well', 714), ('could', 681), ('master', 635), ('day', 554), ('worship', 549), ('thy', 537), ('hand', 535), ('god', 532), ('lady', 524), ('reply', 516), ('senor', 511), ('man', 487), ('call', 444), ('thing', 444), ('life', 402), ('love', 393), ('answer', 380), ('return', 369), ('heart', 348), ('eye', 332)])

@app.route('/madamebovary.html')
def madamebovary_page():
  return render_template("analysis2.html", filename="madamebovary.txt", file_folder_short="madamebovary_2014_8_16_17_56_54_619870", occurance_text_sorted=[('kbkbkb', 7191), ('emma', 374), ('charles', 317), ('madame', 246), ('time', 243), ('day', 233), ('monsieur', 229), ('bovary', 226), ('hand', 196), ('could', 183), ('thought', 182), ('good', 170), ('homais', 170), ('eye', 167), ('love', 166), ('long', 159), ('room', 156), ('leon', 140), ('man', 135), ('head', 135), ('will', 133), ('work', 131), ('rodolphe', 129), ('began', 129), ('well', 128), ('three', 128), ('open', 127), ('window', 119), ('house', 116), ('look', 115)])

@app.route('/prideandprejudice.html')
def prideandprejudice_page():
  return render_template("analysis2.html", filename="prideandprejudice.txt", file_folder_short="prideandprejudice_2014_8_16_17_59_32_846616", occurance_text_sorted=[('kbkbkb', 7357), ('elizabeth', 635), ('could', 527), ('will', 424), ('darcy', 418), ('bennet', 333), ('bingley', 306), ('jane', 295), ('sister', 294), ('lady', 265), ('time', 224), ('well', 224), ('good', 201), ('wickham', 194), ('great', 187), ('collin', 180), ('day', 178), ('young', 177), ('dear', 175), ('lydia', 171), ('hope', 169), ('friend', 167), ('room', 159), ('family', 159), ('man', 151), ('manner', 143), ('thought', 139), ('mother', 137), ('father', 135), ('daughter', 134)])

@app.route('/antichrist.html')
def antichrist_page():
<<<<<<< HEAD
  return render_template("analysis2.html", filename="antichrist.txt", file_folder_short="antichrist_2014_8_16_18_3_20_482391", occurance_text_sorted=[('kbkbkb', 2510), ('god', 191), ('man', 130), ('christian', 118), ('christianity', 111), ('work', 104), ('thing', 100), ('life', 99), ('will', 98), ('gutenberg', 92), ('project', 90), ('instinct', 89), ('great', 78), ('truth', 64), ('priest', 62), ('sort', 62), ('men', 58), ('concept', 58), ('tm', 57), ('fact', 53), ('german', 51), ('power', 51), ('state', 51), ('lie', 49), ('nietzsche', 48), ('people', 47), ('call', 45), ('order', 44), ('form', 44), ('time', 44)])











=======
  return render_template("analysis2.html", filename="antichrist.txt", file_folder_short="antichrist_2014_8_16_18_3_20_482391", occurance_text_sorted=[('kbkbkb', 2510), ('god', 191), ('man', 130), ('christian', 118), ('christianity', 111), ('work', 104), ('thing', 100), ('life', 99), ('will', 98), ('gutenberg', 92), ('project', 90), ('instinct', 89), ('great', 78), ('truth', 64), ('priest', 62), ('sort', 62), ('men', 58), ('concept', 58), ('tm', 57), ('fact', 53), ('german', 51), ('power', 51), ('state', 51), ('lie', 49), ('nietzsche', 48), ('people', 47), ('call', 45), ('order', 44), ('form', 44), ('time', 44)])
>>>>>>> 6ac35fbb81f54c212197dc8d2053d646fe0a988d
