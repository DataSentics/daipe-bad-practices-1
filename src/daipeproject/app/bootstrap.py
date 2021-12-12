# Databricks notebook source
# MAGIC %sh
# MAGIC pip install benvy==1.2.2b1

# COMMAND ----------

from benvy.databricks.repos import bootstrap  # noqa
from benvy.databricks.detector import is_databricks_repo  # noqa

if is_databricks_repo():
    bootstrap.install()

# COMMAND ----------

from benvy.databricks.repos import bootstrap  # noqa
from benvy.databricks.detector import is_databricks_repo  # noqa

if is_databricks_repo():
    bootstrap.setup_env()

# COMMAND ----------

# %install_master_package_whl

# COMMAND ----------

import os  # noqa

if "APP_ENV" not in os.environ:
    os.environ["APP_ENV"] = "dev"

if "DAIPE_BOOTSTRAPPED" not in os.environ:
    os.environ["DAIPE_BOOTSTRAPPED"] = "1"

# COMMAND ----------

from daipecore.decorator.ContainerManager import ContainerManager  # noqa
from daipecore.bootstrap.container_factory import create_container  # noqa

def init_container():
    ContainerManager.set_container(create_container(os.environ["APP_ENV"]))
    
init_container()

# COMMAND ----------

from datetime import datetime as dt

class WatcherLogger:
  
    LEVELS = {
      1: "debug",
      2: "info",
      3: "warning",
      4: "error"
    }

    def __init__(self):
        self.messages = []

    def debug(self, message: str):
        self.messages.append((1, dt.now(), message))

    def info(self, message: str):
        self.messages.append((2, dt.now(), message))

    def error(self, message: str):
        self.messages.append((3, dt.now(), message))

    def error(self, message: str):
        self.messages.append((4, dt.now(), message))

    def print(self, minimal_level=1):
        for message in self.messages:
            if message[0] >= minimal_level:
                print(WatcherLogger.LEVELS[message[0]] + ": " + message[1].strftime("%m.%d.%Y_%H:%M:%S") + " " + str(message[2]))

# COMMAND ----------

import threading
import time
from pathlib import Path
from typing import List

class ConfigsWatcherThread(threading.Thread):
    def __init__(self, configs_dir: str, watcher_logger: WatcherLogger, callback, polling_interval = 1):
        threading.Thread.__init__(self)
        self._configs_dir = configs_dir
        self._watcher_logger = watcher_logger
        self._callback = callback
        self._polling_interval = polling_interval
        
        def excepthook(args):
            watcher_logger.error("Configs watcher failed")
            watcher_logger.error(str(args))
            
        threading.excepthook = excepthook
        
    def run(self):
        from datetime import datetime as dt
      
        self._watcher_logger.info(f"Watching of {self._configs_dir} started")
  
        def get_config_file_paths(base_path: str):
            return list(Path(base_path).rglob("*.yaml"))

        def get_files_with_timestamp(paths: List[Path]):
            return {str(path): path.stat().st_mtime for path in paths}

        files_with_timestamp_previous = get_files_with_timestamp(get_config_file_paths(self._configs_dir))

        while True:      
            files_with_timestamp_new = get_files_with_timestamp(get_config_file_paths(self._configs_dir))

            for path, timestamp in files_with_timestamp_previous.items():
                if path not in files_with_timestamp_new:
                    self._watcher_logger.info(f"Existing file deleted: {path}")
                    self._callback()
                    self._watcher_logger.info(f"New container ready")
                    break

                if files_with_timestamp_new[path] > timestamp:
                    time_string = dt.fromtimestamp(files_with_timestamp_new[path]).strftime("%m.%d.%Y_%H:%M:%S")
                    self._watcher_logger.info(f"File changed: {path}, timestamp: {time_string}")
                    self._callback()
                    self._watcher_logger.info(f"New container ready")
                    break

            new_files_only = set(files_with_timestamp_new.keys()) - set(files_with_timestamp_previous.keys())

            if new_files_only != set():
                self._watcher_logger.info(f"New file(s) found: {new_files_only}")
                self._callback()
                self._watcher_logger.info(f"New container ready")

            files_with_timestamp_previous = files_with_timestamp_new

            time.sleep(self._polling_interval)

# COMMAND ----------

from databricksbundle.notebook.helpers import get_notebook_path

def start_configs_watcher(configs_dir: str):
    watcher_logger = WatcherLogger()
    
    def prepare_container():
        try:
            init_container()
        except Exception as e:
            watcher_logger.error("Container initialization failed")
            watcher_logger.debug(str(e))

    watcher_thread = ConfigsWatcherThread(configs_dir, watcher_logger, prepare_container)
    watcher_thread.start()
    
    return watcher_logger, watcher_thread

# COMMAND ----------

if os.environ["APP_ENV"] == "dev":
    configs_dir = "/Workspace" + "/".join(get_notebook_path().split("/")[:6]) + "/_config"
    watcher_logger, watcher_thread = start_configs_watcher(configs_dir)
    watcher_logger.print()
