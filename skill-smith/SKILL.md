---
name: skill-smith
description: Guide for creating effective skills for OpenClaw agents. Use when building, updating, or reviewing agent skills — modular knowledge packages with SKILL.md, optional scripts, references, and assets. Covers OpenClaw header format, progressive disclosure, skill anatomy, naming, and git workflow.
metadata:
  openclaw:
    emoji: "🔨"
    requires:
      bins: []
---

# Skill Smith

*Based on the [Kimi CLI skill-creator](https://github.com/MoonshotAI/kimi-cli) by Moonshot AI. Adapted for OpenClaw workflows.*

This skill provides guidance for creating effective skills.

## About Skills

Skills are modular, self-contained packages that extend an agent's capabilities by providing
specialized knowledge, workflows, and tools. Think of them as "onboarding guides" for specific
domains or tasks — they transform a general-purpose agent into a specialized agent
equipped with procedural knowledge that no model can fully possess.

### What Skills Provide

1. Specialized workflows — Multi-step procedures for specific domains
2. Tool integrations — Instructions for working with specific file formats or APIs
3. Domain expertise — Company-specific knowledge, schemas, business logic
4. Bundled resources — Scripts, references, and assets for complex and repetitive tasks

## Core Principles

### Concise is Key

The context window is a public good. Skills share the context window with everything else the agent needs: system prompt, conversation history, other Skills' metadata, and the actual user request.

**Default assumption: The agent is already very smart.** Only add context it doesn't already have. Challenge each piece of information: "Does the agent really need this explanation?" and "Does this paragraph justify its token cost?"

Prefer concise examples over verbose explanations.

### Set Appropriate Degrees of Freedom

Match the level of specificity to the task's fragility and variability:

**High freedom (text-based instructions)**: Use when multiple approaches are valid, decisions depend on context, or heuristics guide the approach.

**Medium freedom (pseudocode or scripts with parameters)**: Use when a preferred pattern exists, some variation is acceptable, or configuration affects behavior.

**Low freedom (specific scripts, few parameters)**: Use when operations are fragile and error-prone, consistency is critical, or a specific sequence must be followed.

Think of the agent as exploring a path: a narrow bridge with cliffs needs specific guardrails (low freedom), while an open field allows many routes (high freedom).

## OpenClaw Header Format

Every `SKILL.md` must start with YAML frontmatter. OpenClaw extends the basic `name` and `description` fields with a `metadata.openclaw` block for dependency declaration and display hints.

```yaml
---
name: my-skill-name
description: A clear description of what this skill does and when to use it
metadata:
  openclaw:
    emoji: "🔧"
    requires:
      bins: ["python3", "node"]
      python: ["requests", "pandas"]
      node: ["axios"]
---
```

**Required fields:**
- `name` — Unique identifier, lowercase with hyphens
- `description` — Complete description of what the skill does and when to use it. This is the primary triggering mechanism.

**Optional `metadata.openclaw` fields:**
- `emoji` — Visual identifier for the skill
- `requires.bins` — List of required system binaries
- `requires.python` — List of required Python packages
- `requires.node` — List of required npm packages

See [references/openclaw-metadata.md](references/openclaw-metadata.md) for complete examples.

## Anatomy of a Skill

Every skill consists of a required `SKILL.md` file and optional bundled resources:

```
skill-name/
├── SKILL.md (required)
│   ├── YAML frontmatter metadata (required)
│   │   ├── name: (required)
│   │   ├── description: (required)
│   │   └── metadata.openclaw (optional)
│   └── Markdown instructions (required)
└── Bundled Resources (optional)
    ├── scripts/          - Executable code (Python/Bash/etc.)
    ├── references/       - Documentation intended to be loaded into context as needed
    └── assets/           - Files used in output (templates, icons, fonts, etc.)
```

#### SKILL.md (required)

Every `SKILL.md` consists of:

- **Frontmatter** (YAML): Contains `name`, `description`, and optional `metadata.openclaw`. The `description` field is critical — it determines when the skill gets triggered.
- **Body** (Markdown): Instructions and guidance for using the skill. Only loaded AFTER the skill triggers.

#### Bundled Resources (optional)

##### Scripts (`scripts/`)

Executable code for tasks that are repeatedly rewritten or need to be run directly.

- **When to include**: When code is useful for the skill's workflow
- **Example**: `scripts/rotate_pdf.py` for PDF rotation tasks
- **Note**: Scripts may be executed directly or read by the agent for context

##### References (`references/`)

Documentation intended to be loaded as needed into context.

- **When to include**: For documentation that the agent should reference while working
- **Examples**: API docs, schemas, policies, detailed workflow guides
- **Benefits**: Keeps `SKILL.md` lean, loaded only when needed
- **Best practice**: Keep references one level deep from `SKILL.md`

##### Assets (`assets/`)

Files not intended to be loaded into context, but used within the output.

- **When to include**: When the skill needs files for final output
- **Examples**: Templates, images, boilerplate code

#### What to Not Include in a Skill

A skill should only contain essential files. Do NOT create extraneous documentation:

- README.md
- INSTALLATION_GUIDE.md
- QUICK_REFERENCE.md
- CHANGELOG.md

The skill should only contain the information needed for an agent to do the job at hand.

## Progressive Disclosure Design Principle

Skills use a three-level loading system:

1. **Metadata (name + description)** — Always in context (~100 words)
2. **SKILL.md body** — When skill triggers (<500 lines optimal)
3. **Bundled resources** — As needed by the agent

**Key principle:** When a skill supports multiple variations or options, keep only the core workflow in `SKILL.md`. Move variant-specific details into separate reference files.

**Pattern: High-level guide with references**

```markdown
# PDF Processing

## Quick start
Extract text with pdfplumber:
[code example]

## Advanced features
- **Form filling**: See [FORMS.md](FORMS.md)
- **API reference**: See [REFERENCE.md](REFERENCE.md)
```

**Important guidelines:**
- **Avoid deeply nested references** — Keep references one level deep
- **Structure longer reference files** — For files >100 lines, include a table of contents

## Skill Naming

- Use lowercase letters, digits, and hyphens only
- Prefer short, verb-led phrases that describe the action
- Namespace by tool when it improves clarity (e.g., `gh-address-comments`)
- Name the skill folder exactly after the skill name

## Git Workflow

Skills are typically maintained in a Git repository. After creating or updating a skill:

1. Review changes with `git diff`
2. Stage the skill directory: `git add skill-name/`
3. Commit with a descriptive message: `git commit -m "Add skill-name for X"`
4. Push to the remote repository: `git push`

See [references/git-workflow.md](references/git-workflow.md) for detailed examples.

## Skill Creation Process

Skill creation involves these steps:

1. Understand the skill with concrete examples
2. Plan reusable skill contents (scripts, references, assets)
3. Initialize the skill (create directory and SKILL.md)
4. Edit the skill (implement resources and write SKILL.md)
5. Iterate based on real usage

Follow these steps in order, skipping only if there is a clear reason why they are not applicable.

### Step 1: Understanding the Skill with Concrete Examples

To create an effective skill, clearly understand concrete examples of how the skill will be used. Ask:

- "What functionality should this skill support?"
- "Can you give some examples of how this skill would be used?"
- "What would a user say that should trigger this skill?"

Conclude this step when there is a clear sense of the functionality.

### Step 2: Planning the Reusable Skill Contents

Analyze each example by:

1. Considering how to execute on the example from scratch
2. Identifying what scripts, references, and assets would be helpful

Example: A `pdf-editor` skill might benefit from `scripts/rotate_pdf.py`.

Example: A `frontend-builder` skill might benefit from `assets/hello-world/` templates.

### Step 3: Initializing the Skill

Create a new skill directory with a required `SKILL.md` file and any optional resource directories. Create only directories you intend to populate.

### Step 4: Edit the Skill

When editing, remember the skill is being created for another agent to use. Include information that would be beneficial and non-obvious.

**Writing Guidelines:** Always use imperative/infinitive form.

**Frontmatter:**
- `name`: The skill name
- `description`: Primary triggering mechanism. Include what the skill does AND when to use it.

**Body:** Write instructions for using the skill and its bundled resources.

### Step 5: Iterate

After using the skill on real tasks:

1. Notice struggles or inefficiencies
2. Identify how SKILL.md or bundled resources should be updated
3. Implement changes and test again
