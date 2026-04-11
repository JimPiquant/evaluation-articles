# Copilot Instructions

## Repository purpose

- This repository is for writing a series of articles about AI evaluations, including guidance, best practices, tooling, and related workflows.
- Optimize for high-quality written content and reusable guidance rather than assuming this is an application codebase.

## Build, test, and lint commands

- No build, test, or lint commands are defined yet.
- There is currently no single-test or per-file validation command; check the repository again before assuming a tooling workflow has been added.

## High-level architecture

- The main deliverables are articles, not services or libraries.
- Each article is a single Markdown file. Its plan lives in a separate companion file (e.g. `my-article.plan.md` alongside `my-article.md`).
- Articles cover related topics for different audiences, so terminology, recommendations, and framing around AI evaluations must stay consistent across the full set.
- References are part of the content architecture: guidance and best-practice claims should remain traceable to the sources used while drafting. Include URLs when referencing external material.

## Audience and tone

- Default audience: software developers who may or may not be new to using evaluations.
- Some articles target software architects or IT leaders — these should avoid code samples and focus on strategic guidance.
- Tone: practitioner-to-practitioner. Write as a peer sharing practical experience, not as a textbook or marketing copy.

## Key conventions

- Every article must start with a plan file (`<article-name>.plan.md`) that includes:
  - purpose
  - audience (specify where it differs from the default)
  - outline (structure)
  - references
- Do not draft or substantially revise an article before creating or reviewing its plan file.
- When editing an existing article, align changes to its stated audience and outline instead of rewriting the structure ad hoc.
- More technical articles aimed at developers should include concrete code examples. Articles targeting IT leadership should not contain code samples.
- Prefer concrete, source-backed guidance over generic commentary about AI.
- If the repository later adds article templates, frontmatter, or validation tooling, follow those exact patterns and update this file with the concrete commands.
