import os
import re
import requests

from bs4 import BeautifulSoup

URL = "https://docs.aws.amazon.com/elasticbeanstalk/latest/platforms/platforms-supported.html"

ANCHOR = (
    "https://docs.aws.amazon.com/elasticbeanstalk/latest/"
    "platforms/platforms-supported.html#platforms-supported.docker"
)

WEBHOOK = os.environ["SLACK_WEBHOOK_URL"]


def get_current_version():
    html = requests.get(URL, timeout=30).text

    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text(" ", strip=True)

    #
    # Looks for:
    #
    # Docker running on 64bit Amazon Linux 2023
    # v4.13.4
    #
    pattern = r"Docker.*?Amazon Linux 2023.*?v(\d+\.\d+\.\d+)"
    match = re.search(pattern, text, re.S)

    if not match:
        raise RuntimeError("Couldn't locate Docker AL2023 version")

    return match.group(1)


def send_slack(old, new):

    payload = {
        "text":
f"""🚀 *Elastic Beanstalk Docker AL2023 Updated*

*Previous Version:* `{old}`
*New Version:* `{new}`

<{ANCHOR}|View Docker AL2023 Supported Platforms>
"""
    }

    requests.post(
        WEBHOOK,
        json=payload,
        timeout=30,
    ).raise_for_status()


def main():

    current = get_current_version()

    with open("version.txt") as f:
        previous = f.read().strip()

    print(f"Current : {current}")
    print(f"Previous: {previous}")

    if current == previous:
        print("No change.")
        return

    send_slack(previous, current)

    with open("version.txt", "w") as f:
        f.write(current)

    print("Updated version.txt")


if __name__ == "__main__":
    main()
