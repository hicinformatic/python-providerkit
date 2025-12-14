"""Social media publishing for release announcements."""

from __future__ import annotations

import json
import os
import platform
import subprocess
from pathlib import Path
from typing import Any

from .. import utils
from .release import get_project_version

PROJECT_ROOT = utils.PROJECT_ROOT

# Import utility functions
print_info = utils.print_info
print_success = utils.print_success
print_error = utils.print_error
print_warning = utils.print_warning
print_header = utils.print_header
print_separator = utils.print_separator


def format_release_message(version: str | None = None, changelog: str = "") -> str:
    """Format a release announcement message."""
    if not version:
        version = get_project_version() or "new version"

    project_name = PROJECT_ROOT.name
    message = f"🚀 {project_name} {version} is now available!\n\n"

    if changelog:
        # Truncate changelog if too long
        if len(changelog) > 200:
            changelog = changelog[:200] + "..."
        message += f"{changelog}\n\n"

    # Add common links (can be customized)
    message += "#Python #OpenSource"

    return message


def task_twitter(message: str | None = None) -> bool:
    """Publish release announcement to X (Twitter)."""
    print_info("Publishing to X (Twitter)...")

    # Check for Twitter API credentials
    api_key = os.environ.get("TWITTER_API_KEY")
    api_secret = os.environ.get("TWITTER_API_SECRET")
    access_token = os.environ.get("TWITTER_ACCESS_TOKEN")
    access_token_secret = os.environ.get("TWITTER_ACCESS_TOKEN_SECRET")
    bearer_token = os.environ.get("TWITTER_BEARER_TOKEN")

    if not bearer_token and not all([api_key, api_secret, access_token, access_token_secret]):
        print_error("Twitter API credentials not found in environment variables")
        print_info("Required: TWITTER_BEARER_TOKEN (or TWITTER_API_KEY, TWITTER_API_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET)")
        print_info("See: https://developer.twitter.com/en/docs/authentication/overview")
        return False

    if not message:
        message = format_release_message()

    # Check if tweepy is available
    try:
        import tweepy

        if bearer_token:
            client = tweepy.Client(bearer_token=bearer_token)
            response = client.create_tweet(text=message)
        else:
            auth = tweepy.OAuth1UserHandler(
                api_key, api_secret, access_token, access_token_secret
            )
            api = tweepy.API(auth)
            response = api.update_status(message)

        print_success("Tweet published successfully!")
        if hasattr(response, "data") and hasattr(response.data, "id"):
            print_info(f"Tweet ID: {response.data.id}")
        return True
    except ImportError:
        print_error("tweepy not installed. Install with: pip install tweepy")
        print_info("Message to post:")
        print_info(f"  {message}")
        return False
    except Exception as e:
        print_error(f"Error publishing to Twitter: {e}")
        return False


def task_devto(message: str | None = None, title: str | None = None) -> bool:
    """Publish release announcement to dev.to."""
    print_info("Publishing to dev.to...")

    api_key = os.environ.get("DEVTO_API_KEY")
    if not api_key:
        print_error("DEVTO_API_KEY not found in environment variables")
        print_info("Get your API key from: https://dev.to/settings/extensions")
        return False

    if not message:
        message = format_release_message()

    if not title:
        version = get_project_version()
        title = f"{PROJECT_ROOT.name} {version} Released"

    # Use dev.to API
    import requests

    url = "https://dev.to/api/articles"
    headers = {
        "api-key": api_key,
        "Content-Type": "application/json",
    }
    data = {
        "article": {
            "title": title,
            "body_markdown": f"# {title}\n\n{message}",
            "published": True,
            "tags": ["python", "opensource", "release"],
        }
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        result = response.json()
        print_success("Article published to dev.to!")
        print_info(f"URL: {result.get('url', 'N/A')}")
        return True
    except ImportError:
        print_error("requests not installed. Install with: pip install requests")
        return False
    except Exception as e:
        print_error(f"Error publishing to dev.to: {e}")
        return False


def task_linkedin(message: str | None = None) -> bool:
    """Publish release announcement to LinkedIn."""
    print_info("Publishing to LinkedIn...")

    access_token = os.environ.get("LINKEDIN_ACCESS_TOKEN")
    if not access_token:
        print_error("LINKEDIN_ACCESS_TOKEN not found in environment variables")
        print_info("See: https://www.linkedin.com/developers/apps")
        return False

    if not message:
        message = format_release_message()

    # LinkedIn API v2
    import requests

    url = "https://api.linkedin.com/v2/ugcPosts"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "X-Restli-Protocol-Version": "2.0.0",
    }

    # Get person URN (simplified - in production, you'd want to fetch this)
    person_urn = os.environ.get("LINKEDIN_PERSON_URN", "urn:li:person:YOUR_PERSON_ID")

    data = {
        "author": person_urn,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {"text": message},
                "shareMediaCategory": "NONE",
            }
        },
        "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"},
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        print_success("Post published to LinkedIn!")
        return True
    except ImportError:
        print_error("requests not installed. Install with: pip install requests")
        return False
    except Exception as e:
        print_error(f"Error publishing to LinkedIn: {e}")
        return False


def task_mastodon(message: str | None = None) -> bool:
    """Publish release announcement to Mastodon."""
    print_info("Publishing to Mastodon...")

    instance_url = os.environ.get("MASTODON_INSTANCE_URL")
    access_token = os.environ.get("MASTODON_ACCESS_TOKEN")

    if not instance_url or not access_token:
        print_error("MASTODON_INSTANCE_URL and MASTODON_ACCESS_TOKEN required")
        print_info("Get your access token from: https://<your-instance>/settings/applications")
        return False

    if not message:
        message = format_release_message()

    try:
        from mastodon import Mastodon

        mastodon = Mastodon(access_token=access_token, api_base_url=instance_url)
        status = mastodon.toot(message)
        print_success("Toot published to Mastodon!")
        print_info(f"Status ID: {status['id']}")
        return True
    except ImportError:
        print_error("Mastodon.py not installed. Install with: pip install Mastodon.py")
        print_info("Message to post:")
        print_info(f"  {message}")
        return False
    except Exception as e:
        print_error(f"Error publishing to Mastodon: {e}")
        return False


def task_github_discussion(message: str | None = None, category: str = "Announcements") -> bool:
    """Create a GitHub Discussion for the release."""
    print_info("Creating GitHub Discussion...")

    # Check if GitHub CLI is available
    gh_result = subprocess.run(
        ["gh", "--version"],
        capture_output=True,
        text=True,
    )
    if gh_result.returncode != 0:
        print_error("GitHub CLI (gh) not found. Install from: https://cli.github.com/")
        return False

    if not message:
        message = format_release_message()

    version = get_project_version()
    title = f"Release {version}" if version else "New Release"

    # Get repository info
    repo_result = subprocess.run(
        ["gh", "repo", "view", "--json", "nameWithOwner"],
        capture_output=True,
        text=True,
        cwd=PROJECT_ROOT,
    )
    if repo_result.returncode != 0:
        print_error("Could not determine GitHub repository")
        return False

    try:
        repo_info = json.loads(repo_result.stdout)
        repo = repo_info.get("nameWithOwner")
        if not repo:
            print_error("Could not determine repository name")
            return False
    except json.JSONDecodeError:
        print_error("Could not parse repository information")
        return False

    # Create discussion using GitHub CLI
    # Note: GitHub CLI doesn't directly support creating discussions via API
    # This is a placeholder - you might need to use the GitHub API directly
    print_warning("GitHub Discussions creation via CLI is limited")
    print_info("You can create a discussion manually at:")
    print_info(f"  https://github.com/{repo}/discussions/new")
    print_info(f"\nTitle: {title}")
    print_info(f"Category: {category}")
    print_info(f"Message:\n{message}")

    return True


def task_reddit(message: str | None = None, subreddit: str | None = None) -> bool:
    """Publish release announcement to Reddit."""
    print_info("Publishing to Reddit...")

    client_id = os.environ.get("REDDIT_CLIENT_ID")
    client_secret = os.environ.get("REDDIT_CLIENT_SECRET")
    username = os.environ.get("REDDIT_USERNAME")
    password = os.environ.get("REDDIT_PASSWORD")
    user_agent = os.environ.get("REDDIT_USER_AGENT", f"{PROJECT_ROOT.name}/1.0")

    if not all([client_id, client_secret, username, password]):
        print_error("Reddit API credentials not found in environment variables")
        print_info("Required: REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USERNAME, REDDIT_PASSWORD")
        print_info("See: https://www.reddit.com/prefs/apps")
        return False

    if not subreddit:
        subreddit = os.environ.get("REDDIT_SUBREDDIT")
        if not subreddit:
            print_error("Subreddit not specified. Set REDDIT_SUBREDDIT or use --subreddit option")
            return False

    if not message:
        message = format_release_message()

    try:
        import praw

        reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            username=username,
            password=password,
            user_agent=user_agent,
        )

        subreddit_obj = reddit.subreddit(subreddit)
        version = get_project_version()
        title = f"{PROJECT_ROOT.name} {version} Released" if version else f"{PROJECT_ROOT.name} Release"

        submission = subreddit_obj.submit(title=title, selftext=message)
        print_success(f"Post submitted to r/{subreddit}!")
        print_info(f"URL: https://reddit.com{submission.permalink}")
        return True
    except ImportError:
        print_error("praw not installed. Install with: pip install praw")
        print_info("Message to post:")
        print_info(f"  Title: {title if 'title' in locals() else 'Release'}")
        print_info(f"  {message}")
        return False
    except Exception as e:
        print_error(f"Error publishing to Reddit: {e}")
        return False


def task_publish_all(message: str | None = None) -> bool:
    """Publish release announcement to all configured platforms."""
    print_separator()
    print_header("PUBLISHING TO ALL PLATFORMS")
    print_separator()

    if not message:
        message = format_release_message()

    print_info("Message to publish:")
    print_info(f"  {message}\n")

    # Map platform names to their task functions
    platforms = {
        "Twitter/X": task_twitter,
        "dev.to": task_devto,
        "LinkedIn": task_linkedin,
        "Mastodon": task_mastodon,
        "GitHub Discussion": task_github_discussion,
        "Reddit": task_reddit,
    }

    results = {}

    # Publish to each platform
    for platform_name, task_func in platforms.items():
        print("\n" + "-" * 70)
        print_info(platform_name)
        print("-" * 70)
        results[platform_name] = task_func(message)

    # Summary
    print_separator()
    print_header("PUBLISHING SUMMARY")
    print_separator()
    for platform_name, success in results.items():
        status = "✓" if success else "✗"
        print(f"{status} {platform_name}: {'Success' if success else 'Failed'}")
    print_separator()

    return all(results.values())

