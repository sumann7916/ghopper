# 🐙 ghopper Cheatsheet

> ⚡ CLI tool to manage and open GitHub repositories and PRs fast using aliases

---

## 🔧 Setup

**Create config file location:**
```bash
~/.config/ghopper/config.json
```

**Config Structure:**
```json
{
  "repos": {
    "my-alias": {
      "url": "https://github.com/username/repo",
      "branches": {
        "prod": "main",
        "pre": "staging",
        "dev": "dev"
      }
    }
  }
}
```

---

## 📌 Commands

### ➕ Add a repo to config
```bash
ghopper add <alias> [--url <repo-url>] [--prod <branch>] [--pre <branch>] [--dev <branch>]
```

**Examples:**
```bash
ghopper add ghop --prod main --dev dev
ghopper add myapp --url https://github.com/user/myapp.git
```

If `--url` is omitted, the current Git repo remote is used.

---

### 🔍 View the repo in browser
```bash
ghopper view [alias]
```

If no alias is provided, uses the current repo (from `git remote`) and looks it up in config.

---

### 🔀 Open a PR compare page
```bash
ghopper pr [alias] <branch-key> [--from <current-branch>]
```

- `branch-key` should be one of: `prod`, `pre`, or `dev`
- If alias is omitted, it infers from current Git repo
- If `--from` is omitted, uses the current branch name

**Examples:**
```bash
ghopper pr prod
ghopper pr ghop dev --from fix/bug
```

---

### 📜 List all saved repos
```bash
ghopper list
```

Shows aliases, repo URLs, and mapped branches.

---

### ❌ Remove a repo from config
```bash
ghopper remove <alias>
```

**Example:**
```bash
ghopper remove ghop
```

---

### ✏️ Modify branch names of a saved alias
```bash
ghopper modify <alias> [--prod <branch>] [--pre <branch>] [--dev <branch>]
```

**Example:**
```bash
ghopper modify ghop --prod main --dev develop
```

---

## 🧠 Tips

- Aliases save typing and speed up common GitHub workflows.
- You can manage multiple remotes or work/personal GitHub accounts by mapping repo URLs accordingly.
- `ghopper pr` can save you several clicks when creating PRs.

---

## 🗂 Example Config Snippet
```json
{
  "repos": {
    "ghop": {
      "url": "https://github.com/sumann7916/ghopper",
      "branches": {
        "prod": "main",
        "dev": "dev"
      }
    }
  }
}
```

---

