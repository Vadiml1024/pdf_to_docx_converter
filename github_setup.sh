#!/bin/bash
# GitHub Repository Setup Script
# Run this after creating the GitHub repository

echo "🚀 Setting up GitHub remote for PDF-to-DOCX Converter"
echo "================================================="

# Check if we're in the right directory
if [ ! -f "main.py" ]; then
    echo "❌ Error: Please run this script from the pdf_to_docx_converter directory"
    exit 1
fi

# Get GitHub username
read -p "Enter your GitHub username: " GITHUB_USERNAME

if [ -z "$GITHUB_USERNAME" ]; then
    echo "❌ Error: GitHub username is required"
    exit 1
fi

# Set up SSH remote
SSH_URL="git@github.com:${GITHUB_USERNAME}/pdf-to-docx-converter.git"

echo "🔗 Adding GitHub remote..."
git remote add origin "$SSH_URL"

# Verify remote
echo "✅ Remote URL set to: $SSH_URL"
git remote -v

# Test SSH connection
echo "🔐 Testing SSH connection to GitHub..."
ssh -T git@github.com

if [ $? -eq 1 ]; then
    echo "✅ SSH connection successful!"
    
    # Push to GitHub
    echo "📤 Pushing to GitHub..."
    
    echo "Pushing main branch..."
    git push -u origin main
    
    echo "Pushing develop branch..."
    git push -u origin develop
    
    echo "Pushing tags..."
    git push --tags
    
    echo ""
    echo "🎉 Successfully pushed to GitHub!"
    echo "Repository URL: https://github.com/${GITHUB_USERNAME}/pdf-to-docx-converter"
    
else
    echo "❌ SSH connection failed. Please check your SSH setup:"
    echo "1. Make sure you have SSH keys generated"
    echo "2. Add your public key to GitHub"
    echo "3. Run: ssh -T git@github.com"
    echo ""
    echo "See SSH_SETUP.md for detailed instructions"
fi
