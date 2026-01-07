from gcp_workflow.core.base import Task
from gcp_workflow.core.data import DataAsset


def test_data_asset_initialization():
    asset = DataAsset(
        name="test_data",
        bucket_name="test-bucket",
        relative_path="data",
        param_name="param",
    )
    assert asset.name == "test_data"
    assert asset.bucket_name == "test-bucket"
    assert asset.relative_path == "data"
    assert asset.uri == "gs://test-bucket/data"
    assert asset.mount_path == "/gcs/test-bucket/data"


def test_task_abstraction():
    class MockTask(Task):
        @property
        def docker_image(self):
            return "mock-image"

        @property
        def entrypoint(self):
            return ["run"]

        @property
        def data_assets(self):
            return []

        def get_overrides(self):
            return ["override=1"]

    task = MockTask()
    assert task.docker_image == "mock-image"
    assert task.entrypoint == ["run"]
    assert task.get_overrides() == ["override=1"]
