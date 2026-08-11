from scripts.dashboard import render_dashboard


def test_runtime_dashboard_contains_all_six_panels() -> None:
    rendered = render_dashboard()
    for title in (
        "Latency percentiles",
        "Request traffic",
        "Error rate and breakdown",
        "Cost over time",
        "Input and output tokens",
        "Quality proxy",
    ):
        assert title in rendered
    assert "Time range: last 60 minutes" in rendered
    assert "Refresh: 30 seconds" in rendered
