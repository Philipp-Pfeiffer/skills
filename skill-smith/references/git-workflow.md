# Git Workflow for Skills

Skills are typically maintained in a Git repository. This reference covers common workflows for creating, updating, and managing skills with Git.

## Creating a New Skill

```bash
# Create the skill directory
mkdir my-new-skill

# Create SKILL.md and optional resources
# ... edit files ...

# Stage and commit
git add my-new-skill/
git commit -m "Add my-new-skill for [purpose]"

# Push to remote
git push
```

## Updating an Existing Skill

```bash
# Edit the skill files
# ... make changes ...

# Review what changed
git diff my-existing-skill/

# Stage and commit
git add my-existing-skill/
git commit -m "Update my-existing-skill: [what changed]"

git push
```

## Moving or Renaming a Skill

```bash
# Git tracks renames automatically when content is similar
git mv old-skill-name/ new-skill-name/
git commit -m "Rename old-skill-name to new-skill-name"

git push
```

## Commit Message Conventions

Use clear, descriptive commit messages:

- `Add skill-name for [purpose]` — New skill
- `Update skill-name: [specific change]` — Modification
- `Fix skill-name: [bug description]` — Bugfix
- `Remove skill-name` — Deletion

## Review Checklist Before Commit

- [ ] `SKILL.md` has valid YAML frontmatter with `name` and `description`
- [ ] Skill name matches directory name
- [ ] `description` is specific and includes trigger conditions
- [ ] No extraneous files (README, CHANGELOG, etc.)
- [ ] Scripts are tested and executable
- [ ] References are linked from `SKILL.md`
