import re
import json
import os
from typing import Literal

import urllib.request
from urllib.error import URLError

class VersionChecker:
    def __init__(self, url: str):
        self.url = url

    def get_tags(self) -> list:
        try:
            # Call the GitHub API and retrieve the tags
            with urllib.request.urlopen(self.url) as f:
                tags_str = f.read().decode('utf-8')
            return json.loads(tags_str)
        except URLError as e:
            print(f"Error while fetching tags from GitHub API: {e}")
            exit(1)

    def get_latest_version(self, tags: list) -> str:
      for tag in tags:
          if tag['name'].startswith('gopls/v'):
              return tag['name'].split('v')[1]

      print("Could not find latest version from tags.")
      exit(1)

    def get_version_locally(self) -> str:
        try:
            with open("plugin/version.py", "r") as f:
                groups = re.search(r"\d+\.\d+\.\d+", f.read())
                if groups is None:
                    raise ValueError("Could not find version in plugin/version.py.")
                return groups.group(0)
        except (IOError, ValueError) as e:
            print(f"Error while reading plugin/version.py: {e}")
            exit(1)


    def compare_semantic_versions(self, v1: str, v2: str) -> Literal[0, 1]:
        # Split the versions into lists of integers
        v1_parts = [int(x) for x in v1.split(".")]
        v2_parts = [int(x) for x in v2.split(".")]

        # Compare each part of the version
        for i in range(min(len(v1_parts), len(v2_parts))):
            if v1_parts[i] > v2_parts[i]:
                return 0
            elif v1_parts[i] < v2_parts[i]:
                return 1
        # If all parts are equal, return 1 if v2 has more parts
        return 1 if len(v2_parts) > len(v1_parts) else 0

    def check_for_update(self):
        tags = self.get_tags()
        latest_version = self.get_latest_version(tags)
        local_version = self.get_version_locally()

        # Check if update is required
        requires_update = self.compare_semantic_versions(local_version, latest_version)
        branch_name = latest_version.replace(".", "_")

        with open(os.environ['GITHUB_OUTPUT'], 'a') as fh:
            print(f'REQUIRES_UPDATE={requires_update}', file=fh)
            print(f'LATEST_VERSION={latest_version}', file=fh)
            print(f'BRANCH_NAME={branch_name}', file=fh)


url = "https://api.github.com/repos/golang/tools/tags"
VersionChecker(url=url).check_for_update()
