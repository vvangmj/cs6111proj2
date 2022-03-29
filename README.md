# COMS6111 Project 2

## Team Members

- Mingjun Wang (mw3542)
- Zihuan Wu (zw2771)

## Files

```
- proj2
    - pretrained_spanbert
    - pytorch_pretrained_bert
    - main.py
    - google_search.py
    - webpage_retrieval.py
    - spacy_help_functions.py
    - spanbert.py
- transcript.txt
- README.md
```

## How to Run

In order to run the system, you can run

```
python main.py --r <relation> --t <threshold> --q "<query>" --k <#ofTuples> [--engine_id "becd76ddad3b6ac04"] [--API_KEY "AIzaSyCVc0q0-3jtaEc__0I8GORSt2339A4mRsw"]
```

or just

```
python main.py --r <relation> --t <threshold> --q "<query>" --k <#ofTuples>
```

- `<relation>`: an integer represents the relation to extract. 1: Schools_Attended, 2: Work_For, 3: Live_In, 4: Top_Member_Employees. The default value is 2;
- `<threshold>` : extraction confidence threshold. The default value is 0.7;
- `<query>`: the seed query string for searching, which should be enclosed by quotes. The default value is "bill gates microsoft";
- `<#ofTuples>` : the desired number of tuples that we request in the output;
- `<engine_id>`: your engine ID. The default value is becd76ddad3b6ac04 (our engine id);
- `<API_KEY>`: your API key. The default value is AIzaSyCVc0q0-3jtaEc__0I8GORSt2339A4mRsw (our API_KEY).

## Dependencies Installation

- make sure your Python version is 3.8.12 or newer
- numpy: run `pip install numpy==1.22.2`
- sklearn: run `pip install scikit-learn==1.0.2`
- googleapiclient: run `pip install google-api-python-client`

## Internal Design

This project implement the Iterative Set Expansion algorithm. Begin with seed queries, the system extracts specified high quality relation informations from at most 10 webpages that returned by Google Custom Search Engine, and updates the query which will be used in the next search iteration according to the extraction results.

In each iteration, we filter the URLs and only focus on those we have never seen. And we use library `requests` , `BeautifulSoup` to extract text information in those webpages. Then, the plain texts are split into separated sentences and parsed (to get named entities) using `spacy` . Then we generate entity pairs (tuples) according to the name entities which we have interest in. And use `SpanBERT`  to predict the relation of entity pairs and get respective confidence. Finally, we filter or update the repeated tuples. Return the set of tuples if there are enough number of tuples which have confidence higher than requests. Or select the unused tuple with highest confidence to be the query of next iteration.

The construction of each python file is shown as following:

- `main.py`  : Main function. Receive user input. Conduct Iteration process, update the seed query and check if the extracted tuples satisfy the requirement to quit the iteration loop.
- `google_search.py` : Obtain URLs returned by Google Custom Search Engine by searching query. And remove repeated URLs.
- `webpage_retrieval.py` :
   1. `retrieve_split` : Retrieve text from webpages. And do sentence splitting and parsing.
   2. `get_relation` : Traverse through each sentence. Creating desired entity pairs using function `create_entity_pairs`  defined in the `spacy_help_function.py` . Computing pair confidence by `SpanBERT` and filtering the results by calling function `filter_relation` in  `spacy_help_function.py`. Finally update the tuple set.
- `spacy_help_function.py` : Copied from `SpanBERT` . We only use `create_entity_pairs` and `filter_relation`, and didn't use `extract_relations` since we have some modification based on it: add one function `filter_relation`, which only return the tuples where each entity pair has the relation tag that is the same with our desired relation.
- `spanbert.py` : Directly copied from `SpanBERT` .

## Detailed Description of Step 3 (Retrieval and Relation Extraction)

1. To skip repeated URLs that we have already seen,  we maintain an set `url_set` , which store all the URLs that has been returned from Google Search Engine. So for each iteration, we discard those url which has been in the set.
2. To retrieve the corresponding webpage, we use `requests` . And return warning information if there is any error causing the failure of retrieving.
3. To extract the plain text, we use `BeautifulSoup` . And we implement `decompose()` to remove the tags in text. And retrieve the tag content using `stripped_strings` . So that the processed text will not contain tags which messed up the original sentence. Reference: [https://www.geeksforgeeks.org/remove-all-style-scripts-and-html-tags-using-beautifulsoup/](https://www.geeksforgeeks.org/remove-all-style-scripts-and-html-tags-using-beautifulsoup/)
4. We only keep at most first 20,000 characters if the plain text is longer than that.
5. To split text into sentence and extract name entities, we load `Spacy` on the whole document. Then we can traverse through each sentence in the document and extract name entity pairs on it: we call `create_entity_pairs` on each sentence, together with a list of `entities_of_interest` , which contains the name entities that corresponding to the relation we request. e.g. if we want relation `per:schools_attend` , the list will be `["PERSON", "ORGANIZATION"]` . Then `create_entity_pairs` will only returns the entities with those tags. But those returned pairs have not been assigned `’subject’` and `’object’` that is needed as the input of `SpanBERT` . Therefore, we assign entity pairs with `’subject’` and `’object’` respectively, and construct a dictionary whose keys are `"tokens"` (sentence), `"subj"` , `"obj"` . Besides, we only keep those entity pairs which obey the correct required named entity types for each relation type.  e.g. if we want relation `per:schools_attend` , the entity type of  `"subj"` must be `"PERSON"` ; the entity type of `"obj"`must be `”ORGANIZATION”`
6. We use `SpanBERT` classifier to compute the confidence score and the relation of those entity pairs we have filtered. Those entity pairs still need a second round of filtering because some of those relation are different from the relation required. e.g. if we want relation `per:schools_attend` , we should discard those entity pairs with relation `per:employee_of` .
7. Examine the remaining entity pairs, selecting those have confidence not less than the threshold and add them to the tuple sets if the tuple are totally new, or update the higher confidence score for the tuples which have existed in the set.

## JSON API Key and Engine ID

- JSON API Key: AIzaSyCVc0q0-3jtaEc__0I8GORSt2339A4mRsw
- Engine ID: becd76ddad3b6ac04

