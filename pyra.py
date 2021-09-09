"""
JIRA REST API documentation:
https://developer.atlassian.com/cloud/jira/platform/rest/v3/
https://developer.atlassian.com/cloud/jira/software/rest/
"""

import json
import logging
from typing import List

import fire
import requests

from config import settings


def _get_logger(name: str, level: str = "INFO"):
    logger = logging.getLogger(name)
    logger.setLevel(level=level)
    ch = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    return logger


LOGGER = _get_logger(__name__)


def _get_auth():
    return requests.HTTPBasicAuth(
        username=settings.JIRA_EMAIL, password=settings.JIRA_API_TOKEN
    )


def _get_headers():
    return {"Accept": "application/json", "Content-Type": "application/json"}


def search(jql: str, max_results: int = 50) -> List[dict]:
    url = f"{settings.JIRA_ENDPOINT}/rest/api/3/search"
    LOGGER.info(f"Querying: {url}")

    paging_idx = 0
    issues = []
    while True:
        # get issues
        query = {"jql": jql, "startAt": paging_idx, "maxResults": max_results}
        response = requests.get(url=url, params=query)
        response = json.loads(response.text)

        try:
            issues.extend(response["issues"])
        except KeyError:
            break

        # pagination
        if paging_idx < response["total"]:
            paging_idx += max_results
        else:
            break

    LOGGER.info(f"Found {len(issues)} issues")
    return issues


def watch_project(key: str):
    """Add current user as watcher to all issues in project.

    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-watchers/#api-rest-api-3-issue-issueidorkey-watchers-post

    Args:
        key (str): Project key.
    """

    user = settings.JIRA_EMAIL

    LOGGER.info(f"Adding {user.lower()} as watcher to {key.upper()} issues")

    jql = f"project={key.upper()} and watcher!={user.lower()}"
    issues = search(jql=jql)

    for issue in issues:
        LOGGER.info(f"Adding {user.lower()} as watcher to {issue}")
        url = f"{settings.JIRA_ENDPOINT}/rest/api/3/issue/{issue}/watchers"
        response = requests.post(url=url, headers=_get_headers(), auth=_get_auth)
        response = json.loads(response.text)


if __name__ == "__main__":
    # fire.Fire()
    watch_project("RV2")
