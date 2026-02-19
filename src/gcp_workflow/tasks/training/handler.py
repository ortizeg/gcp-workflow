from typing import List

from omegaconf import DictConfig

from gcp_workflow.core.base import DataAsset, Task


class TrainingTask(Task):
    def __init__(self, cfg: DictConfig):
        self.cfg = cfg
        self._data_assets = []

        # Parse data assets from config
        if hasattr(cfg, "data_assets"):
            for name, asset_cfg in cfg.data_assets.items():
                self._data_assets.append(
                    DataAsset(
                        name=name,
                        bucket_name=asset_cfg.bucket_name,
                        relative_path=asset_cfg.relative_path,
                        param_name=asset_cfg.param_name,
                    )
                )

    @property
    def docker_image(self) -> str:
        return self.cfg.docker_image

    @property
    def entrypoint(self) -> List[str]:
        return list(self.cfg.entrypoint)

    @property
    def data_assets(self) -> List[DataAsset]:
        return self._data_assets

    def get_overrides(self) -> List[str]:
        # Start with base overrides from config (as a string or list)
        overrides = []

        # Support both 'overrides' (string/list) and legacy 'params' (dict)
        if hasattr(self.cfg, "overrides") and self.cfg.overrides:
            if isinstance(self.cfg.overrides, str):
                # Split string by whitespace, but be careful (simple split for now)
                overrides.extend(self.cfg.overrides.split())
            elif isinstance(self.cfg.overrides, list):
                overrides.extend(self.cfg.overrides)

        elif hasattr(self.cfg, "params") and self.cfg.params:
            for key, value in self.cfg.params.items():
                overrides.append(f"{key}={value}")

        # Append data asset overrides if param_name is specified
        for asset in self.data_assets:
            overrides.append(f"{asset.param_name}={asset.mount_path}")

        return overrides
