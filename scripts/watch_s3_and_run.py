"""
watch_s3_and_run.py
Polls S3 for changes to the cost report. When a new version is detected,
automatically runs the full pipeline and pushes updated outputs to GitHub.

Usage:
    python scripts/watch_s3_and_run.py

Stop with Ctrl+C.
"""

import sys
import time
import logging
import subprocess
from pathlib import Path

import boto3

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import COST_REPORT_BUCKET, COST_REPORT_KEY, AWS_REGION

# ── Config ──────────────────────────────────────────────────────────────────
POLL_INTERVAL_SECONDS = 60          # Check S3 every 60 seconds
AUTO_GIT_PUSH = True                # Set False if you don't want auto-push
# ────────────────────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

PIPELINE_SCRIPT = Path(__file__).parent / "run_data_pipeline.py"
ROOT = Path(__file__).parent.parent


def get_s3_last_modified(bucket: str, key: str) -> str | None:
    """Return the LastModified timestamp string of an S3 object, or None on error."""
    try:
        s3 = boto3.client("s3", region_name=AWS_REGION)
        head = s3.head_object(Bucket=bucket, Key=key)
        return str(head["LastModified"])
    except Exception as e:
        logger.warning(f"Could not check S3 object: {e}")
        return None


def run_pipeline() -> bool:
    """Run the full data pipeline. Returns True on success."""
    logger.info("Running full pipeline...")
    result = subprocess.run(
        [sys.executable, str(PIPELINE_SCRIPT), "--full"],
        cwd=str(ROOT),
    )
    if result.returncode == 0:
        logger.info("Pipeline completed successfully.")
        return True
    else:
        logger.error(f"Pipeline failed with exit code {result.returncode}.")
        return False


def git_push():
    """Stage updated outputs and push to GitHub."""
    files = [
        "ml_ready_data.csv",
        "anomalies.json",
        "output/ml_ready_data.csv",
        "output/anomalies.json",
        "output/cost_report.json",
    ]
    subprocess.run(["git", "add"] + files, cwd=str(ROOT))
    result = subprocess.run(
        ["git", "commit", "-m", "Auto: pipeline triggered by S3 update"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )
    if "nothing to commit" in result.stdout:
        logger.info("Git: nothing new to commit.")
        return
    subprocess.run(
        ["git", "push", "origin", "data-pipeline-branch"],
        cwd=str(ROOT),
    )
    logger.info("Pushed updated outputs to GitHub.")


def main():
    logger.info(f"Watching s3://{COST_REPORT_BUCKET}/{COST_REPORT_KEY}")
    logger.info(f"Polling every {POLL_INTERVAL_SECONDS}s. Press Ctrl+C to stop.")

    last_modified = get_s3_last_modified(COST_REPORT_BUCKET, COST_REPORT_KEY)
    if last_modified:
        logger.info(f"Current S3 version: {last_modified}")
    else:
        logger.warning("Could not read initial S3 state. Will retry each poll.")

    while True:
        time.sleep(POLL_INTERVAL_SECONDS)
        current = get_s3_last_modified(COST_REPORT_BUCKET, COST_REPORT_KEY)

        if current is None:
            logger.warning("S3 check failed, skipping this cycle.")
            continue

        if current != last_modified:
            logger.info(f"S3 file changed! New version: {current}")
            last_modified = current

            if run_pipeline():
                if AUTO_GIT_PUSH:
                    git_push()
        else:
            logger.info("No change detected.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Watcher stopped.")
