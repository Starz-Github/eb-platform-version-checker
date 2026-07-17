import os
import re

import requests
from bs4 import BeautifulSoup

SUPPORTED_PLATFORMS_URL = (
    "https://docs.aws.amazon.com/elasticbeanstalk/latest/"
    "platforms/platforms-supported.html"
)

DOCKER_AL2023_ANCHOR = (
    "https://docs.aws.amazon.com/elasticbeanstalk/latest/"
    "platforms/platforms-supported.html#platforms-supported.docker"
)

RELEASE_NOTES_URL = (
    "https://docs.aws.amazon.com/elasticbeanstalk/latest/"
    "relnotes/relnotes.html"
)

SLACK_WEBHOOK_URL = os.environ["SLACK_WEBHOOK_URL"]


def get_current_version():
    """
    Find the Docker AL2023 platform version from the AWS supported
    platforms table.
    """

    response = requests.get(
        SUPPORTED_PLATFORMS_URL,
        timeout=30,
        headers={
            "User-Agent": "Mozilla/5.0"
        },
    )

    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    for table in soup.find_all("table"):

        for row in table.find_all("tr"):

            cells = row.find_all(["td", "th"])

            if len(cells) < 2:
                continue

            platform_name = cells[0].get_text(" ", strip=True)

            if (
                "Docker" in platform_name
                and "Amazon Linux 2023" in platform_name
            ):

                row_text = row.get_text(" ", strip=True)

                version_match = re.search(
                    r"v?(\d+\.\d+\.\d+)",
                    row_text,
                )

                if version_match:
                    version = version_match.group(1)

                    print(
                        f"Found platform: {platform_name}"
                    )
                    print(
                        f"Found version: {version}"
                    )

                    return version

    raise RuntimeError(
        "Could not find Docker AL2023 version on AWS page."
    )


def send_slack_notification(old_version, new_version):
    """
    Send Slack notification when version changes.
    """

    message = {
        "text": (
            "🚀 *Elastic Beanstalk Docker AL2023 Updated*\n\n"
            f"*Previous Version:* `{old_version}`\n"
            f"*New Version:* `{new_version}`\n\n"
            f"<{DOCKER_AL2023_ANCHOR}|View Docker AL2023 Supported Platforms>\n"
            f"<{RELEASE_NOTES_URL}|View Elastic Beanstalk Release Notes>"
        )
    }

    response = requests.post(
        SLACK_WEBHOOK_URL,
        json=message,
        timeout=30,
    )

    response.raise_for_status()


def main():

    current_version = get_current_version()

    with open("version.txt", "r") as file:
        stored_version = file.read().strip()

    print(f"Current AWS version : {current_version}")
    print(f"Stored version      : {stored_version}")

    if current_version == stored_version:
        print("No version change detected.")
        return

    print("Version change detected!")

    send_slack_notification(
        stored_version,
        current_version,
    )

    with open("version.txt", "w") as file:
        file.write(current_version)

    print(
        f"Updated version.txt to {current_version}"
    )


if __name__ == "__main__":
    main()
