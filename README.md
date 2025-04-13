# 🦗 ghopper

**ghopper** is a lightweight CLI tool to quickly open GitHub repositories and generate PR compare links directly from your terminal.

---

## ✨ Features

- 🔗 Open GitHub repo pages by alias
- 🔀 Generate PR compare links (`base...head`)
- ➕ Add and manage multiple repos with branch mappings
- 🧼 Stores config in `~/.config/ghopper/config.json`

---

## 📦 Installation

### Option 1: Install for local development

```bash
pip install -e .
```

### Option 2: Global install using pipx

```bash
pipx install .
```

> ⚠️ Make sure `click` is listed in your `install_requires` in `setup.py`.

---

## 🚀 Usage

```bash
ghopper [COMMAND] [ARGS...]
```

---

### 🔍 Open a GitHub repo

```bash
ghopper view myrepo
```

Opens the GitHub page for the `myrepo` repo in your browser.

---

### 🔀 Open a PR compare view

```bash
ghopper pr myrepo dev
```

Compares your current branch with the configured `dev` branch for `myrepo`.

---

### ➕ Add a repo

```bash
ghopper add myrepo --url https://github.com/myorg/myrepo --prod main --dev dev --pre staging
```

Adds a new repo with branch mappings.

---

### 📋 List all repos

```bash
ghopper list
```

Shows all aliases and their mapped URLs & branches.

---

### ❌ Remove a repo

```bash
ghopper remove myrepo
```

Removes the `myrepo` alias from your config.

---

## 🗂 Config Structure

The config is stored at:

```
~/.config/ghopper/config.json
```

Example:

```json
{
  "repos": {
    "myrepo": {
      "url": "https://github.com/myorg/myrepo",
      "branches": {
        "prod": "main",
        "dev": "dev",
        "pre": "staging"
      }
    }
  }
}
```
Video: 


https://github.com/user-attachments/assets/6bf8739b-396e-49a8-83e7-b80bf49816bf



---

## 🛠 Requirements

- Python 3.6+
- [Click](https://palletsprojects.com/p/click/)

---

## 💬 Contributing

Pull requests are welcome! Feel free to open issues or suggestions.

---

## 📄 License

MIT
