# Elastic Beanstalk Docker AL2023 Monitor

Checks the AWS Supported Platforms page every 6 hours.

If the Docker AL2023 platform version changes:

- Posts to Slack
- Updates version.txt
- Commits the new version back to GitHub

## Setup

1. Create a Slack Incoming Webhook.

2. Add the webhook as a GitHub Secret named

SLACK_WEBHOOK_URL

3. Push to GitHub.

4. Run the workflow once manually.

Done.
