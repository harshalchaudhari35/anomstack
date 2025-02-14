import os
import pickle
from typing import List, Tuple

from pyod.models.base import BaseDetector

from anomstack.external.aws.s3 import save_models_s3
from anomstack.external.gcp.gcs import save_models_gcs


def save_models_local(
    models, model_path, metric_batch
) -> List[Tuple[str, BaseDetector]]:
    """
    Save trained models locally.
    """

    model_path = model_path.replace("local://", "")

    if not os.path.exists(f"{model_path}/{metric_batch}"):
        os.makedirs(f"{model_path}/{metric_batch}")

    for metric_name, model in models:
        with open(f"{model_path}/{metric_batch}/{metric_name}.pkl", "wb") as f:
            pickle.dump(model, f)

    return models


def save_models(models, model_path, metric_batch) -> List[Tuple[str, BaseDetector]]:
    """
    Save trained models.
    """

    if model_path.startswith("gs://"):
        models = save_models_gcs(models, model_path, metric_batch)
    elif model_path.startswith("s3://"):
        models = save_models_s3(models, model_path, metric_batch)
    elif model_path.startswith("local://"):
        models = save_models_local(models, model_path, metric_batch)
    else:
        raise ValueError(f"model_path {model_path} not supported")

    return models
