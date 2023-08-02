from random import random

from mlflow import log_metric

if __name__ == "__main__":
    print("An example mlflow project")
    log_metric("foo", random())

