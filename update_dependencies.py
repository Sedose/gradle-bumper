import re
import requests
import argparse

cache_latest_versions = {}

def get_latest_version(dependency_group, dependency_artifact):
    key = f"{dependency_group}:{dependency_artifact}"
    if key in cache_latest_versions:
        return cache_latest_versions[key]
    url = f"https://search.maven.org/solrsearch/select?q=g:\"{dependency_group}\"+AND+a:\"{dependency_artifact}\"&rows=1&wt=json"
    response = requests.get(url)
    if response.status_code != 200:
        return None
    data = response.json()
    docs = data.get("response", {}).get("docs", [])
    if not docs:
        return None
    latest_version = docs[0].get("latestVersion")
    cache_latest_versions[key] = latest_version
    return latest_version

dependency_pattern = re.compile(r'"([\w\.\-]+):([\w\.\-]+):([\w\.\-]+)"')

def update_dependency(match):
    dependency_group, dependency_artifact, current_version = match.groups()
    latest_version = get_latest_version(dependency_group, dependency_artifact)
    if latest_version and latest_version != current_version:
        print(f"Updating {dependency_group}:{dependency_artifact} from {current_version} to {latest_version}")
        return f'"{dependency_group}:{dependency_artifact}:{latest_version}"'
    return match.group(0)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("file", help="Path to the build.gradle.kts file")
    arguments = parser.parse_args()
    with open(arguments.file, "r") as file:
        file_contents = file.read()
    updated_file_contents = dependency_pattern.sub(update_dependency, file_contents)
    with open(arguments.file, "w") as file:
        file.write(updated_file_contents)
    print("Dependency versions have been updated to the latest stable versions.")

if __name__ == "__main__":
    main()
