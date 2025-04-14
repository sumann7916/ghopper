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
    url = url.strip().rstrip(".git")

    if url.startswith("git@"):
        match = re.match(r"git@([\w.-]+):([\w./-]+)", url)
        if match:
            host, path = match.groups()
            # Clean up host to remove any alias (e.g., github.com-alias → github.com)
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

@click.group()
def cli():
    """ghopper — open GitHub repos and PRs fast"""
    pass

@cli.command()
@click.argument("alias", required=False)
def view(alias):
    """Open a repository or its GitHub page."""
    config = load_config()

    if not alias:
        repo_url = get_current_git_repo()
        if not repo_url:
            click.echo("Not in a Git repo or can't detect remote.")
            return
        alias = find_alias_by_repo_url(config, repo_url)
        if not alias:
            click.echo("Repo not found in config.")
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

    if not alias:
        repo_url = get_current_git_repo()
        if not repo_url:
            click.echo("Not in a Git repo or can't detect remote.")
            return
        alias = find_alias_by_repo_url(config, repo_url)
        if not alias:
            click.echo("Repo not found in config.")
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
@click.argument("alias")
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
@click.argument("alias")
@click.option("--prod", help="New production branch")
@click.option("--pre", help="New pre-production branch")
@click.option("--dev", help="New development branch")
def modify(alias, prod, pre, dev):
    """Modify the branches of an existing repo."""
    config = load_config()

    repo = config["repos"].get(alias)
    if not repo:
        click.echo(f"Alias '{alias}' not found.")
        return

    # Update branches
    if prod:
        repo["branches"]["prod"] = prod
    if pre:
        repo["branches"]["pre"] = pre
    if dev:
        repo["branches"]["dev"] = dev

    save_config(config)
    click.echo(f"✅ Updated branches for '{alias}'")


if __name__ == "__main__":
    cli()
