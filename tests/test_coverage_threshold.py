import io


def test_coverage_threshold(pytestconfig):
    plugin = pytestconfig.pluginmanager.get_plugin("_cov")
    assert plugin is not None, "Coverage plugin is required"
    cov = plugin.cov_controller.cov
    cov.stop()
    cov.save()
    total = cov.report(file=io.StringIO())
    assert total >= 90.0, f"Total coverage {total:.2f}% is below 90%"
