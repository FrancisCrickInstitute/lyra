---
name: bioinformatic-tool-selection
description: Research and recommend the best bioinformatics tool for a specific task. Use this when you need to select appropriate tools for bioinformatics analysis based on requirements, performance, integration, and community support.
---

# Bioinformatics Tool Selection Guide

This guide provides a systematic approach for researching and selecting the best bioinformatics tool for a specific task.

## Prerequisites

- Clear understanding of the bioinformatics task requirements
- Access to web search for tool research
- Knowledge of Nextflow/nf-core ecosystem

## Table of Contents

1. [Understanding Task Requirements](#understanding-task-requirements)
2. [Research Strategy](#research-strategy)
3. [Evaluation Criteria](#evaluation-criteria)
4. [Comparison and Selection](#comparison-and-selection)
5. [Output Format](#output-format)

---

## Understanding Task Requirements

Before researching tools, clearly define:

- **Task description**: What biological/computational problem needs solving?
- **Input/output formats**: What data formats are required?
- **Algorithms needed**: Are specific algorithmic approaches required?
- **Performance constraints**: Speed, memory, scalability requirements
- **Compatibility requirements**: Existing pipeline integration, technology stack
- **Scope**: Single-sample analysis vs. batch processing

---

## Research Strategy

### 1. Initial Tool Discovery

Search systematically for tools designed for the specific task:

- Use web search for "{task} bioinformatics tool comparison"
- Check nf-core modules: https://nf-co.re/modules
- Search BioContainers/Bioconda repositories
- Review recent publications and benchmarks (last 2-3 years)

### 2. Prioritize Actively Maintained Tools

Focus on tools with:
- Recent commits/releases (within last 2 years)
- Active issue tracking and responses
- Strong community adoption (stars, forks, citations)
- Good documentation and tutorials
- Docker/Singularity container availability
- Compatible licensing (preferably open source: MIT, GPL, Apache, BSD)

### 3. Consider Integration Factors

For pipeline compatibility, prioritize:
- Existing nf-core modules
- Containerized tools (Docker/Singularity)
- CLI interfaces (vs. GUI-only tools)
- ARM architecture compatibility
- Python 3.13+ or Nextflow compatibility

### 4. Consider Python Utility Alternatives
- If a Python utility could solve the problem, research existing libraries or consider writing a custom utility
- Compare the Python solution to tool-based options in terms of integration ease, performance, and maintenance

---

## Evaluation Criteria

### Criteria Weights

Use these approximate weights when evaluating (adjust based on task specifics):

| Criterion | Weight | Description |
|-----------|--------|-------------|
| **Integration ease** | 30% | nf-core module exists, containers available, clean CLI |
| **Performance/Accuracy** | 25% | Benchmarks, published comparisons, validation |
| **Maintenance/Support** | 20% | Active development, responsive community |
| **Documentation** | 15% | Quality docs, examples, tutorials available |
| **Licensing/Compatibility** | 10% | Open source, format support, no restrictions |

### Detailed Evaluation Points

For each candidate tool, assess:

#### Performance
- Speed and scalability characteristics
- Resource requirements (RAM, CPU cores)
- Benchmark results from published comparisons
- Real-world performance testimonials

#### Accuracy
- Validation against gold standards
- Published accuracy metrics
- Known limitations or biases

#### Maintenance
- Last commit/release date
- Issue response time and resolution rate
- Active development roadmap
- Number of contributors

#### Integration
- nf-core module availability and status
- Container availability (BioContainers, Docker Hub, etc.)
- CLI interface design and ease of use
- Input/output format compatibility

#### Documentation
- Quality and completeness of official docs
- Availability of tutorials and examples
- Community guides and discussions
- API/CLI reference documentation

#### Compatibility
- Supported operating systems (Linux, macOS, ARM)
- Dependency requirements and conflicts
- License type and restrictions
- File format support

---

## Comparison and Selection

### Create a Comparison Matrix

Compare 2-4 leading tools across criteria:

```markdown
| Feature | Tool A | Tool B | Tool C |
|---------|--------|--------|--------|
| nf-core module | ✅ Available | ❌ None | 🔶 Outdated |
| Container | Docker, Singularity | Docker only | BioContainer |
| Last update | 2 months ago | 1 year ago | 2 weeks ago |
| Performance | Fast, 4GB RAM | Slow, 2GB RAM | Fast, 8GB RAM |
| Accuracy | 99.2% (benchmark) | 98.5% | 99.0% |
```

### Note Trade-offs

Document key trade-offs:
- Speed vs. accuracy
- Ease of use vs. flexibility
- Resource efficiency vs. feature completeness
- Maturity vs. cutting-edge algorithms

### Pipeline-Specific Factors

Consider pipeline-specific needs:
- Does an nf-core module already exist?
- Is it containerized?
- Will it work with ARM/Docker environments?
- Does it fit the pipeline architecture?
- Can it handle the expected data volume?

### Make the Selection

Select the best tool based on:
1. Weighted criteria scores
2. Critical requirements (must-haves)
3. Integration ease and maintenance burden
4. Long-term viability

**Practical guidance:**
- If multiple tools are equally viable, choose the one with an nf-core module
- If no clear winner exists, present top 2 options with clear trade-offs
- Favor tools that integrate easily over theoretically optimal solutions that are difficult to implement
- Flag any red flags: abandoned tools, licensing issues, known bugs

---

## Output Format

Structure your recommendation as follows:

```markdown
## Tool Selection: {Task Name}

**Recommended Tool:** {Tool Name} (v{version})
**Repository:** {GitHub/GitLab URL}
**License:** {License type}

**Justification:**
{2-3 sentence summary of why this tool is the best choice}

**Key Strengths:**
- {Specific advantage 1}
- {Specific advantage 2}
- {Specific advantage 3}

**Integration Status:**
- **nf-core module**: {Available/Needs creation} {+ link if available}
- **Container**: {Docker/Singularity available on BioContainers/Bioconda}
- **CLI interface**: {Brief description of how tool is invoked}

**Performance Notes:**
- {Speed/scalability observations}
- {Resource requirements: RAM, CPU}
- {Benchmark results if available}

**Alternatives Considered:**
1. **{Tool Name}**: {Brief reason it ranks lower}
2. **{Tool Name}**: {Brief reason it ranks lower}

**Caveats/Limitations:**
- {Known limitation 1, if any}
- {Known limitation 2, if any}

**Implementation Notes:**
{Any specific guidance for integrating this tool into pipeline}

**Sources:**
- {URL to tool repository}
- {URL to key benchmark/comparison paper}
- {URL to nf-core module if exists}
- {Other relevant sources}
```

---

## Special Considerations

### When Requirements Are Ambiguous

If the task is not clearly defined:
- List assumptions made during research
- Ask clarifying questions about requirements
- Present options for different interpretations

### When No Tools Meet All Requirements

If no single tool satisfies all needs:
- Present the best compromise option
- Document which requirements are not met
- Suggest potential workarounds or alternatives
- Consider whether multiple tools could be combined

---

## Example Workflow

1. **Understand**: Read task requirements → Identify key constraints
2. **Search**: Web search for tools → Check nf-core modules → Review BioContainers
3. **Shortlist**: Select 3-4 candidates based on initial screening
4. **Evaluate**: Score each candidate across all criteria
5. **Compare**: Create comparison matrix → Document trade-offs
6. **Compare to python solution** If a Python utility could solve the problem, compare it to a tool-based solution, considering factors like ease of integration, performance, and maintenance.
7. **Select**: Choose best option → Justify decision
8. **Document**: Format recommendation → Include sources → Note caveats
