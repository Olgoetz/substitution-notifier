import os

os.environ[
    "SUBSTITUTION_NOTIFIER_RECIPIENT"] = "ADJUST ME!!"  # Rename the file to 'config.py'
os.environ["SUBSTITUTION_NOTIFIER_LOG"] = "INFO"
os.environ[
    "SUBSTITUTION_NOTIFIER_LOGFORMAT"] = "%(asctime)-15s %(levelname)-8s %(name)-18s %(message)s"
