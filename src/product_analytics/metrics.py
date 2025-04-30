"""
Metrics Module - Core component for defining standardized product metrics
"""
from typing import Dict, List, Optional, Union, Any
from datetime import datetime, timedelta
import pandas as pd


class Metric:
    """Base class for all metrics in the product analytics framework"""
    
    def __init__(
        self, 
        name: str,
        description: str,
        time_window: Optional[str] = None,
        filter_condition: Optional[str] = None,
        segment: Optional[str] = None
    ):
        """
        Initialize a metric
        
        Args:
            name: Unique name for the metric
            description: Human-readable description of what the metric measures
            time_window: Time period for the metric (e.g., 'day', 'week', 'month')
            filter_condition: SQL-like filter condition to apply
            segment: User segment to calculate this metric for
        """
        self.name = name
        self.description = description
        self.time_window = time_window
        self.filter_condition = filter_condition
        self.segment = segment
        
    def __repr__(self) -> str:
        return f"Metric({self.name}, window={self.time_window})"
    
    def get_sql(self, table_name: str) -> str:
        """Generate SQL to calculate this metric"""
        raise NotImplementedError("Subclasses must implement get_sql method")
    
    def calculate(self, data: pd.DataFrame) -> Union[float, pd.Series]:
        """Calculate the metric from a pandas DataFrame"""
        raise NotImplementedError("Subclasses must implement calculate method")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metric to dictionary for serialization"""
        return {
            "name": self.name,
            "description": self.description,
            "time_window": self.time_window,
            "filter_condition": self.filter_condition,
            "segment": self.segment,
            "type": self.__class__.__name__
        }


class CountMetric(Metric):
    """Metric that counts events or rows"""
    
    def __init__(
        self,
        name: str,
        description: str,
        count_column: str = "*",
        distinct: bool = False,
        **kwargs
    ):
        """
        Initialize a count metric
        
        Args:
            name: Unique name for the metric
            description: Human-readable description of what the metric measures
            count_column: Column to count (default '*' counts all rows)
            distinct: Whether to count distinct values only
            **kwargs: Additional arguments for the base Metric class
        """
        super().__init__(name, description, **kwargs)
        self.count_column = count_column
        self.distinct = distinct
    
    def get_sql(self, table_name: str) -> str:
        """Generate SQL to calculate this count metric"""
        distinct_clause = "DISTINCT " if self.distinct else ""
        where_clause = f"WHERE {self.filter_condition}" if self.filter_condition else ""
        
        sql = f"""
        SELECT COUNT({distinct_clause}{self.count_column}) AS {self.name}
        FROM {table_name}
        {where_clause}
        """
        return sql
    
    def calculate(self, data: pd.DataFrame) -> Union[float, pd.Series]:
        """Calculate the count metric from a pandas DataFrame"""
        if self.filter_condition:
            # In a real implementation, we would parse the filter_condition
            # For now, we'll assume filtered data is passed in
            pass
            
        if self.distinct:
            if self.count_column == "*":
                return len(data)
            else:
                return data[self.count_column].nunique()
        else:
            if self.count_column == "*":
                return len(data)
            else:
                return data[self.count_column].count()


class ActiveUsers(Metric):
    """Metric for counting active users (DAU, WAU, MAU)"""
    
    def __init__(
        self,
        time_window: str = "day",
        user_id_column: str = "user_id",
        **kwargs
    ):
        """
        Initialize an active users metric
        
        Args:
            time_window: Time period for activity ('day', 'week', 'month')
            user_id_column: Column name containing user identifiers
            **kwargs: Additional arguments for the base Metric class
        """
        name = f"{time_window[0].upper()}AU"  # DAU, WAU, MAU
        description = f"{time_window.capitalize()}ly Active Users"
        super().__init__(name, description, time_window=time_window, **kwargs)
        self.user_id_column = user_id_column
    
    def get_sql(self, table_name: str) -> str:
        """Generate SQL to calculate active users"""
        where_clause = f"WHERE {self.filter_condition}" if self.filter_condition else ""
        
        # Date trunc based on time window
        date_trunc = {
            "day": "DATE_TRUNC('day', timestamp)",
            "week": "DATE_TRUNC('week', timestamp)",
            "month": "DATE_TRUNC('month', timestamp)"
        }[self.time_window]
        
        sql = f"""
        SELECT 
            {date_trunc} AS period,
            COUNT(DISTINCT {self.user_id_column}) AS {self.name}
        FROM {table_name}
        {where_clause}
        GROUP BY period
        ORDER BY period
        """
        return sql
    
    def calculate(self, data: pd.DataFrame) -> Union[float, pd.Series]:
        """Calculate active users from a pandas DataFrame"""
        if 'timestamp' not in data.columns or self.user_id_column not in data.columns:
            raise ValueError(f"Data must contain 'timestamp' and '{self.user_id_column}' columns")
            
        # Apply filter if specified
        if self.filter_condition:
            # In a real implementation, we would parse the filter_condition
            # For now, we'll assume filtered data is passed in
            pass
        
        # Convert timestamp to datetime if it's not already
        if not pd.api.types.is_datetime64_any_dtype(data['timestamp']):
            data['timestamp'] = pd.to_datetime(data['timestamp'])
        
        # Group by time period
        if self.time_window == 'day':
            data['period'] = data['timestamp'].dt.floor('D')
        elif self.time_window == 'week':
            data['period'] = data['timestamp'].dt.floor('W')
        elif self.time_window == 'month':
            data['period'] = data['timestamp'].dt.floor('M')
        
        # Count unique users per period
        result = data.groupby('period')[self.user_id_column].nunique()
        result.name = self.name
        
        return result


class RetentionMetric(Metric):
    """Metric for calculating user retention over time periods"""
    
    def __init__(
        self,
        retention_period: int = 1,  # e.g., 1 for next day, 7 for week later
        time_window: str = "day",
        user_id_column: str = "user_id",
        **kwargs
    ):
        """
        Initialize a retention metric
        
        Args:
            retention_period: Number of periods to measure retention
            time_window: Time unit for retention ('day', 'week', 'month')
            user_id_column: Column name containing user identifiers
            **kwargs: Additional arguments for the base Metric class
        """
        name = f"{retention_period}_{time_window}_retention"
        description = f"Retention after {retention_period} {time_window}(s)"
        super().__init__(name, description, time_window=time_window, **kwargs)
        self.retention_period = retention_period
        self.user_id_column = user_id_column
    
    def calculate(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate retention from a pandas DataFrame
        
        Returns: DataFrame with columns for period, cohort_size, returned_users, and retention_rate
        """
        if 'timestamp' not in data.columns or self.user_id_column not in data.columns:
            raise ValueError(f"Data must contain 'timestamp' and '{self.user_id_column}' columns")
            
        # Convert timestamp to datetime if it's not already
        if not pd.api.types.is_datetime64_any_dtype(data['timestamp']):
            data['timestamp'] = pd.to_datetime(data['timestamp'])
        
        # Group by time period
        if self.time_window == 'day':
            data['period'] = data['timestamp'].dt.floor('D')
        elif self.time_window == 'week':
            data['period'] = data['timestamp'].dt.floor('W')
        elif self.time_window == 'month':
            data['period'] = data['timestamp'].dt.floor('M')
        
        # Get first period for each user
        first_periods = data.groupby(self.user_id_column)['period'].min().reset_index()
        first_periods.columns = [self.user_id_column, 'first_period']
        
        # Merge first period info back to main data
        data = pd.merge(data, first_periods, on=self.user_id_column)
        
        # Calculate cohort sizes (number of new users per period)
        cohort_sizes = data.groupby('first_period')[self.user_id_column].nunique().reset_index()
        cohort_sizes.columns = ['cohort_period', 'cohort_size']
        
        # Calculate periods since first use
        data['periods_since_first'] = (data['period'] - data['first_period']).dt.days
        if self.time_window == 'week':
            data['periods_since_first'] = data['periods_since_first'] // 7
        elif self.time_window == 'month':
            data['periods_since_first'] = data['periods_since_first'] // 30  # Approximation
        
        # Filter for the retention period we want
        retention_data = data[data['periods_since_first'] == self.retention_period]
        
        # Count retained users
        retained = retention_data.groupby('first_period')[self.user_id_column].nunique().reset_index()
        retained.columns = ['cohort_period', 'retained_users']
        
        # Merge cohort sizes with retained users
        result = pd.merge(cohort_sizes, retained, on='cohort_period', how='left')
        result['retained_users'] = result['retained_users'].fillna(0)
        
        # Calculate retention rate
        result['retention_rate'] = result['retained_users'] / result['cohort_size']
        
        return result


class ConversionRateMetric(Metric):
    """Metric for calculating conversion rates between two events"""
    
    def __init__(
        self,
        start_event: str,
        end_event: str,
        event_column: str = "event_type",
        user_id_column: str = "user_id",
        time_window: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize a conversion rate metric
        
        Args:
            start_event: Name of the starting event
            end_event: Name of the conversion event
            event_column: Column containing event names/types
            user_id_column: Column containing user identifiers
            time_window: Optional time window to constrain conversions
            **kwargs: Additional arguments for the base Metric class
        """
        name = f"{start_event}_to_{end_event}_conversion"
        description = f"Conversion rate from {start_event} to {end_event}"
        super().__init__(name, description, time_window=time_window, **kwargs)
        self.start_event = start_event
        self.end_event = end_event
        self.event_column = event_column
        self.user_id_column = user_id_column
    
    def calculate(self, data: pd.DataFrame) -> float:
        """Calculate conversion rate from a pandas DataFrame"""
        if self.event_column not in data.columns or self.user_id_column not in data.columns:
            raise ValueError(f"Data must contain '{self.event_column}' and '{self.user_id_column}' columns")
            
        # Get users who performed the start event
        start_users = set(data[data[self.event_column] == self.start_event][self.user_id_column])
        
        if not start_users:
            return 0.0
            
        # Get users who performed the end event
        end_users = set(data[data[self.event_column] == self.end_event][self.user_id_column])
        
        # Calculate conversion rate
        converted_users = start_users.intersection(end_users)
        conversion_rate = len(converted_users) / len(start_users)
        
        return conversion_rate


class MetricRegistry:
    """Registry of available metrics"""
    
    _metrics = {}
    
    @classmethod
    def register(cls, metric_class):
        """Register a metric class"""
        cls._metrics[metric_class.__name__] = metric_class
        return metric_class
    
    @classmethod
    def get_metric_class(cls, metric_type):
        """Get a metric class by name"""
        return cls._metrics.get(metric_type)
    
    @classmethod
    def list_metrics(cls):
        """List all registered metrics"""
        return list(cls._metrics.keys())
    
    @classmethod
    def create_metric(cls, metric_type, **kwargs):
        """Create a metric instance from a type and arguments"""
        metric_class = cls.get_metric_class(metric_type)
        if not metric_class:
            raise ValueError(f"Unknown metric type: {metric_type}")
        return metric_class(**kwargs)


# Register standard metrics
MetricRegistry.register(CountMetric)
MetricRegistry.register(ActiveUsers)
MetricRegistry.register(RetentionMetric)
MetricRegistry.register(ConversionRateMetric)