#!/usr/bin/env python3
import click
import subprocess
import webbrowser
import json
import os
import re
from urllib.parse import urlparse
from pathlib import Path

# Config path: ~/.config/ghopper/config.json
CONFIG_DIR = Path(os.path.expanduser("~/.config/ghopper"))
CONFIG_PATH = CONFIG_DIR / "config.json"

def load_config():
    """Load the configuration data from the JSON file."""
    try:
        if CONFIG_PATH.exists():
            with open(CONFIG_PATH) as f:
                return json.load(f)
    except Exception as e:
        click.echo(f"Error loading config: {e}")
    return {"repos": {}}

def save_config(data):
    """Save configuration to the JSON file."""
    try:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        with open(CONFIG_PATH, 'w') as f:
            json.dump(data, f, indent=4)
        click.echo(f"✅ Config saved at {CONFIG_PATH}")
    except Exception as e:
        click.echo(f"Error saving config: {e}")

def get_current_git_repo():
    """Get current git repo remote URL."""
    try:
        remote_url = subprocess.check_output(
            ["git", "config", "--get", "remote.origin.url"],
            text=True
        ).strip()
        return remote_url if remote_url else None
    except subprocess.CalledProcessError:
        return None

def normalize_repo_url(url):
    """Normalize GitHub URLs to a comparable form."""
    url = url.strip()
    if url.endswith(".git"):
        url = url[:-4]

    if url.startswith("git@"):
        match = re.match(r"git@([\w.-]+):([\w./-]+)", url)
        if match:
            host, path = match.groups()
            base_host = host.split("-")[0]
            return f"{base_host}/{path}".lower()

    elif url.startswith("http"):
        parsed = urlparse(url)
        base_host = parsed.netloc.split(":")[0].split("-")[0]
        return f"{base_host}{parsed.path}".strip("/").lower()

    return url.lower()

def find_alias_by_repo_url(config, repo_url):
    """Find the alias for a given repo URL by normalized comparison."""
    normalized = normalize_repo_url(repo_url)
    for alias, info in config["repos"].items():
        if normalize_repo_url(info["url"]) == normalized:
            return alias
    return None

def resolve_alias_from_context(config, alias=None):
    """Resolve alias either from the argument or current Git repo context."""
    if alias:
        return alias
    repo_url = get_current_git_repo()
    if not repo_url:
        click.echo("Not in a Git repo or can't detect remote.")
        return None
    alias = find_alias_by_repo_url(config, repo_url)
    if not alias:
        click.echo("Repo not found in config.")
        return None
    return alias

@click.group()
def cli():
    """ghopper — open GitHub repos and PRs fast"""
    pass

@cli.command()
@click.argument("alias", required=False)
def view(alias):
    """Open a repository or its GitHub page."""
    config = load_config()
    alias = resolve_alias_from_context(config, alias)
    if not alias:
        return

    repo = config["repos"].get(alias)
    if repo:
        webbrowser.open(repo["url"])
        click.echo(f"🌐 Opening {repo['url']}")
    else:
        click.echo(f"Alias '{alias}' not found.")

@cli.command()
@click.argument("args", nargs=-1)
@click.option("--from", "from_branch", default=None, help="Branch to compare from")
def pr(args, from_branch):
    """Open a GitHub PR compare view."""
    config = load_config()

    if len(args) == 1:
        alias = None
        target = args[0]
    elif len(args) == 2:
        alias, target = args
    else:
        click.echo("Usage: pr [alias] <target>")
        return

    alias = resolve_alias_from_context(config, alias)
    if not alias:
        return

    repo = config["repos"].get(alias)
    if not repo:
        click.echo(f"Alias '{alias}' not found.")
        return

    to_branch = repo["branches"].get(target)
    if not to_branch:
        click.echo(f"Branch key '{target}' not found in alias '{alias}'")
        return

    if not from_branch:
        try:
            from_branch = subprocess.check_output(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"], text=True
            ).strip()
        except subprocess.CalledProcessError:
            click.echo("Could not determine current branch.")
            return

    url = f"{repo['url']}/compare/{to_branch}...{from_branch}"
    webbrowser.open(url)
    click.echo(f"🔀 PR Compare: {url}")

@cli.command()
@click.argument("alias", required=False)
@click.option("--url", help="GitHub repository URL")
@click.option("--prod", help="Production branch")
@click.option("--pre", help="Pre-production branch")
@click.option("--dev", help="Development branch")
def add(alias, url, prod, pre, dev):
    """Add a repository to config."""
    config = load_config()

    if not url:
        url = get_current_git_repo()
    if not url:
        click.echo("No URL provided and not in a Git repo.")
        return

    normalized_url = normalize_repo_url(url)

    if not alias:
        alias = Path(normalized_url).name.replace(".git", "")

    branches = {k: v for k, v in {"prod": prod, "pre": pre, "dev": dev}.items() if v}
    config["repos"][alias] = {
        "url": f"https://{normalized_url}",
        "branches": branches
    }

    save_config(config)
    click.echo(f"✅ Added repo '{alias}' → https://{normalized_url}")

@cli.command()
def list():
    """List all configured repos."""
    config = load_config()
    repos = config.get("repos", {})
    if not repos:
        click.echo("No repos added yet.")
        return

    for alias, info in repos.items():
        click.echo(f"{alias} → {info['url']}")
        for key, branch in info["branches"].items():
            click.echo(f"  [{key}] → {branch}")

@cli.command()
@click.argument("alias")
def remove(alias):
    """Remove a repo from the config."""
    config = load_config()
    if alias in config["repos"]:
        del config["repos"][alias]
        save_config(config)
        click.echo(f"❌ Removed '{alias}'")
    else:
        click.echo(f"Alias '{alias}' not found.")

@cli.command()
@click.argument("alias", required=False)
@click.option("--prod", help="New production branch")
@click.option("--pre", help="New pre-production branch")
@click.option("--dev", help="New development branch")
def modify(alias, prod, pre, dev):
    """Modify the branches of an existing repo."""
    config = load_config()
    alias = resolve_alias_from_context(config, alias)
    if not alias:
        return

    repo = config["repos"].get(alias)
    if not repo:
        click.echo(f"Alias '{alias}' not found.")
        return

    if prod:
        repo["branches"]["prod"] = prod
    if pre:
        repo["branches"]["pre"] = pre
    if dev:
        repo["branches"]["dev"] = dev

    save_config(config)
    click.echo(f"✅ Updated branches for '{alias}'")

@cli.command()
@click.argument("branch_key", type=click.Choice(["prod", "pre", "dev"]))
@click.argument("alias", required=False)
def checkout(branch_key, alias):
    """Quickly checkout to a prod/pre/dev branch using alias."""
    config = load_config()
    alias = resolve_alias_from_context(config, alias)
    if not alias:
        return

    repo = config["repos"].get(alias)
    if not repo:
        click.echo(f"Alias '{alias}' not found.")
        return

    branch_name = repo["branches"].get(branch_key)
    if not branch_name:
        click.echo(f"No '{branch_key}' branch configured for alias '{alias}'")
        return

    try:
        subprocess.run(["git", "checkout", branch_name], check=True)
        click.echo(f"🚀 Switched to {branch_key} branch: {branch_name}")
    except subprocess.CalledProcessError:
        click.echo(f"❌ Failed to checkout branch '{branch_name}'")
@cli.command("commit")
@click.option('-m', '--message', required=True, help="Commit message")
def commit(message):
    """Commit to the current branch, then cherry-pick to the corresponding dev and pre branches."""

    # Perform the git commit
    try:
        subprocess.check_call(["git", "commit", "-m", message])
        click.echo(f"✅ Committed changes with message: '{message}'")
    except subprocess.CalledProcessError:
        click.echo("❌ Commit failed. Please check your changes and try again.")
        return

    # Get the latest commit hash
    last_commit_hash = subprocess.check_output(
        ["git", "log", "-n", "1", "--pretty=format:%H"], text=True
    ).strip()

    # Get the current branch name (e.g., TICKET-12345)
    current_branch = subprocess.check_output(
        ["git", "symbolic-ref", "--short", "HEAD"], text=True
    ).strip()

    # Generate the target branches by appending -dev and -pre-merge to the current branch name
    dev_branch = f"{current_branch}-dev"
    pre_branch = f"{current_branch}-pre-merge"

    # Cherry-pick to the dev and pre branches
    target_branches = [dev_branch, pre_branch]

    for target in target_branches:
        try:
            click.echo(f"Cherry-picking commit {last_commit_hash} into {target} branch...")

            # Try to checkout the target branch
            try:
                subprocess.check_call(["git", "checkout", target])
            except subprocess.CalledProcessError:
                click.echo(f"❌ {target} branch does not exist. Aborting the operation.")
                return  # Abort if the branch doesn't exist

            subprocess.check_call(["git", "cherry-pick", last_commit_hash])

            # Check if a conflict happened
            status = subprocess.check_output(["git", "status"], text=True)
            if "both modified" in status:
                click.echo("⚠️ Conflict detected. Please resolve conflicts manually.")

                # Wait for the user to input how to resolve the conflict
                resolve_choice = click.prompt(
                    "Do you want to resolve conflicts automatically using 'theirs' strategy? (y/n)",
                    type=str
                ).lower()

                if resolve_choice == 'y':
                    click.echo("🔧 Resolving conflicts automatically using 'theirs' strategy.")
                    # Resolve conflicts using 'git checkout --theirs'
                    subprocess.check_call(["git", "checkout", "--theirs", "."])
                    subprocess.check_call(["git", "add", "."])

                    # Continue the merge and push
                    subprocess.check_call(["git", "commit", "--no-edit"])
                    subprocess.check_call(["git", "push", "origin", target])

                    click.echo(f"✅ Conflict resolved and changes pushed to {target}.")
                    continue

                else:
                    click.echo("❌ Aborted. Please resolve conflicts manually and push changes.")
                    return

            subprocess.check_call(["git", "push", "origin", target])
            click.echo(f"✅ Successfully cherry-picked to {target} and pushed.")
        except subprocess.CalledProcessError:
            click.echo(f"❌ Failed to cherry-pick to {target}.")
            return

    # Checkout back to the original feature branch
    subprocess.check_call(["git", "checkout", current_branch])
    click.echo(f"✅ Cherry-pick complete. Commit {last_commit_hash} added to {', '.join(target_branches)}.")

if __name__ == "__main__":
    cli()
