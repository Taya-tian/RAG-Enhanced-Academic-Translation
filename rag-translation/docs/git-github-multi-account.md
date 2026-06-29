# Git and GitHub: Multiple Accounts & Identity

This manual explains how **commit identity** and **authentication** differ, why `git clone` / `git push` may still use your first GitHub account, and how to use a second account with SSH on macOS.

---

## 1. Commit author vs login account

| What | Purpose |
|------|---------|
| `user.name` / `user.email` | Author line on commits (who wrote the commit). |
| SSH keys / HTTPS tokens | Who GitHub thinks you are when you **clone**, **pull**, or **push**. |

Setting `user.name` in one repo does **not** change which account authenticates.

---

## 2. Use a different name in one repository only

Use **local** config (overrides global for this repo only):

```bash
cd /path/to/your/repo
git config user.name "Your Other Name"
git config user.email "other-email@example.com"
```

Verify:

```bash
git config --get user.name
git config --get user.email
git config --list --show-origin
```

---

## 3. Why `git clone` still looks like the “global” user

`git clone` does not read `user.name` for login. It uses:

- **HTTPS**: stored credentials (macOS Keychain) or the account in the URL.
- **SSH**: whichever key GitHub accepts first for `git@github.com`.

So cloning can still authenticate as your primary account even after you set local `user.name`.

---

## 4. Why `git push` still uses the first account

Same reason: **push uses your auth method**, not commit identity.

- **HTTPS**: cached PAT/username for `github.com` in Keychain.
- **SSH**: default `ssh -T git@github.com` identity (e.g. first key GitHub recognizes).

Typical error when URL or access is wrong:

```text
ERROR: Repository not found.
fatal: Could not read from remote repository.
```

Check remote and access:

```bash
git remote -v
```

Fix URL if the repo moved or the path is wrong:

```bash
git remote set-url origin git@github.com:<owner>/<repo>.git
# or HTTPS:
git remote set-url origin https://github.com/<owner>/<repo>.git
```

---

## 5. Quick check: which GitHub user SSH uses

```bash
ssh -T git@github.com
```

Example success message:

```text
Hi <username>! You've successfully authenticated, but GitHub does not provide shell access.
```

That `<username>` is the account your **default** SSH key is using. Pushes to `git@github.com:...` go through that account unless you change the remote (see below).

---

## 6. Use a second GitHub account with SSH (recommended)

GitHub allows only one default key per host in many setups. The usual pattern is **a separate SSH key + a Host alias** in `~/.ssh/config`.

### Step 1: Create a key for the second account

```bash
ssh-keygen -t ed25519 -C "your-second-account-email" -f ~/.ssh/id_ed25519_account2
```

### Step 2: Add `~/.ssh/config`

```sshconfig
Host github-account2
  HostName github.com
  User git
  IdentityFile ~/.ssh/id_ed25519_account2
  IdentitiesOnly yes
```

### Step 3: Add the public key to the second GitHub account

Copy `~/.ssh/id_ed25519_account2.pub` and add it under  
**GitHub → Settings → SSH and GPG keys → New SSH key**.

### Step 4: Test the alias

```bash
ssh -T git@github-account2
```

You should see: `Hi <second-username>! ...`

### Step 5: Point **this** repository’s `origin` at the alias

```bash
cd /path/to/your/repo
git remote set-url origin git@github-account2:<owner>/<repo>.git
git remote -v
git push
```

Use your real `<owner>` and `<repo>` from the GitHub URL.

---

## 7. HTTPS alternative (second account)

Use the second account in the URL so Git prompts or uses the right token:

```bash
git clone https://<second-username>@github.com/<owner>/<repo>.git
```

If macOS keeps using the wrong saved password:

- Open **Keychain Access** → search for `github.com` → remove outdated **internet password** entries for Git, **or**
- Use **GitHub CLI**: `gh auth login` and choose the correct account.

---

## 8. GitHub CLI

If you use `gh`:

```bash
gh auth status
gh auth login
```

Ensure the active login matches the account that owns or can access the repo.

---

## 9. Summary

- **Local `user.name` / `user.email`**: only commit metadata.
- **Clone / push account**: HTTPS credential store or SSH key + remote URL.
- **Second account over SSH**: new key + `Host` alias + `git remote set-url origin git@github-account2:owner/repo.git`.

If anything fails, capture `git remote -v` and whether you use HTTPS or SSH, then adjust URL or credentials accordingly.
