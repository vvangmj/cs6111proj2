from collections import defaultdict

from webpage_retrieval import *
from google_search import *

import argparse


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
    print("Relation  = ", args.r)
    print("Threshold = ", args.t)
    print("Query  = ", args.q)
    print("# of Tuples = ", args.k)
    print("Iterative Set Expansion Results:")
    print("======================")

if __name__ == '__main__':
    print_parameters()
    url_set = set()
    tot_relations = defaultdict(int)
    engine_id = args.engine_id
    API_KEY = API_KEY
    q = args.q
    r = args.r
    t = args.t
    ###### One Iteration ######
    url_list = search(engine_id, API_KEY, q, url_set)
    for i in range(len(url_list)):
        url = url_list[i]
        print("URL ( {} / {} ): {}".format(i+1,len(url_list),url))
        doc = retrieve_split(url)
        # X
        tot_relations = get_relation(tot_relations, doc, r, t)
        # print(tot_relations)
        print()
        print()