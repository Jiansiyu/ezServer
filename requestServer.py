
from server.apiserver import ApiServer, ApiRoute, ApiError, ApiHandler
import json
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MyServer(ApiServer):
        @ApiRoute("/popup")
        def addbar(req):
            return {"boo":req["bar"]+1}

        @ApiRoute("/baz")
        def justret(req):
            if req:
                 raise ApiError(501,"no data in for baz")
            return {"obj":1}
        @ApiRoute("/ezserver/api")
        def pyQuandCandle(req):

            queryString = ''
            if 'querystring' in req:
                queryString = req['querystring'][0]

            logger.debug("Search Sting : {}".format(queryString))

            # ====================================================================================================================================
            import io
            import os
            import spacy
            import nltk
            import pyaudio
            import playsound
            import time
            import re
            import json

            import numpy as np
            import pandas as pd
            import speech_recognition as sr

            from nltk.corpus import stopwords
            from scipy import spatial
            from gtts import gTTS
            from datetime import date

            key_file = 'secret'
            api_key = 'secret'

            # --- | Voice to Text | ---
            def speak_to_user(message, lang = 'en'):
                sound_filename = os.path.join(os.getcwd(),'tmp_message.mp3')
                tts = gTTS(text = message, lang = lang)
                tts.save(sound_filename)
                playsound.playsound(sound_filename)
                if os.path.exists(sound_filename):
                    os.remove(sound_filename)

            def get_json_key(key_dir = os.getcwd()):
                for _, _, files in os.walk(key_dir):
                    for f in files:
                        if re.search('google_key.json',f):
                            return os.path.join(os.getcwd(),f)

            def get_api_key(key_file = key_file):
                with open(key_file,'r') as f:
                    data = json.load(f)
                    key = data["private_key"]
                    return key

            def google_listen(r,in_audio):
                status = False
                try:
                    out_audio = r.recognize_google(in_audio)
                    print("Google Speech Recognition thinks you said " + r.recognize_google(in_audio))
                    status = True
                except sr.UnknownValueError:
                    speak_to_user('sorry, I couldnt understand that')
                    print("Google Speech Recognition could not understand audio")
                except sr.RequestError as e:
                    print("Could not request results from Google Speech Recognition service; {0}".format(e))
                except Exception as e:
                    print(e)
                    speak_to_user('sorry, I couldnt understand that')
                    print('error in transcribing')
                    
                return out_audio, status

            def get_mic_audio(select_recognizer = True, api_key = api_key):
                r = sr.Recognizer()

                with sr.Microphone() as source:
                    print('listening...')
                    in_audio = r.listen(source)
                    print('transcribing...')

                if select_recognizer == True:
                    print("\nusing google speech\n")
                    if key_file is not None:
                        try:
                            print('\ttrying private api key')
                            out_audio = r.recognize_google(in_audio)
                            print("Google Speech Recognition thinks you said: " + r.recognize_google(in_audio, key=api_key))
                            return out_audio, True
                        except Exception as ge:
                            print('using default key instead, {}\n'.format(ge))
                            out_audio, status = google_listen(r,in_audio)
                            return out_audio, status
                    else:
                        out_audio, status = google_listen(r,in_audio)
                        return out_audio, status

                    if select_recognizer == False:
                        print("\nusing sphinx\n")
                        try:
                            out_audio = r.recognize_sphinx(in_audio)
                            print("Sphinx Recognition thinks you said: " + out_audio)
                            return out_audio, True
                        except Exception as e:
                            speak_to_user('sorry, I couldnt understand that')
                            print('error in transcribing')
                            return None, False

            def voice_to_text():
                print('starting application...')

                speak_to_user('What are you searching for?')
                time.sleep(.4)

                key_file = get_json_key()
                api_key = get_api_key()

                raw_text = ""
                while(True):
                    raw_text, status = get_mic_audio()
                    if status:
                        break
                    else:
                        time.sleep(.4)

                print('finished with query: {}'.format(raw_text))
            # --- | Voice to Text | ---  

            

            # --- | Text to Query | --- 
            def get_post(query):
                nlp = spacy.load("en_core_web_sm") # python -m spacy download en_core_web_sm
                query = nlp(query)
                tokenized = []
                for token in query:
                    tokenized.append((token, token.tag_, token.pos_, token.lemma_))
                return tokenized, query, nlp

            def read_arxiv_cats(csv_file = os.path.join(os.getcwd(),'arxiv_cats.csv')):
                stopword_set = set(stopwords.words('english'))

                df = pd.read_csv(csv_file)

                cats_to_ids = {}
                cats_vec = []

                for idx,c in enumerate(df['category']):
                    cats = c.replace(',','').replace(' –','').replace('-','').lower()
                    filtered_cats =  [w for w in cats.split() if not w in stopword_set]
                    cats = ' '.join(filtered_cats) 

                    ids = df.loc[idx,['id']].item()

                    cats_vec.append(cats)
                    cats_to_ids[cats] = ids

                return cats_vec, cats_to_ids

            def build_vectors(c_list): # could be stored in external file
                c_dict = {}
                c_idx = {}
                c_set = set([])

                counter = 0
                idx_counter = 0

                for idx, category in enumerate(c_list):
                    if category not in c_idx:
                        c_idx[category] = idx_counter
                        idx_counter += 1
                    else:
                        print(category)
                    for word in category.split():
                        if word not in c_set:
                            c_set.add(word)
                            c_dict[word] = counter
                            counter += 1

                c_mat = np.zeros([len(c_list),len(c_set)])

                for i, category in enumerate(c_list):
                    for word in category.split():
                        c_mat[c_idx[category]][c_dict[word]] = 1.0
                
                return c_mat, c_dict, c_idx

            def get_category(tokens, mat, c_idx):
                vec_rep = np.zeros(category_matrix.shape[1])
                for noun in tokens:
                    if noun[2] == 'NOUN':
                        try:
                            idx = c_dict[noun[0].orth_]
                            vec_rep[idx] = 1.0
                        except:
                            pass

                sims = []
                reversed_c = {value : key for (key, value) in c_idx.items()}

                for i,row in enumerate(mat):
                    distance = 1
                    try:
                        distance = spatial.distance.cosine(row, vec_rep)
                    except:
                        distance = 1
                    cos_sim = 1 - distance
                    sims.append((reversed_c[i],cos_sim))

                sims.sort(key=lambda x:x[1],reverse=True) 
                return sims[:3]

            def get_dates(query):
                dates = []
                for ent in filter(lambda e: e.label_=='DATE',query.ents):
                    dates.append(ent.text)
                return dates

            def get_sort_order(query):
                ordering = ['latest', 'recent', 'newest', 'current'] # can be expanded / not important
                for token in query:
                    if token.orth_.lower() in ordering:
                        return token
                return None

            def get_influence(query):
                ordering = ['influential', 'important', 'pivotal', 'significant', 'leading', 'noteworthy'] # can be expanded / ont important
                for token in query:
                    if token.orth_.lower() in ordering:
                        return token
                return None

            def get_authors(query, toks):
                authors = []
                for ent in filter(lambda e: e.label_=='PERSON',query.ents):
                    authors.append(ent.text)
                return authors

            def get_keys(tokens):
                keys = [tok[3] for tok in tokens]
                return keys

            arxiv_categories, arxiv_categories_to_ids = read_arxiv_cats()

            print('building categories...')
            category_matrix, c_dict, c_idx = build_vectors(arxiv_categories)
            tokens, query, nlp = get_post(queryString)
            
            print('matching category...')
            categories = get_category(tokens, category_matrix, c_idx)

            print('getting dates...')
            dates = get_dates(query)

            print('getting sort order')
            sort_order = get_sort_order(query)

            print('getting influence score...')
            influence = get_influence(query)

            print('getting authors...')
            authors = get_authors(query, tokens)

            tokens = [toks for toks in tokens if ((toks[2] != 'ADJ') and (toks[2] != 'ADP') and (toks[2] != 'CCONJ'))]
            
            for auth in authors:
                tokens = [toks for toks in tokens if toks[3] not in auth.split()]

            for cat in categories:
                tokens = [toks for toks in tokens if toks[3] not in cat[0].split()]

            for dat in dates:
                tokens = [toks for toks in tokens if toks[3] not in dat.split()]

            print('getting keywords...')
            keywords = get_keys(tokens)

            print('------------------------------------------------\nCategories: {}\nDates: {}\nSort Order: {}\nInfluence: {}\nAuthors: {}\nOther Keywords: {}'.format(
                categories,dates,sort_order,influence,authors,keywords))
            # --- | Text to Query | --- 

            

            # --- | Json Get | --- # this is very bad - feel free to make improvements
            def get_cat(cats):
                import math
                query_top = cats[0][0]
                if math.isnan(cats[0][1]):
                    return None
                cat = arxiv_categories_to_ids[query_top]
                return cat
            cat = get_cat(categories) # single cateogry short form

            def get_dat(dats): # this is especially very bad - feel free to make improvements
                date_to_parse = dats[0].split()

                today = date.today()
                curr_d = today.strftime("%d-%m-%Y").split('-')
                year = curr_d[2]
                month = curr_d[1]
                day = curr_d[0]

                for word in date_to_parse: # year
                    if word.isdigit():
                        year = word
                        break

                month_dict = {"january" : '01', "february" : '02', "march": '03',  "april": '04',
                              "may" : '05', "june" : '06', "july": '07',  "august": '08',
                              "september" : '09', "november" : '10', "october": '11',  "december": '12'} 

                for word in date_to_parse: # months
                    if word in month_dict:
                        month = month_dict[word]
                        break

                for word in date_to_parse: # days
                    break

                dats = year + '-' + month + '-' + day
                return dats
            dat = get_dat(dates) # YYYY-MM-DD

            def get_so(so):
                return so 
            so = get_so(sort_order) # sort order optional, if not EMPTY then sort by newest

            def get_inf(inf):
                return inf 
            inf = get_inf(influence) # sort order optional, if not EMPTY then sort by number of citations

            def get_aut(authors):
                authors_list = []
                for author_identified in authors:
                    for x in author_identified:
                        x = x.replace(' and','')
                        authors_list = [y for y in x.split(',')]
                        
                return authors_list 
            aut = get_aut(authors) # list of author strings 

            def get_keys(keywords):
                return keywords
            key = get_keys(keywords) # list of keyword strings

            criteria = [cat, dat, so, inf, aut, key]

            print("FINAL: ", cat, dat, so, inf, aut, key)

            json_file = os.path.join(os.getcwd(),'arxiv_demo.json') # OR SQL PASTE HERE #######################################################################################################
            # also url download ?

            def return_searches(json_filename, criteria):
                import ijson

                start = time.time()
                rets = []

                f = open(json_filename)
                objects = ijson.items(f, 'root.item')

                papers_ = (o for o in objects)

                for papers in papers_:
                    if criteria[0] == papers["categories"] or criteria[1] == papers["authors"] or criteria[4] == papers["update_date"]:
                        rets.append(papers)
                        if len(rets) > 3:
                            return rets
                        if time.time() - start > 5:
                            return rets
                
                return rets # wont get here


            print('\n',return_searches(json_file, criteria),'\n')

            # --- | Json Get | --- 

            searchres = {  "organic_results":[
                {
                "position":  2,
                "title": "Best Coffee Shops in Austin, Winter 2019 - Eater Austin",
                "link":
                "https://austin.eater.com/maps/best-coffee-austin-cafes",
                "displayed_link":
                "https://austin.eater.com › maps › best-coffee-austin-cafes",
                "date":
                "Jan 10, 2020",
                "author":"BullFrog",
                "abstract":
                "28 Excellent Coffee Shops in Austin, Winter 2020 · 1. Machine Head Coffee · 2. Epoch Coffee · 3. Houndstooth Coffee · 4. Cherrywood ...",
                "score":25
                },
                {
                "position":3,
                "title": "13 Health Benefits of Coffee, Based on Science - Healthline",
                "link": "https://www.healthline.com/nutrition/top-13-evidence-based-health-benefits-of-coffee",
                "displayed_link":  "https://healthline.com › nutrition › top-13-evidence-bas...",
                "date": "Sep 20, 2018",
                "abstract":  "Coffee is the biggest source of antioxidants in the diet. It has many health benefits, such as improved brain function and a lower risk of serious ..."
                },
                {
                "position":  4,
                "title":
                "Peet's Coffee: The Original Craft Coffee",
                "link":
                "https://www.peets.com/",
                "displayed_link":
                "https://peets.com",
                "author":"BullFrog",
                "abstract":
                "Since 1966, Peet's Coffee has offered superior coffees and teas by sourcing the best quality coffee beans and tea leaves in the world and adhering to strict ...",
                "score":23
                }]
            }
            return json.dumps(searchres)

if __name__ == '__main__':
    from sys import argv
    if len(argv) == 2:
        MyServer("127.0.0.1",argv[1]).serve_forever()
    else:
        MyServer("127.0.0.1", 8001).serve_forever()
