import requests
import sys
from shutil import copyfile

SNAP_NAME = "k6"
GITHUB_REPO = "grafana/k6"


def update_file(file_name, repo, version):
    with open(file_name) as file_handle:
        file_contents = file_handle.read()

    file_contents = file_contents.replace("$GITHUB_REPO", repo)
    file_contents = file_contents.replace("$VERSION", version)

    with open(file_name, "w") as file_handle:
        file_handle.write(file_contents)


def get_latest_version(channel_maps):
    newest_channel = None
    for channel_map in channel_maps:
        if not newest_channel:
            newest_channel = channel_map
        else:
            if channel_map["channel"]["risk"] == "stable":
                newest_channel = channel_map

        if newest_channel["channel"]["risk"] == "stable":
            break

    return newest_channel["version"]


snap_info = requests.get(
    f"https://api.snapcraft.io/v2/snaps/info/{SNAP_NAME}",
    headers={"Snap-Device-Series": "16"},
).json()
last_published_version = get_latest_version(snap_info["channel-map"])

releases = requests.get(
    f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
).json()
last_github_release = releases["tag_name"]

if releases["prerelease"]:
    print("Exit: prerelease")
    sys.exit(1)

if last_published_version == last_github_release:
    print("Exit: no new version")
    sys.exit(1)

copyfile("_snapcraft.yaml", "snapcraft.yaml")
update_file("snapcraft.yaml", GITHUB_REPO, last_github_release)
