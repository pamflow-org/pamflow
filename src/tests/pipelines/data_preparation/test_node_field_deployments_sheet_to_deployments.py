import pandas as pd

from pamflow.pipelines.data_preparation import nodes
from pamflow.datasets.pamDP.deployments import deployments_pamdp_columns


def test_field_deployments_sheet_to_deployments_basic():
    # input field_deployments with required columns
    field_deployments = pd.DataFrame(
        [
            {
                "deploymentID": "dep1",
                "setupByName": "John",
                "setupByLastName": "Doe",
                "deploymentStartDate": "2020-01-01",
                "deploymentStartTime": "08:00:00",
                "deploymentEndDate": "2020-01-02",
                "deploymentEndTime": "10:30:00",
            }
        ]
    )

    # minimal media_summary (function only logs n_recordings)
    media_summary = pd.DataFrame([{"n_recordings": 5}])

    deployments = nodes.field_deployments_sheet_to_deployments(
        field_deployments.copy(), media_summary, timezone="America/Bogota"
    )

    # same number of rows
    assert len(deployments) == 1

    # returned frame follows pamDP schema
    assert list(deployments.columns) == list(deployments_pamdp_columns)

    # copied fields
    assert deployments.loc[0, "deploymentID"] == "dep1"

    # setupBy combined from name + last name (no separator in implementation)
    assert deployments.loc[0, "setupBy"] == "John Doe"

    # deploymentStart / deploymentEnd formatted and localized to America/Bogota (-0500)
    assert deployments.loc[0, "deploymentStart"] == "2020-01-01T08:00:00-0500"
    assert deployments.loc[0, "deploymentEnd"] == "2020-01-02T10:30:00-0500"