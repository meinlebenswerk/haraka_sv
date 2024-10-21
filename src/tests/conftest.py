import os
import logging


def pytest_configure(config):
    os.makedirs("logs", exist_ok=True)
    worker_id = os.environ.get("PYTEST_XDIST_WORKER")
    if worker_id is not None:
        logging.basicConfig(
            format=config.getini("log_file_format"),
            filename=os.path.join("logs", f"pytest-worker-{worker_id}.log"),
            level=logging.DEBUG,
            datefmt="%Y-%m-%d %H:%M:%S",
            # Overwrite existing logs
            filemode="w",
        )
    else:
        logging.basicConfig(
            format=config.getini("log_file_format"),
            filename=os.path.join("logs", "pytest.log"),
            level=logging.DEBUG,
            datefmt="%Y-%m-%d %H:%M:%S",
            # Overwrite existing logs
            filemode="w",
        )
