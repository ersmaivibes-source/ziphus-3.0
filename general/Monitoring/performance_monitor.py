"""
📊 Monitoring - Performance Monitor
Enterprise-grade performance monitoring for Ziphus Bot v3.2

Tracks system performance, metrics, and health indicators.
"""

import asyncio
import logging
import time
import psutil
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict, deque

class PerformanceMonitor:
    """
    Performance Monitor
    
    Tracks and monitors system performance metrics and health.
    """
    
    def __init__(self):
        """Initialize the performance monitor."""
        self.logger = logging.getLogger(self.__class__.__name__)
        self.metrics = defaultdict(deque)
        self.service_stats = defaultdict(dict)
        self.is_running = False
        self.start_time = None
        self.monitoring_task = None
        
        # Configuration
        self.metric_retention_time = timedelta(hours=24)
        self.collection_interval = 30  # seconds
        self.max_metrics_per_type = 2880  # 24 hours worth at 30-second intervals
    
    async def start(self):
        """Start the performance monitoring."""
        try:
            self.logger.info("Starting Performance Monitor...")
            
            self.is_running = True
            self.start_time = datetime.now()
            
            # Start the monitoring task
            self.monitoring_task = asyncio.create_task(self._monitoring_loop())
            
            # Record initial metrics
            await self._collect_system_metrics()
            
            self.logger.info("Performance Monitor started successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to start Performance Monitor: {e}")
            raise
    
    async def stop(self):
        """Stop the performance monitoring."""
        try:
            self.logger.info("Stopping Performance Monitor...")
            
            self.is_running = False
            
            if self.monitoring_task:
                self.monitoring_task.cancel()
                try:
                    await self.monitoring_task
                except asyncio.CancelledError:
                    pass
            
            self.logger.info("Performance Monitor stopped successfully")
            
        except Exception as e:
            self.logger.error(f"Error stopping Performance Monitor: {e}")
    
    async def _monitoring_loop(self):
        """Main monitoring loop that collects metrics periodically."""
        while self.is_running:
            try:
                await self._collect_system_metrics()
                await self._cleanup_old_metrics()
                await asyncio.sleep(self.collection_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(self.collection_interval)
    
    async def _collect_system_metrics(self):
        """Collect system performance metrics."""
        try:
            timestamp = datetime.now()
            
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            self._add_metric('cpu_usage', cpu_percent, timestamp)
            
            # Memory metrics
            memory = psutil.virtual_memory()
            self._add_metric('memory_usage', memory.percent, timestamp)
            self._add_metric('memory_available', memory.available / (1024**3), timestamp)  # GB
            
            # Disk metrics
            disk = psutil.disk_usage('/')
            self._add_metric('disk_usage', disk.percent, timestamp)
            self._add_metric('disk_free', disk.free / (1024**3), timestamp)  # GB
            
            # Network metrics (if available)
            try:
                network = psutil.net_io_counters()
                self._add_metric('network_bytes_sent', network.bytes_sent, timestamp)
                self._add_metric('network_bytes_recv', network.bytes_recv, timestamp)
            except:
                pass  # Network stats might not be available in all environments
            
            # Process-specific metrics
            process = psutil.Process()
            self._add_metric('process_cpu', process.cpu_percent(), timestamp)
            self._add_metric('process_memory', process.memory_info().rss / (1024**2), timestamp)  # MB
            
        except Exception as e:
            self.logger.error(f"Error collecting system metrics: {e}")
    
    def _add_metric(self, metric_name: str, value: float, timestamp: datetime):
        """Add a metric to the collection."""
        metric_queue = self.metrics[metric_name]
        metric_queue.append({
            'value': value,
            'timestamp': timestamp
        })
        
        # Limit the number of metrics stored
        while len(metric_queue) > self.max_metrics_per_type:
            metric_queue.popleft()
    
    async def _cleanup_old_metrics(self):
        """Remove metrics older than the retention time."""
        try:
            cutoff_time = datetime.now() - self.metric_retention_time
            
            for metric_name, metric_queue in self.metrics.items():
                while metric_queue and metric_queue[0]['timestamp'] < cutoff_time:
                    metric_queue.popleft()
                    
        except Exception as e:
            self.logger.error(f"Error cleaning up old metrics: {e}")
    
    async def track_service_start(self, service_name: str):
        """Track when a service starts."""
        self.service_stats[service_name]['start_time'] = datetime.now()
        self.service_stats[service_name]['status'] = 'running'
        self.logger.debug(f"Service {service_name} started")
    
    async def track_service_stop(self, service_name: str):
        """Track when a service stops."""
        if service_name in self.service_stats:
            start_time = self.service_stats[service_name].get('start_time')
            if start_time:
                uptime = datetime.now() - start_time
                self.service_stats[service_name]['last_uptime'] = uptime
            
            self.service_stats[service_name]['status'] = 'stopped'
            self.service_stats[service_name]['stop_time'] = datetime.now()
            
        self.logger.debug(f"Service {service_name} stopped")
    
    async def update_metrics(self):
        """Update performance metrics (called by application service)."""
        # This method can be called by other services to trigger metric updates
        await self._collect_system_metrics()
    
    def get_current_metrics(self) -> Dict[str, Any]:
        """Get the most recent metrics."""
        current_metrics = {}
        
        for metric_name, metric_queue in self.metrics.items():
            if metric_queue:
                current_metrics[metric_name] = metric_queue[-1]['value']
        
        return current_metrics
    
    def get_metric_history(self, metric_name: str, duration: timedelta = None) -> List[Dict]:
        """Get historical data for a specific metric."""
        if metric_name not in self.metrics:
            return []
        
        if duration is None:
            return list(self.metrics[metric_name])
        
        cutoff_time = datetime.now() - duration
        return [
            metric for metric in self.metrics[metric_name]
            if metric['timestamp'] >= cutoff_time
        ]
    
    def get_service_stats(self) -> Dict[str, Any]:
        """Get statistics for all tracked services."""
        return dict(self.service_stats)
    
    def get_system_summary(self) -> Dict[str, Any]:
        """Get a summary of system performance."""
        current_metrics = self.get_current_metrics()
        
        return {
            'uptime': str(datetime.now() - self.start_time) if self.start_time else None,
            'status': 'running' if self.is_running else 'stopped',
            'current_metrics': current_metrics,
            'service_count': len(self.service_stats),
            'metrics_collected': sum(len(queue) for queue in self.metrics.values()),
            'last_collection': max(
                (metric['timestamp'] for queue in self.metrics.values() for metric in queue),
                default=None
            )
        }