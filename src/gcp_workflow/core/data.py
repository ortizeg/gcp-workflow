from dataclasses import dataclass
from typing import Optional


@dataclass
class DataAsset:
    """
    Represents a data asset that can be used in a task.
    """

    bucket_name: str
    relative_path: str
    param_name: str  # Parameter name to override (e.g. "training.dataset_dir")
    name: Optional[str] = None  # Optional name for the asset, e.g. "training_data"

    @property
    def uri(self) -> str:
        """Returns the GCS URI."""
        return f"gs://{self.bucket_name}/{self.relative_path}"

    @property
    def mount_path(self) -> str:
        """Returns the local mount path in the container."""
        # Vertex AI mounts buckets at /gcs/<bucket_name>
        return f"/gcs/{self.bucket_name}/{self.relative_path}"
