"""
src/billing_collector.py
Collect AWS cost and usage data from Cost Explorer API.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any

from src.aws_utils import CostExplorerCollector
from src.collect_metrics import insert_metric

logger = logging.getLogger(__name__)


class BillingDataPipeline:
    """Collect and store billing data from AWS"""
    
    def __init__(self):
        self.collector = CostExplorerCollector()
    
    def collect_daily_costs(self, days_back: int = 7) -> List[Dict[str, Any]]:
        """
        Collect daily cost data for the past N days.
        
        Args:
            days_back: Number of days to look back (default: 7)
        
        Returns:
            List of cost records
        """
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days_back)
        
        try:
            response = self.collector.get_cost_data(
                start_date=start_date.isoformat(),
                end_date=end_date.isoformat(),
                granularity="DAILY",
                metrics=["UnblendedCost"]
            )
            
            # Parse response and insert into database
            results = self._parse_cost_response(response)
            logger.info(f"✅ Collected {len(results)} daily cost records")
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Error collecting daily costs: {e}")
            return []
    
    def collect_costs_by_service(self, days_back: int = 7) -> Dict[str, float]:
        """
        Collect costs grouped by AWS service.
        
        Args:
            days_back: Number of days to look back
        
        Returns:
            Dict mapping service name to total cost
        """
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days_back)
        
        try:
            response = self.collector.get_cost_data(
                start_date=start_date.isoformat(),
                end_date=end_date.isoformat(),
                granularity="DAILY",
                metrics=["UnblendedCost"]
            )
            
            service_costs = {}
            for result in response.get("ResultsByTime", []):
                for group in result.get("Groups", []):
                    service = group["Keys"][0]  # Service name
                    cost = float(group["Metrics"]["UnblendedCost"]["Amount"])
                    
                    if service not in service_costs:
                        service_costs[service] = 0
                    service_costs[service] += cost
            
            logger.info(f"✅ Collected costs for {len(service_costs)} services")
            return service_costs
            
        except Exception as e:
            logger.error(f"❌ Error collecting costs by service: {e}")
            return {}
    
    def collect_costs_by_resource(self, days_back: int = 7) -> Dict[str, float]:
        """
        Collect costs grouped by resource (using resource tags).
        
        Args:
            days_back: Number of days to look back
        
        Returns:
            Dict mapping resource name/ID to total cost
        """
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days_back)
        
        try:
            response = self.collector.get_cost_by_resource(
                start_date=start_date.isoformat(),
                end_date=end_date.isoformat()
            )
            
            resource_costs = {}
            for result in response.get("ResultsByTime", []):
                for group in result.get("Groups", []):
                    resource = group["Keys"][0]  # Resource name/tag
                    cost = float(group["Metrics"]["UnblendedCost"]["Amount"])
                    
                    if resource not in resource_costs:
                        resource_costs[resource] = 0
                    resource_costs[resource] += cost
                    
                    # Store in database
                    timestamp = result["TimePeriod"]["Start"]
                    insert_metric(
                        resource_id=resource,
                        metric_name="billing_cost",
                        metric_value=cost,
                        timestamp=timestamp
                    )
            
            logger.info(f"✅ Collected costs for {len(resource_costs)} resources")
            return resource_costs
            
        except Exception as e:
            logger.error(f"❌ Error collecting resource costs: {e}")
            return {}
    
    def _parse_cost_response(self, response: Dict) -> List[Dict[str, Any]]:
        """
        Parse Cost Explorer API response into records.
        
        Returns:
            List of records with timestamp, service, and cost
        """
        records = []
        
        try:
            for result in response.get("ResultsByTime", []):
                timestamp = result["TimePeriod"]["Start"]
                
                for group in result.get("Groups", []):
                    service = group["Keys"][0]
                    amount = float(group["Metrics"]["UnblendedCost"]["Amount"])
                    
                    record = {
                        "timestamp": timestamp,
                        "service": service,
                        "cost": amount
                    }
                    records.append(record)
                    
                    # Also store in database
                    insert_metric(
                        resource_id=service,
                        metric_name="service_cost",
                        metric_value=amount,
                        timestamp=timestamp
                    )
            
            return records
            
        except Exception as e:
            logger.error(f"❌ Error parsing cost response: {e}")
            return []
    
    def calculate_cost_anomalies(self, current_cost: float, 
                                history: List[float],
                                threshold_percent: float = 20.0) -> bool:
        """
        Detect cost anomalies using simple statistical method.
        
        Args:
            current_cost: Current day's cost
            history: List of previous days' costs
            threshold_percent: Percentage increase threshold
        
        Returns:
            True if anomaly detected
        """
        if not history:
            return False
        
        avg_cost = sum(history) / len(history)
        percent_change = ((current_cost - avg_cost) / avg_cost) * 100
        
        is_anomaly = percent_change > threshold_percent
        
        logger.info(f"Cost: ${current_cost:.2f}, Avg: ${avg_cost:.2f}, Change: {percent_change:.1f}%")
        
        if is_anomaly:
            logger.warning(f"⚠️  COST ANOMALY DETECTED: {percent_change:.1f}% increase!")
        
        return is_anomaly
