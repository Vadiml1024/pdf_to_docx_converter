# GitHub SSH Setup Guide

## 🔐 Setting Up SSH Authentication for GitHub

### Step 1: Check for Existing SSH Keys
```bash
ls -la ~/.ssh
```

Look for files named:
- `id_rsa` and `id_rsa.pub` (RSA)
- `id_ed25519` and `id_ed25519.pub` (Ed25519 - recommended)

### Step 2: Generate New SSH Key (if needed)
If you don't have SSH keys or want to create new ones:

```bash
# Generate Ed25519 key (recommended)
ssh-keygen -t ed25519 -C "your-email@example.com"

# OR generate RSA key (if Ed25519 is not supported)
ssh-keygen -t rsa -b 4096 -C "your-email@example.com"
```

When prompted:
- **File location**: Press Enter for default (`~/.ssh/id_ed25519`)
- **Passphrase**: Enter a secure passphrase (optional but recommended)

### Step 3: Add SSH Key to SSH Agent
```bash
# Start the ssh-agent
eval "$(ssh-agent -s)"

# Add your SSH private key to the ssh-agent
ssh-add ~/.ssh/id_ed25519

# OR for RSA key
ssh-add ~/.ssh/id_rsa
```

### Step 4: Copy Public Key to Clipboard
```bash
# For Ed25519 key
cat ~/.ssh/id_ed25519.pub | pbcopy

# OR for RSA key  
cat ~/.ssh/id_rsa.pub | pbcopy

# If pbcopy doesn't work, just display the key
cat ~/.ssh/id_ed25519.pub
```

### Step 5: Add SSH Key to GitHub
1. Go to GitHub.com and sign in
2. Click your profile picture → **Settings**
3. In the sidebar, click **SSH and GPG keys**
4. Click **New SSH key**
5. Add a descriptive **Title** (e.g., "MacBook Pro")
6. **Paste** your public key into the "Key" field
7. Click **Add SSH key**
8. Confirm with your GitHub password if prompted

### Step 6: Test SSH Connection
```bash
ssh -T git@github.com
```

You should see a message like:
```
Hi username! You've successfully authenticated, but GitHub does not provide shell access.
```

### Step 7: Configure Git Repository for SSH

```bash
cd /Users/vadim/work/pdf_to_docx_converter

# Add SSH remote (replace 'yourusername' with your GitHub username)
git remote add origin git@github.com:yourusername/pdf-to-docx-converter.git

# If you already added HTTPS remote, change it to SSH
git remote set-url origin git@github.com:yourusername/pdf-to-docx-converter.git

# Verify the remote URL
git remote -v
```

### Step 8: Push to GitHub
```bash
# Push main branch
git push -u origin main

# Push develop branch  
git push -u origin develop

# Push tags
git push --tags
```

## 🔧 Troubleshooting

### Permission Denied (publickey)
If you get this error:
```
Permission denied (publickey).
```

**Solutions:**
1. Make sure your SSH key is added to ssh-agent:
   ```bash
   ssh-add -l
   ssh-add ~/.ssh/id_ed25519
   ```

2. Check if your SSH key is correctly added to GitHub

3. Test SSH connection again:
   ```bash
   ssh -T git@github.com
   ```

### SSH Key Passphrase Issues
If you set a passphrase and don't want to enter it every time:

**macOS:**
```bash
ssh-add --apple-use-keychain ~/.ssh/id_ed25519
```

Add to `~/.ssh/config`:
```
Host *
  AddKeysToAgent yes
  UseKeychain yes
  IdentityFile ~/.ssh/id_ed25519
```

**Linux:**
```bash
ssh-add ~/.ssh/id_ed25519
```

### Multiple GitHub Accounts
If you have multiple GitHub accounts, add to `~/.ssh/config`:
```
# Work account
Host github-work
  HostName github.com
  User git
  IdentityFile ~/.ssh/id_ed25519_work

# Personal account  
Host github-personal
  HostName github.com
  User git
  IdentityFile ~/.ssh/id_ed25519_personal
```

Then use:
```bash
git remote add origin git@github-work:company/repo.git
```

## ✅ Verification Checklist

- [ ] SSH key generated
- [ ] SSH key added to ssh-agent
- [ ] Public key copied
- [ ] SSH key added to GitHub account
- [ ] SSH connection tested successfully
- [ ] Git remote configured for SSH
- [ ] Repository pushed successfully

## 🎉 You're All Set!

Once SSH is configured, you can:
- Push and pull without entering credentials
- Use secure key-based authentication
- Work with private repositories seamlessly

Your repository is now ready for secure SSH-based Git operations!
