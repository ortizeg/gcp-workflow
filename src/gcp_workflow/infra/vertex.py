from typing import Any, Dict, List, Optional

from google.cloud import aiplatform
from loguru import logger


class VertexClient:
    def __init__(
        self,
        project: str,
        location: str,
        staging_bucket: str,
        experiment: Optional[str] = None,
    ):
        self.project = project
        self.location = location
        self.staging_bucket = staging_bucket
        self.experiment = experiment

        aiplatform.init(
            project=project,
            location=location,
            staging_bucket=staging_bucket,
            experiment=experiment,
        )

    def submit_job(
        self,
        display_name: str,
        worker_pool_specs: List[Dict[str, Any]],
        labels: Optional[Dict[str, str]] = None,
        tensorboard: Optional[str] = None,
        service_account: Optional[str] = None,
        base_output_directory: Optional[Dict[str, str]] = None,
        dry_run: bool = False,
    ):
        if dry_run:
            logger.info("DRY RUN: Would submit the following CustomJob to Vertex AI:")
            logger.info(
                {
                    "display_name": display_name,
                    "worker_pool_specs": worker_pool_specs,
                    "labels": labels,
                    "tensorboard": tensorboard,
                    "service_account": service_account,
                    "base_output_directory": base_output_directory,
                }
            )
            return "dry-run-job-id"

        logger.info(f"Submitting CustomJob: {display_name}")
        job = aiplatform.CustomJob(
            display_name=display_name,
            worker_pool_specs=worker_pool_specs,
            labels=labels,
            base_output_dir=(
                base_output_directory.get("output_uri_prefix")
                if base_output_directory
                else None
            ),
        )

        job.submit(
            tensorboard=tensorboard,
            service_account=service_account,
        )
        return job.resource_name

    def create_worker_pool_spec(
        self,
        container_image_uri: str,
        command: List[str],
        args: List[str],
        data_assets: List[Any],
        machine_type: str = "n1-standard-4",
        accelerator_type: str = "NVIDIA_TESLA_T4",
        accelerator_count: int = 1,
    ) -> Dict[str, Any]:
        """
        Creates a worker pool specification for the Vertex AI CustomJob.
        Note: GCS buckets are automatically mounted at /gcs/ by Vertex AI.
        """
        # Note regarding GCS mounts:
        # Vertex AI automatically mounts GCS buckets at /gcs/<bucket_name>
        # provided the service account has permission.
        # We don't need to explicitly define mounts in the spec for standard GCS access.

        return {
            "machine_spec": {
                "machine_type": machine_type,
                "accelerator_type": accelerator_type,
                "accelerator_count": accelerator_count,
            },
            "replica_count": 1,
            "container_spec": {
                "image_uri": container_image_uri,
                "command": command,
                "args": args,
            },
        }
