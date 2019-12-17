from github import Github
import pdb
import pandas as pd
import os
import time

OUTPUT_PATH = "./results/"


class Miner:
    def __init__(self, user_token):
        self.g = Github(user_token, per_page=100)
        self.results = None

    def get_data(self, repo_name, debug=True):
        self.repo_name = repo_name
        self.debug_counts = 50 if debug else 0
        self.output_folder = self._create_output_folder()
        self.repo = self.g.get_repo(repo_name)
        self._get_commits()
        self._get_issues()
        self._get_pull_requests()
        self._get_stargazers()
        self._get_forks()
        self._get_watchers()
        self.save_results()

        self._get_code_frequency()
        self._get_last_year_commits()
        self._get_contributors()

    def save_results(self):
        self.results.to_csv(OUTPUT_PATH + f"{self.repo_name.split('/')[-1]}_monthly.csv", index=False)

    def _create_output_folder(self):
        result_path = OUTPUT_PATH + self.repo_name.split("/")[-1]
        os.makedirs(result_path, exist_ok=True)
        return result_path

    def _get_contributors(self, contrib_threshold=10):
        """
         Return contribution details(add, delete) of each contributor
         from the begnning till now.

         contrib_threshold is the minimum number
         of contributions required to create a profile for this contributor.

         csv file naming: project_name + contributor + "{# of contribution}" + "contributor_id"
        """
        cbs = self.repo.get_stats_contributors()
        for cb in cbs:
            stats = []
            author = str(cb.author.login)
            contribute = cb.total
            if contribute < contrib_threshold:
                continue
            for details in cb.weeks:
                if details.w:
                    one = {"date": str(details.w)}
                    one["additions"] = details.a
                    one["deletions"] = details.d
                    one["changes"] = str(details.a + abs(details.d))
                    stats.append(one)
            stats_pd = pd.DataFrame.from_records(stats)
            path = os.path.join(
                self.output_folder,
                f"{self.repo_name.split('/')[-1]}_contributor_{contribute}_{author}.csv",
            )
            stats_pd.to_csv(
                path,
                index=False,
                columns=["date", "additions", "deletions", "changes"],
            )

    def _get_code_frequency(self):
        """
        The Total number of commits authored by the contributor.
        """
        code_freq = self.repo.get_stats_code_frequency()
        stats = []
        for cf in code_freq:
            one = {"date": str(cf.week)}
            one["additions"] = cf.additions
            one["deletions"] = cf.deletions
            one["changes"] = str(cf.additions + abs(cf.deletions))
            stats.append(one)
        stats_pd = pd.DataFrame.from_records(stats)
        path = os.path.join(
            self.output_folder, f"{self.repo_name.split('/')[-1]}_codefrequency.csv"
        )
        stats_pd.to_csv(
            path, index=False, columns=["date", "additions", "deletions", "changes"],
        )

    def _get_last_year_commits(self):
        """
        Returns the last one year of commit activity grouped by week.
        """
        all_commits = self.repo.get_stats_commit_activity()
        stats = []
        counts = self.debug_counts
        for commit in all_commits:
            if self.debug_counts:
                counts = - 1
                if counts == 0:
                    break
            one = {"total": commit.total}
            one["week"] = commit.week
            one["days"] = commit.days
            stats.append(one)
        stats_pd = pd.DataFrame.from_records(stats)
        path = os.path.join(
            self.output_folder, f"{self.repo_name.split('/')[-1]}_last_year_commits.csv"
        )
        stats_pd.to_csv(
            path, index=False, columns=["total", "week", "days"],
        )

    def _get_commits(self):
        """
        Returns the last one year of commit activity grouped by week.
        """
        all_commits = self.repo.get_commits()
        stats = []
        counts = self.debug_counts
        for commit in all_commits:
            if self.debug_counts:
                counts -= 1
                if counts == 0:
                    break
            one = {"commit_id": commit.sha}
            one["committer_id"] = commit.author.login if commit.author else "None"
            one["committed_at"] = commit.raw_data["commit"]["committer"]["date"]
            one["commit_comment"] = commit.raw_data["commit"]["comment_count"]
            stats.append(one)

        stats_pd = pd.DataFrame.from_records(stats)
        stats_pd.committed_at = stats_pd.committed_at.astype("datetime64[ns]")
        start_date, end_date = (
            str(stats_pd.committed_at.min())[:7],
            str(stats_pd.committed_at.max())[:7],
        )  # i.e, 2019-09
        new_pd = pd.DataFrame(
            {"dates": pd.date_range(start=start_date, end=end_date, freq="MS")}
        )
        new_pd["monthly_commits"] = 0
        new_pd["monthly_commit_comments"] = 0
        new_pd["monthly_contributors"] = 0

        for i in range(len(new_pd)):
            if i != len(new_pd) - 1:
                mask = (stats_pd.committed_at >= new_pd.dates[i]) & (
                        stats_pd.committed_at < new_pd.dates[i + 1]
                )
            else:
                mask = stats_pd.committed_at >= new_pd.dates[i]
            new_pd["monthly_commit_comments"].iloc[i] = sum(
                stats_pd[mask].commit_comment
            )
            new_pd["monthly_commits"].iloc[i] = len(stats_pd[mask])
            print(stats_pd[mask].committer_id.unique())
            new_pd["monthly_contributors"].iloc[i] = len(
                stats_pd[mask].committer_id.unique()
            )
        self.results = new_pd

        path = os.path.join(
            self.output_folder,
            f"{self.repo_name.split('/')[-1]}_commits_and_comments.csv",
        )
        stats_pd.to_csv(
            path,
            index=False,
            columns=["commit_id", "committer_id", "committed_at", "commit_comment"],
        )

    def _get_issues(self, state="all"):
        """
        Get all the issues from this repo.
        In the csv file, we have the following cols:

        issue_id, state(open/closed), comments(int), created_at, closed_at

        """
        all_issues = self.repo.get_issues(state=state)
        stats = []
        counts = self.debug_counts
        for issue in all_issues:
            if self.debug_counts:
                counts -= 1
                if counts == 0:
                    break
            one = {"id": str(issue.number)}
            one["state"] = issue.state
            one["comments"] = issue.comments
            one["created_at"] = str(issue._created_at.value)
            one["closed_at"] = (
                str(issue._closed_at.value)
                if issue._closed_at.value
                else str(pd.to_datetime(1))
            )  # set not closed issue date to 1970-01-01 for calcualte monthly closed issues.
            one["title"] = str(issue.title)
            stats.append(one)
        stats_pd = pd.DataFrame.from_records(stats)
        stats_pd.created_at = stats_pd.created_at.astype("datetime64[ns]")
        stats_pd.closed_at = stats_pd.closed_at.astype(
            "datetime64[ns]", errors="ignore"
        )

        self.results["monthly_open_issues"] = 0
        self.results["monthly_closed_issues"] = 0
        self.results["monthly_issue_comments"] = 0  # comments from open + closed issues

        for i in range(len(self.results)):
            if i != len(self.results) - 1:
                open_mask = (
                        (stats_pd.created_at >= self.results.dates[i])
                        & (stats_pd.created_at < self.results.dates[i + 1])
                        & (stats_pd.state == "open")
                )
                closed_mask = (
                        (stats_pd.closed_at >= self.results.dates[i])
                        & (stats_pd.closed_at < self.results.dates[i + 1])
                        & (stats_pd.state == "closed")
                )
            else:
                open_mask = (stats_pd.created_at >= self.results.dates[i]) & (
                        stats_pd.state == "open"
                )
                closed_mask = (stats_pd.closed_at >= self.results.dates[i]) & (
                        stats_pd.state == "closed"
                )
            self.results["monthly_open_issues"].iloc[i] = len(stats_pd[open_mask])
            self.results["monthly_closed_issues"].iloc[i] = len(stats_pd[closed_mask])
            self.results["monthly_issue_comments"].iloc[i] = sum(
                stats_pd[open_mask].comments
            ) + sum(
                stats_pd[closed_mask].comments
            )  # comments on both open + closed issues.

        path = os.path.join(
            self.output_folder, f"{self.repo_name.split('/')[-1]}_issues.csv"
        )
        stats_pd.to_csv(
            path,
            index=False,
            columns=["id", "title", "state", "comments", "created_at", "closed_at"],
        )

    def _get_stargazers(self):
        """
        Get monthly stargazers and update it in self.results, will finally save to .csv file
        """
        stargazer = self.repo.get_stargazers_with_dates()
        stats = []
        counts = self.debug_counts
        for star in stargazer:
            if self.debug_counts:
                counts -= 1
                if counts == 0:
                    break
            one = {"user_id": star.user.login}
            one["starred_at"] = star.starred_at
            stats.append(one)
        stats_pd = pd.DataFrame.from_records(stats)
        self.results["monthly_stargazer"] = 0
        for i in range(len(self.results)):
            if i != len(self.results) - 1:
                mask = (stats_pd.starred_at >= self.results.dates[i]) & (
                        stats_pd.starred_at < self.results.dates[i + 1]
                )
            else:
                mask = stats_pd.starred_at >= self.results.dates[i]
            self.results["monthly_stargazer"].iloc[i] = len(stats_pd[mask])
        path = os.path.join(
            self.output_folder, f"{self.repo_name.split('/')[-1]}_stargazer.csv"
        )
        stats_pd.to_csv(
            path, index=False, columns=["user_id", "starred_at"],
        )

    def _get_forks(self):
        """
        Get monthly forks and update it in self.results, will finally save to .csv file
        """
        forks = self.repo.get_forks()
        stats = []
        counts = self.debug_counts
        for fork in forks:
            if self.debug_counts:
                counts -= 1
                if counts == 0:
                    break
            one = {"user_id": fork.owner.login}
            one["created_at"] = fork.created_at
            stats.append(one)
        stats_pd = pd.DataFrame.from_records(stats)
        self.results["monthly_forks"] = 0
        for i in range(len(self.results)):
            if i != len(self.results) - 1:
                mask = (stats_pd.created_at >= self.results.dates[i]) & (
                        stats_pd.created_at < self.results.dates[i + 1]
                )
            else:
                mask = stats_pd.created_at >= self.results.dates[i]
            self.results["monthly_forks"].iloc[i] = len(stats_pd[mask])
        path = os.path.join(
            self.output_folder, f"{self.repo_name.split('/')[-1]}_forks.csv"
        )
        stats_pd.to_csv(path, index=False, columns=["user_id", "created_at"])

    def _get_watchers(self):
        """
        ### FIXME for some reasons, this function will intrigure more API calls.
        and will use up all the quota. Need to debug.

        """
        watchers = self.repo.get_watchers()
        stats = []
        counts = self.debug_counts
        for watcher in watchers:
            if self.debug_counts:
                counts -= 1
                if counts == 0:
                    break
            one = {"user_id": watcher.login}
            one["created_at"] = watcher.created_at
            stats.append(one)
        stats_pd = pd.DataFrame.from_records(stats)
        self.results["monthly_watchers"] = 0
        for i in range(len(self.results)):
            if i != len(self.results) - 1:
                mask = (stats_pd.created_at >= self.results.dates[i]) & (
                        stats_pd.created_at < self.results.dates[i + 1]
                )
            else:
                mask = stats_pd.created_at >= self.results.dates[i]
            self.results["monthly_watchers"].iloc[i] = len(stats_pd[mask])
        path = os.path.join(
            self.output_folder, f"{self.repo_name.split('/')[-1]}_watchers.csv"
        )
        stats_pd.to_csv(path, index=False, columns=["user_id", "created_at"])

    def _get_pull_requests(self, state="all"):
        """
        Get all the PR from this repo. Note that issues and PR share the same ID system.
        In the csv file, we have the following cols:

        PR_id, state(open/closed), comments, created_at, closed_at, merged, merged_at,

        """
        pulls = self.repo.get_pulls(state=state, sort="created", base="master")
        stats = []
        # fmt: off
        for pr in pulls:
            one = {"id": str(pr.number)}
            one["state"] = pr.state
            one["comments"] = pr.comments
            one["created_at"] = str(pr.created_at)
            # set not closed pr date to 1970-01-01 for calcualte monthly stats
            one["closed_at"] = (str(pr.closed_at) if pr.closed_at else str(pd.to_datetime(1)))
            one["merged"] = bool(pr._merged.value)
            # set not merged pr date to 1970-01-01 for calcualte monthly stats.
            one["merged_at"] = (str(pr.merged_at) if pr.merged_at else str(pd.to_datetime(1)))
            one["merged_by"] = str(pr.merged_by.login) if pr.merged_by else None
            stats.append(one)
        stats_pd = pd.DataFrame.from_records(stats)
        # pdb.set_trace()
        stats_pd.created_at = stats_pd.created_at.astype("datetime64[ns]")
        stats_pd.closed_at = stats_pd.closed_at.astype("datetime64[ns]", errors="ignore")
        stats_pd.merged_at = stats_pd.merged_at.astype("datetime64[ns]", errors="ignore")

        self.results["monthly_open_PRs"] = 0
        self.results["monthly_closed_PRs"] = 0
        self.results["monthly_merged_PRs"] = 0
        self.results["monthly_PR_mergers"] = 0
        self.results["monthly_PR_comments"] = 0  # comments from open + closed issues
        # fmt: on
        for i in range(len(self.results)):
            if i != len(self.results) - 1:
                open_mask = (
                        (stats_pd.created_at >= self.results.dates[i])
                        & (stats_pd.created_at < self.results.dates[i + 1])
                )
                closed_mask = (
                        (stats_pd.closed_at >= self.results.dates[i])
                        & (stats_pd.closed_at < self.results.dates[i + 1])
                        & (stats_pd.state == "closed")
                        & (stats_pd.merged == False)
                )  # all merged PR's state = close, so have to get rid of merged.
                merged_mask = (
                        (stats_pd.closed_at >= self.results.dates[i])
                        & (stats_pd.closed_at < self.results.dates[i + 1])
                        & (stats_pd.merged)
                )
            else:
                open_mask = (stats_pd.created_at >= self.results.dates[i])
                closed_mask = (
                        (stats_pd.closed_at >= self.results.dates[i])
                        & (stats_pd.state == "closed")
                        & (stats_pd.merged == False)
                )
                merged_mask = (stats_pd.closed_at >= self.results.dates[i]) & (
                    stats_pd.merged
                )
            self.results["monthly_open_PRs"].iloc[i] = len(stats_pd[open_mask])
            self.results["monthly_closed_PRs"].iloc[i] = len(stats_pd[closed_mask])
            self.results["monthly_merged_PRs"].iloc[i] = len(stats_pd[merged_mask])
            self.results["monthly_PR_mergers"].iloc[i] = len(
                stats_pd[merged_mask].merged_by.unique()
            )
            self.results["monthly_PR_comments"].iloc[i] = (
                    sum(stats_pd[open_mask].comments)
                    + sum(stats_pd[closed_mask].comments)
                    + sum(stats_pd[merged_mask].comments)
            )  # comments on both open + closed + merged PRs.

        path = os.path.join(
            self.output_folder, f"{self.repo_name.split('/')[-1]}_pr.csv"
        )
        stats_pd.to_csv(
            path,
            index=False,
            columns=[
                "id",
                "state",
                "comments",
                "created_at",
                "closed_at",
                "merged",
                "merged_at",
            ],
        )


if __name__ == "__main__":
    token = "token XXX"
    # repo_name = "PyGithub/PyGithub"
    # miner = Miner(token)
    # miner.get_data(repo_name, debug=False)

    temp_list = [
        "PyGithub/PyGithub"
        "GoogleCloudPlatform/training-data-analyst",
        "paulhodel/jexcel",
        "hunkim/PyTorchZeroToAll",
        "cookieY/Yearning",
        "christabor/flask_jsondash",
        "ExtendRealityLtd/VRTK",
        "yipianfengye/android-adDialog",
        "udacity/self-driving-car-sim",
        "transitive-bullshit/create-react-library",
        "yjhjstz/deep-into-node",
        "stfalcon-studio/ChatKit",
        "QUANTAXIS/QUANTAXIS",
        "google/pprof",
        "mattallty/Caporal.js",
        "dotnetcore/Util",
        "santinic/pampy",
        "brillout/awesome-angular-components",
        "Aufree/awesome-wechat-weapp",
        "chiphuyen/machine-learning-systems-design"
    ]

    for i in range(20):
        repo_name = temp_list[i]
        miner = Miner(token)
        miner.get_data(repo_name, debug=True)
        time.sleep(10)
