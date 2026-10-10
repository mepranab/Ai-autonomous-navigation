from src.metrics import NavigationMetrics


def test_metrics_record_steps():
    metrics = NavigationMetrics()

    metrics.record_step()
    metrics.record_step()

    assert metrics.steps_taken == 2


def test_metrics_record_collisions():
    metrics = NavigationMetrics()

    metrics.record_collision()

    assert metrics.collision_attempts == 1


def test_metrics_record_replanning():
    metrics = NavigationMetrics()

    metrics.record_replanning()

    assert metrics.replanning_count == 1


def test_metrics_navigation_success():
    metrics = NavigationMetrics()

    metrics.set_navigation_result(True)

    assert metrics.navigation_success is True


def test_metrics_update_environment():
    metrics = NavigationMetrics()

    metrics.update_environment(
        path_length=12,
        obstacle_count=5,
    )

    assert metrics.path_length == 12
    assert metrics.obstacle_count == 5


def test_metrics_save_to_csv(tmp_path):
    metrics = NavigationMetrics()

    metrics.record_step()
    metrics.record_step()
    metrics.set_navigation_result(True)
    metrics.update_environment(
        path_length=12,
        obstacle_count=5,
    )

    output_file = tmp_path / "metrics.csv"
    metrics.save_to_csv(str(output_file))

    assert output_file.exists()

    content = output_file.read_text(encoding="utf-8")
    assert "steps_taken" in content
    assert "navigation_success" in content
    assert "True" in content
    