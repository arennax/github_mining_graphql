import requests
import pprint
import pandas as pd
from pandas.io.json import json_normalize

headers = {"Authorization": "token XXX"}


def run_query(query):  # A simple function to use requests.post to make the API call. Note the json= section.
    request = requests.post('https://api.github.com/graphql', json={'query': query}, headers=headers)
    if request.status_code == 200:
        return request.json()
    else:
        raise Exception("Query failed to run by returning code of {}. {}".format(request.status_code, query))


# # The GraphQL query (with a few aditional bits included) itself defined as a multi-line string.
# query = """
# {
#   viewer {
#     login
#   }
#   rateLimit {
#     limit
#     cost
#     remaining
#     resetAt
#   }
# }
# """
#
# result = run_query(query)  # Execute the query
# remaining_rate_limit = result["data"]["rateLimit"]["remaining"]  # Drill down the dictionary
# print("Remaining rate limit - {}".format(remaining_rate_limit))

query = """
{{
   search(query: "{queryString}", type: REPOSITORY, first: {maxItems}) {{
     # repositoryCount
     edges {{
       node {{
         ... on Repository {{
           name
           url
           pullRequests {{ totalCount }}
           openpullRequests: pullRequests(states:OPEN) {{totalCount}}
           closedPullRequests: pullRequests(states:CLOSED) {{totalCount}}
           mergedPullRequests: pullRequests(states:MERGED) {{totalCount}}
           forks {{ totalCount }}
           commitComments {{ totalCount }}
           mentionableUsers {{ totalCount }}
           assignableUsers {{ totalCount }}
           issues {{ totalCount }}
           totalIssues: issues {{totalIssues: totalCount}}
           openIssues: issues(states:[OPEN]) {{openIssues: totalCount}}
           languages {{ totalCount }}
           releases {{ totalCount }}
           watchers {{ totalCount }}
           stargazers {{ totalCount }}
           master: object(expression:"master") {{
             ... on Commit {{
               history(since:  "2019-04-30T00:00:00Z") {{
                 # edges {{
                 #   node {{
                 #     author {{ email }}
                 #   }}
                 # }}
                 commits: totalCount
               }}
             }}
           }}
         }}
       }}
    }}
  }}
}}
"""
variables = {
   'queryString' : 'is:public archived:true stars:1000..1528 created:>=2014-01-01',
   'maxItems' : '10'
    # stars:10000..20000 repo:tensorflow/tensorflow language:C++ vue in:name pushed:>=2013-02-01
}


result = run_query(query.format(**variables))

# print(type(result))
# pprint.pprint(result)

temp0 = json_normalize(result, record_path=['data', 'search', 'edges'])
# temp1 = flatten(result)
# temp2 = (flatten(d) for d in temp1)
# df = pd.DataFrame.from_dict(temp1.items()).T
#
# print(df)
# pprint.pprint(temp0)
# print(temp0)
#
with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
   print(temp0)

# temp0.to_csv('./output/test_0.csv', sep='\t', index=False)
# temp0.to_excel('~./output/test_0.xlsx')

with open('./output/test_1.csv', 'a+', newline="") as f:
    temp0.to_csv(f, sep='\t', index=False, header=False)
