from collections import defaultdict

from webpage_retrieval import *
from google_search import *

import argparse

internal_name = {
    1: "per:schools_attended",
    2: "per:employee_of",
    3: "per:cities_of_residence",
    4: "org:top_members/employees"
}

parser = argparse.ArgumentParser()

parser.add_argument('--engine_id', type=str, default="becd76ddad3b6ac04", help='Engine_id for Google API.')
parser.add_argument('--API_KEY', type=str, default="AIzaSyCVc0q0-3jtaEc__0I8GORSt2339A4mRsw",
                    help='KEY for Google API.')
parser.add_argument('--r', type=int, default=2,
                    help='Relation to extract: 1 : Schools_Attended, 2 : Work_For, 3 : Live_In,  4 : Top_Member_Employees')
parser.add_argument('--t', type=float, default=0.7,
                    help='Extraction confidence threshold')
parser.add_argument('--q', type=str, default="bill gates microsoft",
                    help='Seed query')
parser.add_argument('--k', type=int, default=10,
                    help='Number of tuples')
args = parser.parse_args()


def print_parameters():
    print("Parameters:")
    print("Client key  = ", args.API_KEY)
    print("Engine key  = ", args.engine_id)
    print("Relation  = ", internal_name[args.r])
    print("Threshold = ", args.t)
    print("Query  = ", args.q)
    print("# of Tuples = ", args.k)
    print("Loading necessary libraries; This should take a minute or so ...")


if __name__ == '__main__':
    print_parameters()
    query_list = list()
    url_set = set()
    tot_relations = defaultdict(int)
    engine_id = args.engine_id
    API_KEY = API_KEY
    q = args.q
    r = args.r
    t = args.t
    k = args.k
    iter_count = 0

    while True:
        query_list.append(q)
        print("=========== Iteration: {} - Query: {} =========== \n".format(iter_count, q))
        print()
        url_list = search(engine_id, API_KEY, q, url_set)
        for i in range(len(url_list)):
            url = url_list[i]
            print("URL ( {} / {} ): {}".format(i+1, len(url_list),url))
            doc = retrieve_split(url)
            # X
            tot_relations.update(get_relation(defaultdict(int), doc, r, t))

        tot_relations = dict(reversed(sorted(tot_relations.items(), key=lambda x: x[1])))
        num_relations = len(tot_relations)
        print("================== ALL RELATIONS for {} ( {} ) =================".format(internal_name[r], num_relations))

        for key, conf in tot_relations.items():
            print("Confidence: {} \t\t| Subject: {} \t\t| Object: {}".format(conf, key[0], key[2]))
        iter_count += 1

        if num_relations >= k:
            print("Total # of iterations =", str(iter_count))
            break
        else:
            q = None
            for key in tot_relations.keys():
                if key is not None:
                    subj, obj = key[0], key[2]
                    temp = str(subj) + " " + str(obj)
                    if len(temp) > 1 and temp not in query_list:
                        q = temp
                        break
            if q is None:
                print("No more tuples. ISE has stalled")