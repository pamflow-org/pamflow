import importlib
import matplotlib
matplotlib.use("Agg")
import pandas as pd

from pamflow.pipelines.quality_control import nodes
importlib.reload(nodes)


def test_plot_sensor_performance_basic():
    rows = [
        {"deploymentID": "A", "timestamp": "2021-01-01T01:00:00+0000"},
        {"deploymentID": "A", "timestamp": "2021-01-01T02:00:00+0000"},
        {"deploymentID": "A", "timestamp": "2021-01-02T01:00:00+0000"},
        {"deploymentID": "B", "timestamp": "2021-01-01T03:00:00+0000"},
        {"deploymentID": "B", "timestamp": "2021-01-08T04:00:00+0000"},
    ]
    media = pd.DataFrame(rows)

    fig, media_out = nodes.plot_sensor_performance(media)

    # basic returns
    from matplotlib.figure import Figure
    assert isinstance(fig, Figure)
    assert "deploymentID" in media_out.columns
    assert "timestamp" in media_out.columns
    assert "count" in media_out.columns

    # expected counts per deployment/day
    grp = media_out.set_index(["deploymentID", "timestamp"])["count"].to_dict()
    assert grp[("A", pd.to_datetime("2021-01-01").date())] == 2
    assert grp[("A", pd.to_datetime("2021-01-02").date())] == 1
    assert grp[("B", pd.to_datetime("2021-01-01").date())] == 1
    assert grp[("B", pd.to_datetime("2021-01-08").date())] == 1