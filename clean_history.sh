#!/bin/bash

# Create a new branch from main without secrets
git checkout --orphan temp_branch

# Add all files except sensitive ones
git add --all -- ':!.env' ':!.env.example'

# Commit the changes
git commit -m "Initial commit without sensitive files"

# Delete the main branch
git branch -D main

# Rename the current branch to main
git branch -m main

# Force update the repository
echo "Run 'git push -f origin main' to push these changes to GitHub" 