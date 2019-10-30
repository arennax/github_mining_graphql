import pandas as pd
temp_df = pd.read_csv('../outputs/test_0_copy.csv', sep='\t')

renamed_df = temp_df.rename(columns={"node.name": "name",
                        "node.url": "url",
                        "node.pullRequests.totalCount": "pullRequests",
                        "node.openpullRequests.totalCount": "openpullRequests",
                        "node.closedPullRequests.totalCount": "closedPullRequests",
                        "node.mergedPullRequests.totalCount": "mergedPullRequests",
                        "node.forks.totalCount": "forks",
                        "node.commitComments.totalCount": "commitComments",
                        "node.mentionableUsers.totalCount": "mentionableUsers",
                        "node.assignableUsers.totalCount": "assignableUsers",
                        "node.issues.totalCount": "issues",
                        "node.totalIssues.totalIssues": "totalIssues",
                        "node.openIssues.openIssues": "openIssues",
                        "node.languages.totalCount": "languages",
                        "node.releases.totalCount": "releases",
                        "node.watchers.totalCount": "watchers",
                        "node.stargazers.totalCount": "stars",
                        "node.master.history.commits": "commits"})

renamed_df['activities'] = 1
renamed_df['contributors'] = 0
renamed_df.loc[:205,'activities'] = 0

with pd.option_context('display.max_rows', None, 'display.max_columns', None):
    print(renamed_df)

with open('../outputs/df_final.csv', 'a+', newline="") as f:
    renamed_df.to_csv(f, sep='\t', index=False, header=True)
