#!/usr/bin/env python3
"""Publishing service for releases and social media announcements.

Usage:
    python publish.py <command> [args...]
    ./service.py publish <command> [args...]

Examples:
    ./service.py publish release-full
    ./service.py publish git-tag
    ./service.py publish upload-pypi
    ./service.py publish social-all
    ./service.py publish twitter
"""

from __future__ import annotations

import sys
from typing import Callable

from . import utils
from .publish import release, socialnetwork

# Import utility functions
print_error = utils.print_error
print_info = utils.print_info
print_success = utils.print_success
print_warning = utils.print_warning

# Import task functions from modules
# Release tasks
task_show_info = release.task_show_info
task_git_tag = release.task_git_tag
task_git_push_tags = release.task_git_push_tags
task_upload_testpypi = release.task_upload_testpypi
task_upload_pypi = release.task_upload_pypi
task_github_release = release.task_github_release
task_full_release = release.task_full_release

# Social network tasks
task_twitter = socialnetwork.task_twitter
task_devto = socialnetwork.task_devto
task_linkedin = socialnetwork.task_linkedin
task_mastodon = socialnetwork.task_mastodon
task_github_discussion = socialnetwork.task_github_discussion
task_reddit = socialnetwork.task_reddit
task_publish_all = socialnetwork.task_publish_all


def task_help() -> bool:
    """Display help message."""
    print_info("Publishing Commands\n")
    print_success("Release Management:")
    print("  show-info            Show project information (name, version, type)")
    print("  git-tag              Create a Git tag for current version")
    print("  git-push-tags        Push Git tags to remote")
    print("  upload-testpypi      Upload package to TestPyPI")
    print("  upload-pypi          Upload package to PyPI")
    print("  github-release       Create a GitHub release")
    print("  release-full         Full release workflow (tag, build, upload, GitHub)")
    print("")
    print_success("Social Media Publishing:")
    print("  twitter              Publish to X (Twitter)")
    print("  devto                Publish to dev.to")
    print("  linkedin             Publish to LinkedIn")
    print("  mastodon             Publish to Mastodon")
    print("  github-discussion    Create GitHub Discussion")
    print("  reddit               Publish to Reddit")
    print("  social-all           Publish to all configured platforms")
    print("")
    print_success("Usage:")
    print("  python publish.py <command> [args...]")
    print("  ./service.py publish <command> [args...]")
    print("")
    print_success("Environment Variables:")
    print("  Release:")
    print("    - PyPI credentials: ~/.pypirc or TWINE_USERNAME/TWINE_PASSWORD")
    print("  Social Media:")
    print("    - Twitter: TWITTER_BEARER_TOKEN (or API keys)")
    print("    - dev.to: DEVTO_API_KEY")
    print("    - LinkedIn: LINKEDIN_ACCESS_TOKEN, LINKEDIN_PERSON_URN")
    print("    - Mastodon: MASTODON_INSTANCE_URL, MASTODON_ACCESS_TOKEN")
    print("    - Reddit: REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USERNAME, REDDIT_PASSWORD")
    return True


# Command mapping
COMMANDS: dict[str, Callable[[], bool]] = {
    "help": task_help,
    # Release commands
    "show-info": task_show_info,
    "git-tag": task_git_tag,
    "git-push-tags": task_git_push_tags,
    "upload-testpypi": task_upload_testpypi,
    "upload-pypi": task_upload_pypi,
    "github-release": task_github_release,
    "release-full": task_full_release,
    # Social media commands
    "twitter": task_twitter,
    "devto": task_devto,
    "linkedin": task_linkedin,
    "mastodon": task_mastodon,
    "github-discussion": task_github_discussion,
    "reddit": task_reddit,
    "social-all": task_publish_all,
}


def main() -> int:
    """Main entry point."""
    if len(sys.argv) < 2:
        task_help()
        return 0

    command = sys.argv[1].lower()

    if command not in COMMANDS:
        print_error(f"Unknown command: {command}")
        print_info("Run 'python publish.py help' to see available commands")
        return 1

    try:
        success = COMMANDS[command]()
        return 0 if success else 1
    except KeyboardInterrupt:
        print_warning("\nOperation cancelled by user.")
        return 130
    except Exception as exc:
        print_error(f"Error: {exc}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

