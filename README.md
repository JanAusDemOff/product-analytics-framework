# Product Analytics Framework

A comprehensive, modular framework for standardizing product analytics across teams and applications. This framework provides a consistent approach to tracking, analyzing, and visualizing product metrics.

## Features

- **Standardized Metrics Library**: Common product metrics with consistent definitions
- **ETL Utilities**: Tools for extracting, transforming, and loading analytics data
- **Visualization Components**: Reusable visualization templates and components
- **Statistical Analysis Modules**: Tools for significance testing, cohort analysis, and more
- **A/B Testing Framework**: End-to-end workflow for designing, running, and analyzing experiments
- **Documentation Generation**: Automated documentation for metrics and dimensions

## Installation

```bash
pip install product-analytics-framework
```

## Quick Start

```python
import product_analytics as pa

# Initialize with your data source
analytics = pa.ProductAnalytics(data_source="postgresql://user:pass@host/db")

# Define a metric
daily_active_users = pa.metrics.ActiveUsers(
    time_window="day",
    filter_condition="event_type = 'app_open'"
)

# Calculate the metric over time
results = analytics.calculate(
    metrics=[daily_active_users],
    dimensions=["date", "platform"],
    start_date="2023-01-01",
    end_date="2023-01-31"
)

# Visualize the results
pa.visualize.time_series(results, metric="active_users", dimension="platform")
```

## Key Components

### Metrics Library

The framework includes a comprehensive library of pre-defined metrics:

- **Engagement Metrics**: DAU, WAU, MAU, stickiness, session depth
- **Growth Metrics**: Acquisition, activation, retention rates
- **Revenue Metrics**: ARPU, LTV, conversion rates
- **Performance Metrics**: Load time, error rates, crash rates

Each metric includes metadata such as definition, calculation method, and recommended visualization types.

### Data Models

Standardized data models ensure consistency across teams:

- **Event Model**: User interactions with timestamps and properties
- **User Model**: User attributes and segments
- **Session Model**: Group events into meaningful sessions
- **Funnel Model**: Track multi-step conversion processes

### Analytical Modules

Specialized modules for common analytical tasks:

- **Funnel Analysis**: Track conversion through sequential steps
- **Cohort Analysis**: Compare behavior of user cohorts over time
- **Segmentation**: Divide users into meaningful segments
- **Retention Analysis**: Analyze user retention patterns

### Visualization Components

Ready-to-use visualization components with consistent styling:

- **Metric Dashboards**: Overview dashboards for key metrics
- **Funnel Visualizations**: Interactive funnel displays
- **Cohort Heatmaps**: Visualize cohort retention patterns
- **Statistical Charts**: Significance testing and experiment results

## Use Cases

### Standardized Reporting

Create consistent reports across products and teams:

```python
# Generate standard weekly report
report = pa.reporting.WeeklyReport(
    metrics=["dau", "retention", "conversion_rate"],
    product="mobile_app",
    date_range=pa.DateRange.last_week()
)

# Export to various formats
report.to_pdf("weekly_report.pdf")
report.to_dashboard(dashboard_id="weekly-metrics")
```

### A/B Testing

End-to-end A/B test workflow:

```python
# Define an experiment
experiment = pa.experiments.Experiment(
    name="new_checkout_flow",
    variants=["control", "variant_a", "variant_b"],
    metrics=["conversion_rate", "average_order_value"],
    segment="new_users"
)

# Analyze results
results = experiment.analyze()

# Generate recommendations
recommendation = pa.experiments.generate_recommendation(results)
```

### Anomaly Detection

Monitor metrics for unusual patterns:

```python
# Set up anomaly detection
anomaly_detector = pa.monitoring.AnomalyDetector(
    metrics=["error_rate", "conversion_rate", "session_duration"],
    sensitivity=0.8
)

# Check for anomalies in recent data
anomalies = anomaly_detector.check_recent()

# Send alerts if anomalies found
if anomalies:
    pa.alerting.send_alert(anomalies)
```

## Documentation

Complete documentation is available at [docs.product-analytics-framework.io](https://docs.product-analytics-framework.io).

## Contributing

Contributions are welcome! Please check out our [contribution guidelines](CONTRIBUTING.md).

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.