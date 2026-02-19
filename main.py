import datetime

import hydra
from loguru import logger
from omegaconf import DictConfig

from gcp_workflow.infra.vertex import VertexClient
from gcp_workflow.tasks.training.handler import TrainingTask


@hydra.main(version_base=None, config_path="conf", config_name="config")
def main(cfg: DictConfig):
    logger.info("Starting GCP Workflow Launcher")
    logger.info(f"Task: {cfg.task.name}")

    # Create a unique timestamp for this run
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    # 1. Initialize Infrastructure Client
    vertex_client = VertexClient(
        project=cfg.infra.project,
        location=cfg.infra.location,
        staging_bucket=cfg.infra.staging_bucket,
        experiment=cfg.experiment.name if hasattr(cfg, "experiment") else None,
    )

    # 2. Initialize Task Handler
    if cfg.task.name == "object_detection":
        task = TrainingTask(cfg.task)
    else:
        raise NotImplementedError(f"Task {cfg.task.name} not implemented.")

    logger.info(f"Initializing task: {cfg.task.name}")

    # Determine Job Name and Update Output Paths
    job_name_val = (
        cfg.infra.job_name
        if hasattr(cfg.infra, "job_name") and cfg.infra.job_name
        else f"{cfg.task.name}-job"
    )

    display_name = job_name_val

    # Append timestamp to the display name unless it's already unique
    if timestamp not in display_name:
        display_name = f"{display_name}-{timestamp}"

    # Determine base output directory if available (for TensorBoard)
    base_output_directory = None

    # Ensure output directory is unique by appending job_name and timestamp
    for asset in task.data_assets:
        if asset.name == "output_data":
            # Strip trailing slash if present to avoid double slashes
            base_path = asset.relative_path.rstrip("/")

            # Append job_name and timestamp to the path
            if job_name_val not in base_path:
                asset.relative_path = f"{base_path}/{job_name_val}/{timestamp}"
            elif timestamp not in base_path:
                asset.relative_path = f"{base_path}/{timestamp}"

            logger.info(f"Updated output path to: {asset.relative_path}")
            if asset.uri.startswith("gs://"):
                base_output_directory = {"output_uri_prefix": asset.uri}

    # 3. Create Job Specification
    worker_pool_specs = [
        vertex_client.create_worker_pool_spec(
            container_image_uri=task.docker_image,
            command=task.entrypoint,
            args=task.get_overrides(),
            data_assets=task.data_assets,
            machine_type=cfg.infra.machine_type,
            accelerator_type=cfg.infra.accelerator_type,
            accelerator_count=cfg.infra.accelerator_count,
        )
    ]

    # 4. Determine base output directory if available (for TensorBoard)
    base_output_directory = None
    for asset in task.data_assets:
        if asset.name == "output_path" or asset.mount_path == "/output":
            if asset.uri.startswith("gs://"):
                base_output_directory = {"output_uri_prefix": asset.uri}
                break

    # 5. Submit Job
    job_name_val = (
        cfg.infra.job_name
        if hasattr(cfg.infra, "job_name") and cfg.infra.job_name
        else f"{cfg.task.name}-job"
    )

    display_name = job_name_val

    # Append timestamp if it's the default name or if user wants uniqueness by default
    # But for simplicity, let's always append to the display name unless it's already
    # unique
    if timestamp not in display_name:
        display_name = f"{display_name}-{timestamp}"

    # Ensure output directory is unique by appending job_name and timestamp
    for asset in task.data_assets:
        if asset.name == "output_data":
            # Append job_name and timestamp to the path
            if job_name_val not in asset.relative_path:
                asset.relative_path = (
                    f"{asset.relative_path}/{job_name_val}/{timestamp}"
                )
            elif timestamp not in asset.relative_path:
                asset.relative_path = f"{asset.relative_path}/{timestamp}"

            logger.info(f"Updated output path to: {asset.relative_path}")
            if asset.uri.startswith("gs://"):
                base_output_directory = {"output_uri_prefix": asset.uri}

    job_id = vertex_client.submit_job(
        display_name=display_name,
        worker_pool_specs=worker_pool_specs,
        tensorboard=(
            cfg.infra.tensorboard_resource_name
            if hasattr(cfg.infra, "tensorboard_resource_name")
            else None
        ),
        service_account=(
            cfg.infra.service_account if hasattr(cfg.infra, "service_account") else None
        ),
        base_output_directory=base_output_directory,
        dry_run=cfg.infra.dry_run,
    )

    logger.info(f"Job submitted successfully. ID: {job_id}")


if __name__ == "__main__":
    main()
