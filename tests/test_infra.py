from unittest.mock import patch

from gcp_workflow.infra.vertex import VertexClient


@patch("gcp_workflow.infra.vertex.aiplatform")
def test_create_worker_pool_spec(mock_aiplatform):
    client = VertexClient(project="p", location="l", staging_bucket="b")

    spec = client.create_worker_pool_spec(
        container_image_uri="image",
        command=["cmd"],
        args=["arg"],
        data_assets=[],
        machine_type="n1-standard-4",
    )

    assert spec["machine_spec"]["machine_type"] == "n1-standard-4"
    assert spec["container_spec"]["image_uri"] == "image"
    assert spec["container_spec"]["command"] == ["cmd"]
    assert spec["container_spec"]["args"] == ["arg"]
    # We no longer explicitly add gcs_mounts to the dict as Vertex AI handles it
    # automatically via /gcs/ paths.
