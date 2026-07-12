# Training Experiment Records

Each training run uses an independent timestamped directory under this folder.

Files retained in Git:

- `config.yaml`: training configuration used for the run.
- `train_command.txt`: resolved Ultralytics training command.
- `environment_snapshot.txt`: Python, platform, dependency, and Git information.
- `summary.json`: run status and metrics copied from the real Ultralytics output.
- `effective_args.yaml`: stable copy of Ultralytics' generated `train/args.yaml`.
- `git_commit.txt`, `start_time.txt`, and `end_time.txt`: reproducibility metadata.

Compatibility files `command.txt` and `environment.txt` are also retained for
existing runs.

Git-ignored artifacts include model checkpoints, caches, plots, batch images,
predictions, and framework-generated CSV files. Metrics intended for comparison
must be copied from real framework output into `summary.json`; last-epoch and
best-recorded metrics must remain explicitly distinguished. Do not invent or
manually estimate metrics.
