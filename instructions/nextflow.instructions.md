---
applyTo: "**/*.nf, **/*.{config,groovy}"
---

# Nextflow Development Instructions for sequencing-demux

This document provides coding standards and patterns for developing the sequencing-demux Nextflow pipeline.

## Table of Contents

1. [Repository Structure](#repository-structure)
2. [General Conventions](#general-conventions)
3. [Module Development](#module-development)
4. [Subworkflow Development](#subworkflow-development)
5. [Workflow Development](#workflow-development)
6. [Configuration System](#configuration-system)
7. [Testing with nf-test](#testing-with-nf-test)
8. [Channel Patterns](#channel-patterns)
9. [Code Style](#code-style)
10. [Best Practices](#best-practices)

---

## Repository Structure

```
sequencing-demux/
├── main.nf                   # Main pipeline workflow entry point
├── nextflow.config           # Main configuration file
├── nf-test.config            # nf-test framework configuration
├── conf/                     # Configuration files
│   ├── base.config           # Base process resource labels
│   ├── modules.config        # Process-specific configurations
│   ├── arm.config            # ARM architecture compatibility
│   ├── nemo.config           # Nemo HPC cluster configuration
│   ├── genomics.config       # Genomics HPC cluster configuration
│   ├── test_ont*.config      # ONT test profiles
│   └── test_illumina.config  # Illumina test profile
├── modules/                  # Process modules
│   ├── local/                # Custom modules for this pipeline
│   │   └── tool_name/
│   │       └── main.nf
│   └── nf-core/              # nf-core standardized modules
│       └── tool/
│           └── main.nf
├── subworkflows/             # Reusable workflow components
│   └── local/                # Custom subworkflows
├── lib/core/                 # Python support libraries
├── tests/                    # nf-test files and test data
│   ├── config/               # Test-specific configurations
│   └── data/                 # Test datasets
│       ├── runs/             # ONT test run data
│       ├── illumina_runs/    # Illumina test run data
│       └── bam/              # Test BAM files
├── assets/                   # Pipeline assets and schemas
└── containers/               # Custom container definitions
    ├── bcl_convert/          # BCL Convert container
    ├── dorado/               # Dorado basecaller container
    └── pod5/                 # POD5 tools container
```

---

## General Conventions

- Use Nextflow DSL2 syntax and features
- Follow nf-core module and subworkflow development standards
- Use consistent naming conventions for processes, channels, and parameters
- Document complex logic with comments
- Use the new workflow output system instead of `publishDir`
- Write nf-tests ONLY for the main workflow and critical components, not for individual modules or subworkflows
- Use nf-core modules and subworkflows where possible, customize with `task.ext.args` and `task.ext.prefix`
- Track tool versions in every process and subworkflow
- Use configuration profiles for environment-specific settings (e.g., Docker, ARM)
- Test with the `arm` profile to ensure compatibility with ARM architecture

### Naming Standards

- **Processes**: `TOOL_NAME` (uppercase, underscore for compound names)
- **Workflows**: `WORKFLOW_NAME` (uppercase, descriptive)
- **Channels**: `ch_descriptive_name` (lowercase, prefix with `ch_`)
- **Parameters**: `snake_case` (lowercase, underscores)
- **Meta fields**: `meta.id`, `meta.single_end`, etc.

### Container Standards

- Use containers from `quay.io/biocontainers` when available
- Specify exact version tags (avoid `latest`)
- Configure registry in [nextflow.config](nextflow.config): `docker.registry = "quay.io"`

### Include Statements

```groovy
// Consistent include format with relative paths
include { PROCESS_NAME                     } from '../modules/local/tool/main'
include { PROCESS_NAME as ALIAS            } from '../modules/nf-core/tool/main'
include { SUBWORKFLOW_NAME                 } from '../subworkflows/local/example/main'
```

## Module Development

Modules encapsulate individual tool processes. Each module is self-contained and reusable.

### Module Structure

Place modules in the appropriate directory:
- **Custom modules**: `modules/local/tool_name/main.nf`
- **nf-core modules**: `modules/nf-core/tool/subtool/main.nf`

***CRITICAL:*** Do not edit nf-core modules directly unless necessary. Always pause to verify with user if you believe a change to an nf-core module is required.

### Module Definition Pattern

```groovy
process TOOL_NAME {
    label 'process_medium'  // Use labels from conf/base.config
    tag "$meta.id"

    container "quay.io/biocontainers/tool:version"

    input:
    tuple val(meta), path(input_file)
    path reference

    output:
    tuple val(meta), path('*.output'), emit: result
    path "versions.yml",               emit: versions

    when:
    task.ext.when == null || task.ext.when

    script:
    def args = task.ext.args ?: ''
    def prefix = task.ext.prefix ?: "${meta.id}"
    """
    tool_command \\
        $args \\
        --input $input_file \\
        --reference $reference \\
        --output ${prefix}.output
    
    cat <<-END_VERSIONS > versions.yml
    "${task.process}":
        tool: \$(tool --version | head -n1 | awk '{print \$2}')
    END_VERSIONS
    """
}
```

### Key Patterns

1. **Always tag processes**: `tag "$meta.id"` for traceability
2. **Use task.ext.args**: Allows flexible argument configuration
3. **Track versions**: Include `versions.yml` output in all processes
4. **Process labels**: Use predefined labels (`process_single`, `process_low`, `process_medium`, `process_high`, `process_long`)
5. **Conditional execution**: Use `task.ext.when` for optional processes
6. **Prefix outputs**: Use `${prefix}` for consistent output naming

### Container Standards

- Use containers from `quay.io/biocontainers` when available
- Specify exact version tags (avoid `latest`)
- Configure registry in [nextflow.config](nextflow.config): `docker.registry = "quay.io"`

## Subworkflow Development

Subworkflows combine multiple modules into reusable components. They are named `workflows` with defined inputs and outputs.

### Subworkflow Structure

Place subworkflows in the appropriate directory:
- **Custom subworkflows**: `subworkflows/local/workflow_name/main.nf`
- **nf-core subworkflows**: `subworkflows/nf-core/workflow/main.nf`

### Subworkflow Pattern

```groovy
// subworkflows/local/example/main.nf
workflow EXAMPLE_SUBWORKFLOW {
    take:
    ch_input     // channel: [val(meta), path(files)]
    reference    // path: reference file
    
    main:
    ch_versions = Channel.empty()
    
    PROCESS_A(ch_input, reference)
    ch_versions = ch_versions.mix(PROCESS_A.out.versions)
    
    PROCESS_B(PROCESS_A.out.result)
    ch_versions = ch_versions.mix(PROCESS_B.out.versions)
    
    emit:
    result   = PROCESS_B.out.output
    versions = ch_versions
}
```

### Subworkflow Requirements

- Use `take:` to declare inputs (one per line, with comments)
- Use `emit:` to declare outputs with names
- All emits must be named when multiple outputs exist
- Include version tracking for all processes
- Access outputs using `SUBWORKFLOW_NAME.out.emit_name`

---

## Workflow Development

Workflows orchestrate modules and subworkflows. There are two types: **entry workflows** (unnamed, in [main.nf](main.nf)) and **named subworkflows** (reusable components).

### ⚠️ CRITICAL: Workflow Types

**Entry workflows** and **named workflows** have different syntax rules:

| Feature | Entry Workflow (unnamed) | Named Workflow |
|---------|--------------------------|----------------|
| Declaration | `workflow {` | `workflow NAME {` |
| Input declaration | ❌ No `take:` block | ✅ Required `take:` block |
| Body declaration | ✅ Required `main:` block | ✅ Required `main:` block |
| Output assignment | ✅ Optional `publish:` section | ❌ Use `emit:` instead |
| Output declaration | ✅ Use separate `output` block | ✅ Use `emit:` block |
| Purpose | Pipeline entry point | Reusable component |

### Entry Workflow Pattern

The entry workflow in [main.nf](main.nf) serves as the pipeline entry point:

```groovy
workflow {
    main:
    // Channel initialization
    ch_versions = Channel.empty()
    ch_multiqc_files = Channel.empty()
    
    // Create input channel from samplesheet
    ch_input = Channel
        .fromPath(params.samplesheet)
        .splitCsv(header: true)
        .map { row -> [create_meta_from_row(row), file(row.fastq)] }
    
    // Call processes and subworkflows
    FASTQC(ch_input)
    ch_versions = ch_versions.mix(FASTQC.out.versions)
    ch_multiqc_files = ch_multiqc_files.mix(FASTQC.out.zip)
    
    ALIGNMENT_SUBWORKFLOW(ch_input, reference)
    ch_versions = ch_versions.mix(ALIGNMENT_SUBWORKFLOW.out.versions)
    
    // Collect and publish outputs
    MULTIQC(ch_multiqc_files.collect())

    publish:
    fastqc_results = FASTQC.out
    alignment_bams = ALIGNMENT_SUBWORKFLOW.out.bam
    qc_report      = MULTIQC.out.report
}

output {
    fastqc_results {
        path 'qc/fastqc'
        mode 'copy'
    }
    
    alignment_bams {
        path { meta, bam -> "alignments/${meta.id}/" }
        mode 'copy'
    }
    
    qc_report {
        path 'multiqc_report.html'
        mode 'copy'
    }
}
```

**Key points:**
- No `take:` block (inputs come from parameters)
- Use `main:` block for workflow logic
- Optional `publish:` section assigns channels to output names
- Separate `output` block configures publishing behavior
- Output names in `publish:` must match names in `output` block

### Named Workflow Pattern

Named workflows are reusable components that use `take:` and `emit:` blocks:

```groovy
workflow ALIGNMENT_SUBWORKFLOW {
    take:
    ch_reads     // channel: [val(meta), path(reads)]
    reference    // path: reference genome
    
    main:
    ch_versions = Channel.empty()
    
    BWAMEM(ch_reads, reference)
    ch_versions = ch_versions.mix(BWAMEM.out.versions)
    
    SAMTOOLS_SORT(BWAMEM.out.bam)
    ch_versions = ch_versions.mix(SAMTOOLS_SORT.out.versions)
    
    SAMTOOLS_INDEX(SAMTOOLS_SORT.out.bam)
    ch_versions = ch_versions.mix(SAMTOOLS_INDEX.out.versions)
    
    emit:
    bam      = SAMTOOLS_SORT.out.bam
    bai      = SAMTOOLS_INDEX.out.bai
    versions = ch_versions
}
```

**Key requirements:**
- Use `take:` to declare inputs (one per line with comments)
- Use `main:` block for workflow body
- Use `emit:` block to declare outputs with names
- All emits must be named when multiple outputs exist
- Access outputs using `WORKFLOW_NAME.out.emit_name`
- Do NOT use `publish:` or separate `output` blocks

### Publishing Outputs

#### Basic Structure

The publishing system has three parts:

1. **Output directory**: Set via `-output-dir` CLI option or `outputDir` config (default: `results`)
2. **Output assignment** (optional): In `publish:` section of entry workflow, assign channels to output names
3. **Output configuration**: Top-level `output` block configures how each output is published

#### Publishing Directives

Configure how files are published using directives:

```groovy
output {
    fastqc {
        path 'qc/fastqc'                    // Publish location (required)
        mode 'copy'                         // copy, symlink, link (default: symlink)
        enabled true                        // Boolean or conditional
        overwrite false                     // Don't overwrite existing files
        ignoreErrors false                  // Fail on publishing errors
    }
    
    intermediate {
        path 'intermediate'
        enabled params.save_intermediate    // Conditional on parameter
        mode 'copy'
    }
}
```

**Available directives:**
- `path`: Publish location relative to output directory (required)
- `mode`: Publishing method (`'copy'`, `'symlink'`, `'link'`)
- `enabled`: Conditional publishing (boolean)
- `overwrite`: Overwrite existing files (default: `false`)
- `ignoreErrors`: Continue on publishing errors (default: `false`)
- `label`: Apply labels to published files (can specify multiple times)
- `contentType`: Set content type (cloud storage)
- `storageClass`: Set storage class (cloud storage)
- `tags`: Add tags (cloud storage)

#### Dynamic Publishing Paths

Use closures to customize publish paths based on channel metadata:

```groovy
workflow {
    main:
    // Channel with metadata: [meta, files]
    ch_samples = Channel
        .fromPath(params.samplesheet)
        .splitCsv(header: true)
        .map { row -> [
            [id: row.sample, group: row.group],
            file(row.fastq)
        ] }
    
    ALIGNMENT(ch_samples, reference)
    
    publish:
    bams = ALIGNMENT.out.bam
}

output {
    bams {
        // Publish each sample to group-specific subdirectory
        path { meta, bam -> "alignments/${meta.group}/${meta.id}/" }
        mode 'copy'
    }
}
```

**Closure parameters** must match the channel structure. For `tuple(val(meta), path(files))`, use `{ meta, files -> ... }`.

**Tip:** Use map values for cleaner access:
```groovy
workflow {
    main:
    ch_samples = ALIGNMENT.out.bam
        .map { meta, bam -> 
            [id: meta.id, group: meta.group, bam: bam]
        }
    
    publish:
    bams = ch_samples
}

output {
    bams {
        path { sample -> "alignments/${sample.group}/${sample.id}/" }
    }
}
```

#### Selective File Publishing

Use the `>>` operator to publish specific files from a channel:

```groovy
workflow {
    main:
    PROCESS_TOOL(ch_input)
    // Emits: tuple(val(meta), path(bam), path(bai), path(metrics))
    
    publish:
    results = PROCESS_TOOL.out
}

output {
    results {
        path { meta, bam, bai, metrics ->
            bam >> "alignments/${meta.id}/"
            bai >> "alignments/${meta.id}/"
            metrics >> params.save_metrics ? "metrics/${meta.id}/" : null
        }
    }
}
```

**Key points:**
- Only files captured with `>>` are published
- `>>` left side: source file(s)
- `>>` right side: target directory or filename
- If target ends with `/`, it's treated as a directory
- Setting target to `null` skips publishing that file
- **When using `>>`, ONLY explicitly captured files are published**

**Alternative: Multiple outputs for different file types**

```groovy
workflow {
    main:
    PROCESS_TOOL(ch_input)
    
    publish:
    alignments = PROCESS_TOOL.out.map { meta, bam, bai, metrics -> 
        [meta, bam, bai]
    }
    metrics = PROCESS_TOOL.out.map { meta, bam, bai, metrics -> 
        [meta, metrics]
    }
}

output {
    alignments {
        path { meta, bam, bai -> "alignments/${meta.id}/" }
    }
    
    metrics {
        path { meta, metrics -> "metrics/${meta.id}/" }
        enabled params.save_metrics
    }
}
```

---

## Configuration System

Configuration provides flexibility for different execution environments and process customization.

### Configuration Hierarchy

Configuration files are loaded in this order (highest priority first):

1. **Command line**: `nextflow run main.nf --param value`
2. **Config files**: `-c custom.config`
3. **Profiles**: `-profile docker,test`
4. **Base configs**: `conf/base.config`, `conf/modules.config`
5. **Main config**: `nextflow.config`

### Process Resource Labels

Defined in [conf/base.config](conf/base.config), resource labels provide consistent resource allocation patterns:

| Label | CPUs | Memory | Time | Use Case |
|-------|------|--------|------|----------|
| `process_single` | 1 | 6 GB | 4 h | Single-threaded tools |
| `process_low` | 2 | 12 GB | 4 h | Light computational tasks |
| `process_medium` | 6 | 36 GB | 8 h | Standard bioinformatics tools |
| `process_high` | 12 | 72 GB | 16 h | Intensive computational tasks |
| `process_long` | - | - | 20 h | Long-running processes |
| `process_high_memory` | - | 200 GB | - | Memory-intensive tasks |
| `process_med_memory` | - | 64 GB | - | Medium memory requirements |
| `process_med_cpu` | 4 | 6 GB | 4 h | Medium CPU requirements |
| `error_ignore` | - | - | - | Ignore failures (optional processes) |
| `error_retry` | - | - | - | Retry on failure (up to 2 times) |

**Note:** Resources scale with `task.attempt` on retries and are limited by `params.max_cpus`, `params.max_memory`, and `params.max_time`.

### Process Configuration

**Process-specific settings** in [conf/modules.config](conf/modules.config):

```groovy
process {
    withName: 'TOOL_NAME' {
        ext.args = '--specific-options'
        ext.prefix = { "${meta.id}.custom" }
        ext.when = true  // Conditional execution
    }
    
    withName: 'FASTQC' {
        cpus = 2
        memory = 4.GB
        ext.args = '--quiet'
    }
}
```

**Process selectors:**
- `withName: 'PROCESS'` - Single process
- `withName: 'PROCESS_.*'` - Pattern matching
- `withLabel: 'process_high'` - By label
- `withName: 'SUBWORKFLOW:PROCESS'` - Fully qualified name

### Configuration Profiles

Profiles enable environment-specific and test configurations. Combine multiple profiles with comma separation:

```bash
nextflow run main.nf -profile docker,arm,test_ont
```

#### Container Engine Profiles

| Profile | Purpose | Configuration |
|---------|---------|---------------|
| `docker` | Docker execution | Enables Docker, sets user permissions |
| `singularity` | Singularity/Apptainer execution | Enables Singularity with auto-mounts |

#### Compute Environment Profiles

| Profile | Purpose | Target Environment |
|---------|---------|-------------------|
| `arm` | ARM architecture compatibility | Local ARM (M1/M2/M3 Mac, ARM servers) |
| `nemo` | Nemo HPC cluster | Crick Nemo cluster with GPU support |
| `genomics` | Genomics HPC cluster | Crick Genomics cluster with enhanced resources |

**ARM Profile** ([conf/arm.config](conf/arm.config)):
- Disables Dorado processes (requires x86_64 with GPU)
- Uses ARM-compatible container for Sunder
- Essential for development on M-series Macs

**Nemo Profile** ([conf/nemo.config](conf/nemo.config)):
- Configures GPU resources for Dorado basecalling (2x GPUs, ga100 queue)
- Sets high memory allocations for QC tools
- Optimized for standard HPC workloads

**Genomics Profile** ([conf/genomics.config](conf/genomics.config)):
- Enhanced GPU configuration (4x H100 GPUs, gh100 queue)
- Increased resources for production workloads
- Uses 'sup' (super-accurate) basecalling model by default
- Higher batch processing and parallel operations

#### Test Profiles

Test profiles provide pre-configured datasets and parameters for pipeline validation. See [Testing Profiles](#test-profiles) section for details.

| Profile | Platform | Purpose |
|---------|----------|---------|
| `test_ont` | ONT | Basic demultiplexing from pre-basecalled BAM |
| `test_ont_multi` | ONT | Multi-sample demultiplexing with custom barcode parsing |
| `test_ont_pod5` | ONT | Full pipeline with basecalling from POD5 |
| `test_ont_pod5_batch` | ONT | Batch basecalling from cloud storage |
| `test_illumina` | Illumina | Illumina BCL conversion and demultiplexing |

---

## Testing with nf-test

### Overview

The pipeline uses [nf-test](https://www.nf-test.com/) for testing. Tests are written for the main workflow and critical components, not for individual modules or subworkflows from nf-core.

### Test Configuration Files

- **nf-test config**: [nf-test.config](nf-test.config) - Test framework configuration
- **Test configs**: [tests/config/](tests/config/) - Test-specific settings (reduced resources)
- **Base config**: [conf/base.config](conf/base.config) - Resource labels and error strategies
- **ARM config**: [conf/arm.config](conf/arm.config) - ARM platform compatibility

### Running Tests

**Always use the appropriate platform profile when running nf-test:**

```bash
# Run all tests with ARM profile (for local Mac development)
nf-test test --profile docker,arm

# Run specific test file
nf-test test tests/pipeline_test.nf.test --profile docker,arm

# Run with specific tag
nf-test test --tag "ont" --profile docker,arm

# Update snapshots after intentional changes
nf-test test --update-snapshot --profile docker,arm
```

**Profile selection:**
- Use `docker,arm` for local development on ARM Macs
- Use `docker` for x86_64 Linux systems
- Use `singularity` for HPC environments

### Test File Pattern

```groovy
nextflow_pipeline {
    name "Test pipeline component"
    script "../main.nf"
    tag "component"

    test("basic_functionality") {
        when {
            params {
                outdir      = "$outputDir"
                samplesheet = "tests/data/samplesheet.csv"
            }
        }
        then {
            assertAll(
                { assert workflow.success },
                { assert workflow.trace.succeeded().size() > 0 },
                { assert snapshot(
                    path("${params.outdir}/results/*.txt")
                ).match() }
            )
        }
    }
}
```

### Test Organization

- **Test files**: Place `.nf.test` files alongside the workflows they test
- **Test data**: Store in `tests/data/`
- **Snapshots**: Auto-generated as `.nf.test.snap` files
- **Tags**: Use descriptive tags for test categorization

### Test Profiles

Test profiles provide pre-configured datasets and parameters for different pipeline scenarios. Each profile simulates real-world use cases with minimal data for fast validation.

#### ONT Test Profiles

##### `test_ont` - Basic ONT Demultiplexing

**Purpose:** Tests demultiplexing from a pre-basecalled, unclassified BAM file without basecalling.

**Configuration** ([conf/test_ont.config](conf/test_ont.config)):
```groovy
params {
    max_cpus   = 2
    max_memory = '8.GB'
    max_time   = '6.h'
    
    run_dir     = "$projectDir/tests/data/runs/20230830_1215_P2S-00767-A_PAO92586_3b7ba738"
    bam         = "$projectDir/tests/data/bam/200_sub.bam"
    samplesheet = "$projectDir/tests/data/runs/20230830_1215_P2S-00767-A_PAO92586_3b7ba738/samplesheet.csv"
    dorado_model = 'hac'
}
```

**Command:**
```bash
nextflow run main.nf -profile docker,arm,test_ont
```

**What it tests:**
- Dorado demultiplexing only (no basecalling)
- Single unclassified BAM input
- Standard HAC model configuration
- Basic QC and filtering workflow
- Minimal resource requirements (CI-compatible)

**Data:** 200 subsampled ONT reads from a real sequencing run

---

##### `test_ont_multi` - Multi-Sample Demultiplexing

**Purpose:** Tests multi-sample demultiplexing with custom barcode parsing.

**Configuration** ([conf/test_ont_multi.config](conf/test_ont_multi.config)):
```groovy
params {
    max_cpus   = 2
    max_memory = '8.GB'
    max_time   = '6.h'
    
    run_dir              = "$projectDir/tests/data/runs/fake_run_1"
    bam                  = "$projectDir/tests/data/runs/fake_run_1/1000_reads_6_samples.bam"
    samplesheet          = "$projectDir/tests/data/runs/fake_run_1/samplesheet.csv"
    dorado_model         = 'hac'
    dorado_bc_parse_pos  = 2      // Parse barcode from position 2
    dorado_append_bc     = false  // Don't append barcode to read IDs
    min_qscore           = 0      // No quality filtering for test
}
```

**Command:**
```bash
nextflow run main.nf -profile docker,arm,test_ont_multi
```

**What it tests:**
- Multiple samples in single BAM
- Custom barcode parsing (position-based)
- Barcode ID handling options
- Samplesheet-driven demultiplexing
- Quality score filtering bypass

**Data:** 1000 synthetic reads distributed across 6 samples

---

##### `test_ont_pod5` - Full Pipeline with Basecalling

**Purpose:** Tests complete pipeline from POD5 raw signal files through basecalling and demultiplexing.

**Configuration** ([conf/test_ont_pod5.config](conf/test_ont_pod5.config)):
```groovy
params {
    max_cpus   = 4
    max_memory = '16.GB'
    max_time   = '6.h'
    
    run_dir     = "$projectDir/tests/data/runs/pod5_100"
    samplesheet = "$projectDir/tests/data/runs/pod5_100/samplesheet.csv"
    dorado_model = 'hac'
}
```

**Command:**
```bash
# Requires GPU for basecalling (skip on ARM)
nextflow run main.nf -profile docker,test_ont_pod5  # x86_64 only
```

**What it tests:**
- Dorado basecalling from POD5 files
- POD5 file discovery and batching
- Full demultiplexing workflow
- End-to-end pipeline execution
- Higher resource requirements

**Data:** 100 POD5 files from a real sequencing run

**Note:** This profile requires GPU access and cannot run on ARM systems. Skip when using `-profile arm`.

---

##### `test_ont_pod5_batch` - Batch Basecalling from Cloud

**Purpose:** Tests batch basecalling from cloud storage with POD5 files split into batches.

**Configuration** ([conf/test_ont_pod5_batch.config](conf/test_ont_pod5_batch.config)):
```groovy
params {
    max_cpus   = 4
    max_memory = '16.GB'
    max_time   = '6.h'
    
    run_dir          = "s3://crick-pipeline-technologies-nextflow-test-data/ont/batch_pod5"
    samplesheet      = "$projectDir/tests/data/runs/pod5_100/samplesheet.csv"
    dorado_model     = 'hac'
    dorado_batch_num = 5  // Process 5 POD5 files per batch
}
```

**Command:**
```bash
# Requires AWS credentials and GPU
nextflow run main.nf -profile docker,test_ont_pod5_batch  # x86_64 only
```

**What it tests:**
- Cloud storage integration (S3)
- Batch processing mode
- Multiple basecalling jobs in parallel
- Resource management for batch operations
- Scaling strategies

**Data:** POD5 files stored in S3, processed in batches of 5

**Note:** Requires AWS credentials configured and GPU access. Cannot run on ARM systems.

---

#### Illumina Test Profile

##### `test_illumina` - Illumina BCL Conversion

**Purpose:** Tests Illumina sequencing run demultiplexing using BCL Convert.

**Configuration** ([conf/test_illumina.config](conf/test_illumina.config)):
```groovy
params {
    max_cpus   = 10
    max_memory = '32.GB'
    
    mode        = "illumina"
    run_dir     = "$projectDir/tests/data/illumina_runs/20250714_LH00442_0154_A22WV23LT4"
    samplesheet = "$projectDir/tests/data/illumina_runs/20250714_LH00442_0154_A22WV23LT4/samplesheet.csv"
    fastq       = "/Users/cheshic/dev/test_data/illumina/bcl_convert/20250714_LH00442_0154_A22WV23LT4"
}
```

**Command:**
```bash
nextflow run main.nf -profile docker,arm,test_illumina
```

**What it tests:**
- Illumina mode activation
- BCL Convert demultiplexing
- Illumina-specific samplesheet format
- FASTQ generation and QC
- Illumina-specific MultiQC reports

**Data:** Real Illumina NovaSeq X run data (20250714_LH00442_0154_A22WV23LT4)

**Note:** This profile uses a local FASTQ path that may need adjustment for your environment.

---

### Test Profile Usage Guidelines

**When to use each profile:**

- **Development & CI**: `test_ont`, `test_ont_multi`, `test_illumina` (fastest, ARM-compatible)
- **Full integration testing**: `test_ont_pod5` (requires GPU, x86_64)
- **Cloud & scaling tests**: `test_ont_pod5_batch` (requires AWS & GPU)
- **Platform-specific**: Use `test_illumina` for Illumina workflow changes

**Combining profiles:**
```bash
# Local ARM development (most common)
nextflow run main.nf -profile docker,arm,test_ont

# CI on x86_64 Linux
nextflow run main.nf -profile docker,test_ont

# HPC with Singularity
nextflow run main.nf -profile singularity,nemo,test_ont_pod5
```

## Channel Patterns

Channels are the connective tissue of Nextflow workflows. These patterns help manipulate data flow between processes.

### Basic Meta-Value Channel Structure

```groovy
// Standard channel format: [meta, files...]
ch_input = Channel
    .fromPath(params.samplesheet)
    .splitCsv(header:true)
    .map { row -> 
        def meta = [id: row.sample]
        [meta, file(row.fastq)]
    }
```

### Join Channels

```groovy
// Join by sample ID
ch_bam_bai = ch_bam
    .map { meta, bam -> [meta.id, meta, bam] }
    .join(
        ch_bai.map { meta, bai -> [meta.id, bai] }
    )
    .map { id, meta, bam, bai -> [meta, bam, bai] }
```

### Grouping and Collecting

```groovy
// Group multiple files per sample
ch_grouped = ch_files
    .groupTuple(by: 0)  // Group by meta
    .map { meta, files -> [meta, files.flatten()] }

// Collect all outputs
ch_collected = ch_results
    .map { it[1] }  // Extract files
    .collect()
```

### Version Channels

```groovy
// Initialize and accumulate versions
ch_versions = Channel.empty()
ch_versions = ch_versions.mix(PROCESS_A.out.versions)
ch_versions = ch_versions.mix(PROCESS_B.out.versions)

// Collect unique versions
ch_versions.unique().collectFile(name: 'versions.yml')
```

### Debugging Channels

```groovy
// View channel contents
ch_data.view { "Debug: $it" }

// Inspect structure
ch_data.map { meta, files -> 
    println "Meta: ${meta}, Files: ${files}"
    [meta, files]
}
```

## Code Style

### Code Organization

1. **Shebang and includes** at the top
2. **Channel initialization** early in workflow
3. **Process calls** with clear data flow
4. **Emit block** with descriptive channel names
5. **Comments** for complex channel operations

### Comments

```groovy
//
// MODULE: Process reads with tool
//
TOOL_NAME(ch_reads, reference)

//
// CHANNEL: Join BAM files with their indices
//
ch_bam_bai = ch_bam
    .map { meta, bam -> [meta.id, meta, bam] }
    .join(ch_bai.map { meta, bai -> [meta.id, bai] })
    .map { id, meta, bam, bai -> [meta, bam, bai] }
```

### Error Handling

- Use `task.ext.when` for conditional execution
- Implement error strategies in [conf/base.config](conf/base.config)
- Include meaningful error messages in scripts
- Use `optional: true` for non-critical outputs

## Best Practices

### Performance

- Use `.collect()` judiciously (memory intensive)
- Prefer streaming operations over collection
- Use appropriate process labels for resource allocation
- Consider output publishing mode impact on I/O (prefer `'symlink'` over `'copy'` when possible)

### Reproducibility

- Always specify container versions
- Document parameter requirements
- Use version tracking consistently
- Test against specified resource limits

### Maintainability

- Follow consistent naming conventions
- Document complex channel transformations
- Use subworkflows for reusable components
- Keep processes focused and single-purpose

### Analysing and Debugging

- Use `ch_data.view()` to inspect channel contents
- Check workflow trace for process execution details
- Use the `results` folder for intermediate or final outputs when debugging, assuming the publishing is enabled for those outputs
- Use the `work` directory for intermediate files when debugging, as these are not published and can be inspected directly. Use the execution trace in `results/pipeline_info/execution_trace*` to find the relevant `work` subdirectory for the process of interest.
