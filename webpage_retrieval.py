from google_search import *
from bs4 import BeautifulSoup
import requests
import spacy
from collections import defaultdict
from spanbert import SpanBERT
from spacy_help_functions import create_entity_pairs,filter_relation
engine_id = "becd76ddad3b6ac04"
API_KEY = "AIzaSyCVc0q0-3jtaEc__0I8GORSt2339A4mRsw"
query = "bill gates microsoft"

entities_of_interest = {
    1: ["PERSON", "ORGANIZATION"],
    2: ["PERSON", "ORGANIZATION"],
    3: ["PERSON", "LOCATION", "CITY", "STATE_OR_PROVINCE", "COUNTRY"],
    4: ["ORGANIZATION", "PERSON"]
}

entities_pos = {
    1: {"subj" : ["PERSON"], "obj" : ["ORGANIZATION"]},
    2: {"subj" : ["PERSON"], "obj" : ["ORGANIZATION"]},
    3: {"subj" : ["PERSON"], "obj" : ["LOCATION", "CITY", "STATE_OR_PROVINCE", "COUNTRY"]},
    4: {"subj" : ["ORGANIZATION"], "obj" : ["PERSON"]}
}

internal_name = {
    1: "per:schools_attended",
    2: "per:employee_of",
    3: "per:cities_of_residence",
    4: "org:top_members/employees"
}



def retrieve_split(url):
    print("Fetching text from url ...")
    try:
        response = requests.get(url, timeout=20)
    except requests.exceptions.HTTPError:
        print("Unable to fetch url due to HTTP error. Url skipped.\n")
        return []
    except requests.exceptions.ConnectionError:
        print("Unable to fetch url due to Connection error. Url skipped.\n")
        return []
    except requests.exceptions.Timeout:
        print("Unable to fectch url due to timeout. Url skipped.\n")
        return []
    except requests.exceptions.RequestException:
        print("Unable to fetch url due to requests error. Url skipped.\n")
        return []
    raw_html = response.content
    soup = BeautifulSoup(raw_html, 'html.parser')
    for raw_text in soup(['style', 'script']):
        raw_text.decompose()
    plain_text = ' '.join(soup.stripped_strings)
    # plain_text = soup.get_text(separator='\n')
    # plain_text = plain_text.strip()
    if len(plain_text)>20000:
        print("Trimming webpage content from {} to 20000 characters".format(len(plain_text)))
        plain_text = plain_text[:20000]
    print("Webpage length (num characters):",len(plain_text))

    print("Annotating the webpage using spacy...")
    nlp = spacy.load("en_core_web_lg")
    doc = nlp(plain_text)
    return doc


def get_relation(res, doc, r_id, conf=0.7):
    if not len(doc):
        return defaultdict(int)
    spanbert = SpanBERT("./pretrained_spanbert")
    num_sentences = len([s for s in doc.sents])
    num_ext_sentences = 0
    num_relations = 0
    num_ext_relations = 0
    print("Extracted {} sentences. Processing each sentence...".format(num_sentences))
    count = 0
    for sentence in doc.sents:
        count += 1
        if count%5 == 0:
            print("Processing {}/{} sentences".format(count,num_sentences))
        # print("---------NameEntity---------")
        entity_pairs = create_entity_pairs(sentence, entities_of_interest[r_id])
        examples = []
        if len(entity_pairs) == 0:
            continue
        for ep in entity_pairs:
            ele1 = {"tokens": ep[0], "subj": ep[1], "obj": ep[2]}
            if (ele1["subj"][1] in entities_pos[r_id]["subj"]) and (ele1["obj"][1] in entities_pos[r_id]["obj"]):
                examples.append(ele1)
            ele2 = {"tokens": ep[0], "subj": ep[2], "obj": ep[1]}
            if (ele2["subj"][1] in entities_pos[r_id]["subj"]) and (ele2["obj"][1] in entities_pos[r_id]["obj"]):
                examples.append(ele2)

        if len(examples) == 0:
            continue
        preds = spanbert.predict(examples)
        relations, num_relations, num_ext_relations = filter_relation(examples, preds, conf, num_relations, num_ext_relations,internal_name[r_id])
        dict_relation = dict(relations)
        if dict_relation:
            num_ext_sentences += 1
            # add new relations to set X and remove exact duplicates from set X
            for relat in dict_relation:
                if(res[relat]<dict_relation[relat]):
                    res[relat] = dict_relation[relat]

    print("Extracted annotations for  {}  out of total {} sentences".format(num_ext_sentences, num_sentences))
    print("Relations extracted from this website: {} (Overall: {}) \n".format(num_ext_relations, num_relations))
    print()
    return res


if __name__ == '__main__':
    print("---------------------")
    url_set = set()
    url_list = search(engine_id, API_KEY, query, url_set)
    print(url_list)
    doc = retrieve_split(url_list[0])
    tot_relations = get_relation(doc,2)