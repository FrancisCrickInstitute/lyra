---
name: airflow-debugging-dags
description: Debug Airflow DAGs locally using dag.test() in an IDE or command line with pdb. Use when debugging DAG execution, task failures, import errors, or testing DAGs without deploying to Airflow.
---

# Debugging Airflow DAGs

This skill covers local debugging techniques for Airflow DAGs using `dag.test()`.

---

## Table of Contents

1. [Testing DAGs with dag.test()](#testing-dags-with-dagtest)
2. [Optional Arguments](#optional-arguments)
3. [Conditionally Skipping Tasks](#conditionally-skipping-tasks)
4. [Command Line Debugging with pdb](#command-line-debugging-with-pdb)
5. [IDE Setup](#ide-setup)

---

## Testing DAGs with dag.test()

The `dag.test()` method allows you to debug DAGs in an IDE by running through your DAG in a single serialized Python process.

### Key Benefits

- Works with any supported database (including local SQLite)
- Fails fast (all tasks run in a single process)
- No need to deploy to Airflow scheduler

### Basic Setup

Add these two lines to the bottom of your DAG file:

```python
if __name__ == "__main__":
    dag.test()
```

That's it! You can now run or debug the DAG file directly.

---

## Optional Arguments

You can add optional arguments to fine-tune the testing behavior:

| Argument | Purpose |
|----------|---------|
| `execution_date` | Test argument-specific DAG runs with a particular execution date |
| `use_executor` | Test the DAG using the configured executor instead of running all tasks locally |
| `mark_success_pattern` | Automatically mark tasks matching a regex pattern as successful (useful for skipping sensors/cleanup) |

### Example: Using execution_date

```python
if __name__ == "__main__":
    dag.test(execution_date=pendulum.datetime(2025, 1, 1, tz="UTC"))
```

---

## Conditionally Skipping Tasks

If you don't want to execute certain tasks in your local environment (e.g., dependency check sensors or cleanup steps), use the `mark_success_pattern` argument to automatically mark them successful.

### Example: Skipping Sensors and Cleanup

```python
with DAG("example_dag", default_args=default_args) as dag:
    sensor = ExternalTaskSensor(
        task_id="wait_for_ingestion_dag",
        external_dag_id="ingest_raw_data"
    )
    sensor2 = ExternalTaskSensor(
        task_id="wait_for_dim_dag",
        external_dag_id="ingest_dim"
    )
    collect_stats = PythonOperator(
        task_id="extract_stats_csv",
        python_callable=extract_stats_csv
    )
    # ... run other tasks
    cleanup = PythonOperator(
        task_id="cleanup",
        python_callable=Path.unlink,
        op_args=[collect_stats.output]
    )

    [sensor, sensor2] >> collect_stats >> cleanup

if __name__ == "__main__":
    ingest_testing_data()  # Manually ingest testing data
    run = dag.test(mark_success_pattern="wait_for_.*|cleanup")
    
    # Intermediate CSV is now available for inspection
    csv_path = run.get_task_instance('collect_stats').xcom_pull(
        task_id='collect_stats'
    )
    print(f"Intermediate csv: {csv_path}")
```

In this example:
- The DAG won't wait for either upstream DAG to complete
- Testing data is manually ingested
- The cleanup step is skipped, leaving the intermediate CSV available for inspection

---

## Command Line Debugging with pdb

You can debug a DAG using Python's built-in debugger by running:

```bash
python -m pdb <path_to_dag_file>.py
```

### Example Session

```text
[Breeze:3.10.19] root@ef2c84ad4856:/opt/airflow# python -m pdb providers/standard/src/airflow/providers/standard/example_dags/example_bash_operator.py
> /opt/airflow/providers/standard/src/airflow/providers/standard/example_dags/example_bash_operator.py(18)<module>()
(Pdb) b 45
Breakpoint 1 at /opt/airflow/providers/standard/src/airflow/providers/standard/example_dags/example_bash_operator.py:45
(Pdb) c
> /opt/airflow/providers/standard/src/airflow/providers/standard/example_dags/example_bash_operator.py(45)<module>()
(Pdb) run_this_last
<Task(EmptyOperator): run_this_last>
```

---

## IDE Setup

### Quick Start

1. **Add the main block** at the end of your DAG file:

   ```python
   if __name__ == "__main__":
       dag.test()
   ```

2. **Run or debug** the DAG file directly in your IDE using standard Python debugging tools.

### Tips

- Set breakpoints in your task functions
- Step through task execution
- Inspect XCom values and task states
- Test parameter passing and context variables
