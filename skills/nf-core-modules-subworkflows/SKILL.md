---
name: nf-core-modules-subworkflows
description: Guide for interacting with nf-core modules and subworkflows. Use this when you need to discover, view, install, or update nf-core modules/subworkflows in your pipeline.
---


# Working with nf-core Modules and Subworkflows

This guide covers how to discover, view, install, and update nf-core modules and subworkflows in your pipeline.

## Prerequisites

nf-core is installed via pyproject.toml.

## Table of Contents

1. [Discovering Modules and Subworkflows](#discovering-modules-and-subworkflows)
2. [Getting Information](#getting-information)
3. [Viewing Source Code](#viewing-source-code)
4. [Installing](#installing)
5. [Updating](#updating)
6. [Version Management](#version-management)

---

**CRITICAL:** use `source .venv/bin/activate` to activate the virtual environment before running nf-core commands, to ensure you are using the correct version of nf-core and its dependencies.

## Discovering Modules and Subworkflows

### List All Available Modules

To see all modules available in the nf-core repository:

```bash
# List all remote modules
nf-core modules list remote

# Search for specific module by keyword (e.g., "fastq")
nf-core modules list remote fastq
```

Always try to search for a keyword as the raw list of modules can be overwhelming. The search will match both module names and descriptions.

### List All Available Subworkflows

To see all subworkflows available in the nf-core repository:

```bash
# List all remote subworkflows
nf-core subworkflows list remote

# Search for specific subworkflow by keyword (e.g., "bam")
nf-core subworkflows list remote bam
```

### List Installed Modules/Subworkflows

To see what's already installed in your pipeline:

```bash
# List locally installed modules
nf-core modules list local

# List locally installed subworkflows
nf-core subworkflows list local

# Specify a different pipeline directory
nf-core modules list local --dir /path/to/pipeline
```

---

## Getting Information

### Module Information

Get detailed information about a specific module:

```bash
# View module documentation and metadata
nf-core modules info <module_name>

# Examples:
nf-core modules info fastqc
nf-core modules info samtools/sort
```

This displays:
- Module description
- Input/output channels
- Parameters
- Dependencies
- Tool versions

### Subworkflow Information

Get detailed information about a specific subworkflow:

```bash
# View subworkflow documentation
nf-core subworkflows info <subworkflow_name>

# Example:
nf-core subworkflows info bam_rseqc
```

---

## Viewing Source Code

### Browse on GitHub

There are several ways to view the actual source code:

#### 1. Direct GitHub Links

**Modules:**
- Main repository: https://github.com/nf-core/modules
- Browse modules: https://github.com/nf-core/modules/tree/master/modules/nf-core
- Specific module: `https://github.com/nf-core/modules/tree/master/modules/nf-core/<module_name>`

**Subworkflows:**
- Browse subworkflows: https://github.com/nf-core/modules/tree/master/subworkflows/nf-core
- Specific subworkflow: `https://github.com/nf-core/modules/tree/master/subworkflows/nf-core/<subworkflow_name>`

#### 2. nf-core Website

Visit https://nf-co.re/modules to:
- Browse all modules with search functionality
- View documentation and examples
- See usage statistics
- Access GitHub links

#### 3. After Installation

Once installed, modules and subworkflows are available locally:

```bash
# Modules are installed to:
./modules/nf-core/<module_name>/

# Subworkflows are installed to:
./subworkflows/nf-core/<subworkflow_name>/
```

View them with your editor or terminal:
```bash
# View a module's main script
cat modules/nf-core/fastqc/main.nf

# View a subworkflow
cat subworkflows/nf-core/bam_rseqc/main.nf
```

---

## Installing

### Install a Module

```bash
# Interactive selection
nf-core modules install

# Install specific module directly
nf-core modules install <module_name>

# Examples:
nf-core modules install fastqc
nf-core modules install samtools/sort

# Install from a different directory
nf-core modules install fastqc --dir /path/to/pipeline
```

**Installation Options:**

- `--force`: Overwrite previously installed version
- `--prompt`: Interactively select the module version
- `--sha <commit_sha>`: Install from a specific commit

```bash
# Install specific version by SHA
nf-core modules install fastqc --sha abc123def456

# Force reinstall
nf-core modules install fastqc --force
```

### Install a Subworkflow

```bash
# Interactive selection
nf-core subworkflows install

# Install specific subworkflow directly
nf-core subworkflows install <subworkflow_name>

# Example:
nf-core subworkflows install bam_rseqc

# Install from a different directory
nf-core subworkflows install bam_rseqc --dir /path/to/pipeline
```

**Installation Options:**

- `--dir`: Specify pipeline directory (default: current directory)
- `--force`: Overwrite previously installed version
- `--prompt`: Interactively select version
- `--sha <commit_sha>`: Install from specific commit

---

## Updating

### Update Modules

```bash
# Interactive update (select which module to update)
nf-core modules update

# Update specific module
nf-core modules update <module_name>

# Examples:
nf-core modules update fastqc
nf-core modules update samtools/sort

# Update all modules at once
nf-core modules update --all --no-preview
```

**Update Options:**

- `--all`: Update all modules in the pipeline
- `--force`: Reinstall even if up to date
- `--prompt`: Select version interactively
- `--sha <commit_sha>`: Update to specific commit
- `--preview` / `--no-preview`: Show/hide diff before updating
- `--save-diff <filename>`: Save diffs to file for review

```bash
# Update with preview of changes
nf-core modules update fastqc --preview

# Update all modules without preview
nf-core modules update --all --no-preview

# Save diffs for manual review
nf-core modules update fastqc --save-diff fastqc.diff
git apply fastqc.diff  # Apply later if desired
```

### Update Subworkflows

```bash
# Interactive update
nf-core subworkflows update

# Update specific subworkflow
nf-core subworkflows update <subworkflow_name>

# Example:
nf-core subworkflows update bam_rseqc

# Update all subworkflows at once
nf-core subworkflows update --all --no-preview
```

**Update Options:**

- `--dir`: Specify pipeline directory
- `--all`: Update all subworkflows
- `--force`: Reinstall even if up to date
- `--prompt`: Select version interactively
- `--sha <commit_sha>`: Update to specific commit
- `--preview` / `--no-preview`: Show/hide diff before updating
- `--save-diff <filename>`: Save diffs to file
- `--update-deps`: Automatically update all dependencies

```bash
# Update with dependency check
nf-core subworkflows update bam_rseqc --update-deps

# Preview changes before updating
nf-core subworkflows update bam_rseqc --preview
```

---

## Quick Reference

| Task | Modules Command | Subworkflows Command |
|------|----------------|---------------------|
| List remote | `nf-core modules list remote` | `nf-core subworkflows list remote` |
| List local | `nf-core modules list local` | `nf-core subworkflows list local` |
| Get info | `nf-core modules info <name>` | `nf-core subworkflows info <name>` |
| Install | `nf-core modules install <name>` | `nf-core subworkflows install <name>` |
| Update | `nf-core modules update <name>` | `nf-core subworkflows update <name>` |
| Update all | `nf-core modules update --all` | `nf-core subworkflows update --all` |

---

## Additional Resources

- **nf-core/tools Documentation**: https://nf-co.re/docs/nf-core-tools
- **nf-core/modules Repository**: https://github.com/nf-core/modules
- **Module Browser**: https://nf-co.re/modules
- **nf-core Website**: https://nf-co.re
- **Community Chat**: https://nf-co.re/join/slack

---

## Common Workflows

### Workflow 1: Adding a New Module

```bash
# 1. Search for the module
nf-core modules list remote | grep samtools

# 2. Get information about it
nf-core modules info samtools/sort

# 3. View code on GitHub (in browser)
# Navigate to: https://github.com/nf-core/modules/tree/master/modules/nf-core/samtools/sort

# 4. Install the module
nf-core modules install samtools/sort

# 5. Include in your workflow (edit main.nf or relevant .nf file)
# include { SAMTOOLS_SORT } from './modules/nf-core/samtools/sort/main'
```

---

## Tips and Best Practices

1. **Always check module info before installing** to understand inputs/outputs
2. **Use `--preview` flag** when updating to review changes
3. **Pin versions in `.nf-core.yml`** for production pipelines
4. **Update regularly** for bug fixes and improvements (in development)
5. **Check the changelog** on GitHub when updating modules
6. **Test after updates** using your pipeline test suite
7. **Use semantic versioning** where possible for reproducibility

---

*Last updated: February 2026*
*For the most current information, visit https://nf-co.re/docs/nf-core-tools*
