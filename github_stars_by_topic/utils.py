from __future__ import annotations

import os
import re

from github.PaginatedList import PaginatedList
from github.Repository import Repository
from sklearn.decomposition import NMF  # type: ignore[import]

from .readmereader import fetch_readme, markdown_to_text


def generate_overview_readme(
    decomposition: NMF, feature_names: list[str], username: str
) -> str:
    text = f"# {username}'s stars by topic\n\n"
    text += (
        f"This is a list of topics covered by the starred repositories of {username}.\n"
    )

    topic_list = []
    for topic in decomposition.components_:
        top_feature_indices = topic.argsort()[:-11:-1]
        top_feature_names = [feature_names[i] for i in top_feature_indices]

        topic_name = ", ".join(top_feature_names[0:3])

        topic_directory_name = "-".join(top_feature_names[0:3])
        topic_link = topic_directory_name + os.sep + "README.md"

        topic_list_item = f"- [{topic_name}]({topic_link})"
        topic_list.append(topic_list_item)

    topic_list.sort()  # sort alphabetically
    text += "\n".join(topic_list)

    return text


def extract_texts_from_repos(
    repos: PaginatedList[Repository],
) -> tuple[list[str], dict[int, Repository]]:
    readmes: list[str] = []
    readme_to_repo: dict[int, Repository] = {}  # maps readme index to repo

    for repo in repos:
        full_repo_text = get_text_for_repo(repo)
        readme_to_repo[len(readmes)] = repo
        readmes.append(full_repo_text)

    return readmes, readme_to_repo


def get_text_for_repo(repo: Repository) -> str:
    repo_login, repo_name = repo.full_name.split(
        "/"
    )  # use full name to infer user login

    # readme = fetch_readme(user_login, repo_name, repo.id)
    readme = fetch_readme(repo)
    readme_text = markdown_to_text(readme)

    repo_name_clean = re.sub(r"[^A-z]+", " ", repo_name)

    texts = [
        str(repo.description),
        str(repo.description),
        str(repo.description),  # use description 3x to increase weight
        str(repo.language),
        readme_text,
        repo_name_clean,
    ]
    return " ".join(texts)
