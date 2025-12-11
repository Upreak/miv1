"""
Provider Service for Chatbot/Co-Pilot Module

Manages AI service provider configuration, health monitoring, 
load balancing, and cost optimization.
"""

import logging
import time
import asyncio
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime, timedelta
from collections import defaultdict
import statistics

from ...brain_module.providers.provider_factory import create_provider_from_env
from ...brain_module.providers.base_provider import BaseProvider
from ...config_settings import settings

logger = logging.getLogger(__name__)


class ProviderStatus(Enum):
    """Provider status states"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    MAINTENANCE = "maintenance"


class LoadBalanceStrategy(Enum):
    """Load balancing strategies"""
    ROUND_ROBIN = "round_robin"
    LEAST_LOAD = "least_load"
    FASTEST_RESPONSE = "fastest_response"
    COST_OPTIMIZED = "cost_optimized"


@dataclass
class ProviderMetrics:
    """Provider performance metrics"""
    provider_name: str
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_response_time: float = 0.0
    average_response_time: float = 0.0
    last_success_time: Optional[datetime] = None
    last_failure_time: Optional[datetime] = None
    consecutive_failures: int = 0
    total_cost: float = 0.0
    status: ProviderStatus = ProviderStatus.HEALTHY
    health_score: float = 100.0  # 0-100


@dataclass
class ProviderConfig:
    """Provider configuration"""
    name: str
    api_key: str
    base_url: Optional[str] = None
    timeout: int = 30
    max_retries: int = 3
    enabled: bool = True
    priority: int = 1
    cost_per_token: float = 0.0
    max_concurrent: int = 10


class ProviderService:
    """
    Provider Service for managing AI service providers.
    
    Features:
    - Multi-provider support with automatic fallback
    - Health monitoring and status tracking
    - Load balancing across providers
    - Cost tracking and optimization
    - Performance metrics and analytics
    - Dynamic provider configuration
    """
    
    def __init__(self):
        """Initialize Provider Service"""
        self.providers: Dict[str, BaseProvider] = {}
        self.configs: Dict[str, ProviderConfig] = {}
        self.metrics: Dict[str, ProviderMetrics] = {}
        self.load_balance_strategy = self._parse_load_balance_strategy()
        self.round_robin_index = 0
        self.active_providers: List[str] = []
        self._health_check_task = None
        self._metrics_cleanup_task = None
        self._concurrent_requests: Dict[str, int] = defaultdict(int)
        
        # Initialize from settings
        self._initialize_from_settings()
        
        # Start background tasks
        self._start_background_tasks()
    
    def _parse_load_balance_strategy(self) -> LoadBalanceStrategy:
        """Parse load balancing strategy from settings"""
        strategy = getattr(settings, 'PROVIDER_LOAD_BALANCE', 'round_robin').lower()
        try:
            return LoadBalanceStrategy(strategy)
        except ValueError:
            logger.warning(f"Unknown load balance strategy: {strategy}, using round_robin")
            return LoadBalanceStrategy.ROUND_ROBIN
    
    def _initialize_from_settings(self):
        """Initialize providers from application settings"""
        try:
            # Get provider configurations from settings
            provider_configs = self._get_provider_configs_from_settings()
            
            for config in provider_configs:
                try:
                    # Create provider instance
                    provider = create_provider_from_env(
                        slot=0,  # We'll manage slots dynamically
                        provider_name=config.name,
                        api_key=config.api_key,
                        base_url=config.base_url
                    )
                    
                    if provider:
                        self.providers[config.name] = provider
                        self.configs[config.name] = config
                        self.metrics[config.name] = ProviderMetrics(
                            provider_name=config.name
                        )
                        if config.enabled:
                            self.active_providers.append(config.name)
                        logger.info(f"Initialized provider: {config.name}")
                    else:
                        logger.error(f"Failed to create provider: {config.name}")
                        
                except Exception as e:
                    logger.error(f"Error initializing provider {config.name}: {e}")
                    
        except Exception as e:
            logger.error(f"Error initializing providers from settings: {e}")
    
    def _get_provider_configs_from_settings(self) -> List[ProviderConfig]:
        """Extract provider configurations from settings"""
        configs = []
        
        # Primary provider
        if hasattr(settings, 'PRIMARY_PROVIDER') and settings.PRIMARY_PROVIDER:
            configs.append(ProviderConfig(
                name=settings.PRIMARY_PROVIDER,
                api_key=self._get_api_key(settings.PRIMARY_PROVIDER),
                timeout=settings.PROVIDER_TIMEOUT,
                max_retries=settings.PROVIDER_RETRY_ATTEMPTS,
                priority=1,
                enabled=True
            ))
        
        # Secondary provider
        if hasattr(settings, 'SECONDARY_PROVIDER') and settings.SECONDARY_PROVIDER:
            configs.append(ProviderConfig(
                name=settings.SECONDARY_PROVIDER,
                api_key=self._get_api_key(settings.SECONDARY_PROVIDER),
                timeout=settings.PROVIDER_TIMEOUT,
                max_retries=settings.PROVIDER_RETRY_ATTEMPTS,
                priority=2,
                enabled=True
            ))
        
        # Fallback provider
        if hasattr(settings, 'FALLBACK_PROVIDER') and settings.FALLBACK_PROVIDER:
            configs.append(ProviderConfig(
                name=settings.FALLBACK_PROVIDER,
                api_key=self._get_api_key(settings.FALLBACK_PROVIDER),
                timeout=settings.PROVIDER_TIMEOUT,
                max_retries=settings.PROVIDER_RETRY_ATTEMPTS,
                priority=3,
                enabled=True
            ))
        
        return configs
    
    def _get_api_key(self, provider_name: str) -> str:
        """Get API key for provider from settings"""
        key_attr = f"{provider_name.upper()}_API_KEY"
        return getattr(settings, key_attr, "")
    
    def _start_background_tasks(self):
        """Start background monitoring tasks"""
        # Start health check task
        self._health_check_task = asyncio.create_task(self._health_check_loop())
        
        # Start metrics cleanup task
        self._metrics_cleanup_task = asyncio.create_task(self._metrics_cleanup_loop())
    
    async def _health_check_loop(self):
        """Background task for health checking providers"""
        while True:
            try:
                await self._perform_health_checks()
                await asyncio.sleep(60)  # Check every 60 seconds
            except Exception as e:
                logger.error(f"Error in health check loop: {e}")
                await asyncio.sleep(60)
    
    async def _metrics_cleanup_loop(self):
        """Background task for cleaning up old metrics"""
        while True:
            try:
                self._cleanup_old_metrics()
                await asyncio.sleep(3600)  # Clean up every hour
            except Exception as e:
                logger.error(f"Error in metrics cleanup loop: {e}")
                await asyncio.sleep(3600)
    
    async def _perform_health_checks(self):
        """Perform health checks on all providers"""
        for provider_name in self.active_providers:
            try:
                # Perform health check
                is_healthy = await self._check_provider_health(provider_name)
                
                # Update metrics
                metrics = self.metrics[provider_name]
                if is_healthy:
                    metrics.status = ProviderStatus.HEALTHY
                    metrics.consecutive_failures = 0
                    metrics.last_success_time = datetime.utcnow()
                else:
                    metrics.status = ProviderStatus.UNHEALTHY
                    metrics.consecutive_failures += 1
                    metrics.last_failure_time = datetime.utcnow()
                
                # Update health score
                self._update_health_score(metrics)
                
            except Exception as e:
                logger.error(f"Error checking health for provider {provider_name}: {e}")
                self.metrics[provider_name].status = ProviderStatus.UNHEALTHY
    
    async def _check_provider_health(self, provider_name: str) -> bool:
        """Check if a provider is healthy"""
        try:
            provider = self.providers[provider_name]
            
            # Perform a simple health check (e.g., get model list or ping)
            if hasattr(provider, 'health_check'):
                return await provider.health_check()
            else:
                # Fallback: try to get a simple response
                test_prompt = "Hello"
                result = await provider.generate_response(test_prompt)
                return result is not None and len(result) > 0
                
        except Exception as e:
            logger.warning(f"Provider {provider_name} health check failed: {e}")
            return False
    
    def _update_health_score(self, metrics: ProviderMetrics):
        """Update provider health score based on metrics"""
        # Base score starts at 100
        score = 100.0
        
        # Deduct points for failures
        failure_rate = metrics.failed_requests / max(metrics.total_requests, 1)
        score -= failure_rate * 50
        
        # Deduct points for slow response times
        if metrics.average_response_time > 5.0:  # More than 5 seconds
            score -= 20
        elif metrics.average_response_time > 2.0:  # More than 2 seconds
            score -= 10
        
        # Deduct points for consecutive failures
        score -= metrics.consecutive_failures * 10
        
        # Ensure score is between 0 and 100
        metrics.health_score = max(0, min(100, score))
    
    def _cleanup_old_metrics(self):
        """Clean up old metrics data"""
        cutoff_time = datetime.utcnow() - timedelta(hours=24)
        
        for metrics in self.metrics.values():
            # Reset daily counters if needed
            if metrics.last_success_time and metrics.last_success_time < cutoff_time:
                metrics.total_requests = 0
                metrics.successful_requests = 0
                metrics.failed_requests = 0
                metrics.total_response_time = 0.0
                metrics.average_response_time = 0.0
    
    def get_best_provider(self) -> Optional[str]:
        """
        Get the best available provider based on load balancing strategy.
        
        Returns:
            Optional[str]: Provider name or None if no providers available
        """
        # Filter healthy providers
        healthy_providers = [
            name for name in self.active_providers
            if self.metrics[name].status in [ProviderStatus.HEALTHY, ProviderStatus.DEGRADED]
        ]
        
        if not healthy_providers:
            logger.warning("No healthy providers available")
            return None
        
        if self.load_balance_strategy == LoadBalanceStrategy.ROUND_ROBIN:
            return self._get_round_robin_provider(healthy_providers)
        elif self.load_balance_strategy == LoadBalanceStrategy.LEAST_LOAD:
            return self._get_least_load_provider(healthy_providers)
        elif self.load_balance_strategy == LoadBalanceStrategy.FASTEST_RESPONSE:
            return self._get_fastest_response_provider(healthy_providers)
        elif self.load_balance_strategy == LoadBalanceStrategy.COST_OPTIMIZED:
            return self._get_cost_optimized_provider(healthy_providers)
        
        return healthy_providers[0]
    
    def _get_round_robin_provider(self, providers: List[str]) -> str:
        """Get provider using round robin strategy"""
        if not providers:
            return None
        
        provider = providers[self.round_robin_index % len(providers)]
        self.round_robin_index += 1
        return provider
    
    def _get_least_load_provider(self, providers: List[str]) -> str:
        """Get provider with least concurrent requests"""
        if not providers:
            return None
        
        return min(providers, key=lambda p: self._concurrent_requests[p])
    
    def _get_fastest_response_provider(self, providers: List[str]) -> str:
        """Get provider with fastest average response time"""
        if not providers:
            return None
        
        return min(providers, key=lambda p: self.metrics[p].average_response_time or float('inf'))
    
    def _get_cost_optimized_provider(self, providers: List[str]) -> str:
        """Get provider with best cost-to-performance ratio"""
        if not providers:
            return None
        
        best_provider = None
        best_ratio = float('inf')
        
        for provider in providers:
            metrics = self.metrics[provider]
            config = self.configs[provider]
            
            # Calculate cost-to-performance ratio
            response_time = metrics.average_response_time or 1.0
            cost = config.cost_per_token or 0.001  # Default cost if not specified
            
            ratio = (cost * response_time) / max(metrics.health_score, 1)
            
            if ratio < best_ratio:
                best_ratio = ratio
                best_provider = provider
        
        return best_provider
    
    async def execute_with_fallback(self, 
                                   func: Callable,
                                   *args,
                                   max_retries: Optional[int] = None,
                                   **kwargs) -> Any:
        """
        Execute a function with automatic provider fallback.
        
        Args:
            func: Function to execute (e.g., provider.generate_response)
            *args: Arguments for the function
            max_retries: Maximum retries per provider
            **kwargs: Keyword arguments for the function
            
        Returns:
            Any: Function result
        """
        attempted_providers = set()
        
        while len(attempted_providers) < len(self.active_providers):
            provider_name = self.get_best_provider()
            
            if not provider_name or provider_name in attempted_providers:
                break
            
            attempted_providers.add(provider_name)
            
            try:
                # Execute with retry logic
                result = await self._execute_with_retries(
                    provider_name, func, *args, max_retries=max_retries, **kwargs
                )
                
                if result is not None:
                    return result
                    
            except Exception as e:
                logger.error(f"Provider {provider_name} failed: {e}")
                # Continue to next provider
        
        raise Exception("All providers failed")
    
    async def _execute_with_retries(self,
                                   provider_name: str,
                                   func: Callable,
                                   *args,
                                   max_retries: Optional[int] = None,
                                   **kwargs) -> Any:
        """
        Execute function with retries for a specific provider.
        
        Args:
            provider_name: Name of provider
            func: Function to execute
            *args: Function arguments
            max_retries: Maximum retries (uses config if None)
            **kwargs: Function keyword arguments
            
        Returns:
            Any: Function result
        """
        config = self.configs[provider_name]
        max_retries = max_retries if max_retries is not None else config.max_retries
        
        for attempt in range(max_retries + 1):
            try:
                # Check concurrent request limit
                if self._concurrent_requests[provider_name] >= config.max_concurrent:
                    logger.warning(f"Provider {provider_name} at max concurrent limit")
                    if attempt == max_retries:
                        raise Exception(f"Provider {provider_name} at max concurrent limit")
                    await asyncio.sleep(1)  # Wait before retry
                    continue
                
                # Increment concurrent requests
                self._concurrent_requests[provider_name] += 1
                
                # Execute function
                start_time = time.time()
                result = await func(*args, **kwargs)
                end_time = time.time()
                
                # Update metrics
                self._update_success_metrics(provider_name, end_time - start_time)
                
                return result
                
            except Exception as e:
                # Update failure metrics
                self._update_failure_metrics(provider_name)
                
                if attempt == max_retries:
                    raise e
                
                # Wait before retry
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
                
            finally:
                # Decrement concurrent requests
                self._concurrent_requests[provider_name] = max(0, self._concurrent_requests[provider_name] - 1)
    
    def _update_success_metrics(self, provider_name: str, response_time: float):
        """Update success metrics for provider"""
        metrics = self.metrics[provider_name]
        
        metrics.total_requests += 1
        metrics.successful_requests += 1
        metrics.total_response_time += response_time
        metrics.average_response_time = metrics.total_response_time / metrics.successful_requests
        metrics.last_success_time = datetime.utcnow()
        metrics.consecutive_failures = 0
        
        # Update health score
        self._update_health_score(metrics)
    
    def _update_failure_metrics(self, provider_name: str):
        """Update failure metrics for provider"""
        metrics = self.metrics[provider_name]
        
        metrics.total_requests += 1
        metrics.failed_requests += 1
        metrics.last_failure_time = datetime.utcnow()
        metrics.consecutive_failures += 1
        
        # Update health score
        self._update_health_score(metrics)
    
    def get_provider_metrics(self, provider_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get metrics for providers.
        
        Args:
            provider_name: Specific provider name (returns all if None)
            
        Returns:
            Dict[str, Any]: Provider metrics
        """
        if provider_name:
            if provider_name in self.metrics:
                return asdict(self.metrics[provider_name])
            else:
                return {}
        
        return {name: asdict(metrics) for name, metrics in self.metrics.items()}
    
    def get_provider_status(self) -> Dict[str, Any]:
        """Get overall provider status"""
        return {
            'active_providers': self.active_providers,
            'load_balance_strategy': self.load_balance_strategy.value,
            'provider_count': len(self.active_providers),
            'metrics': self.get_provider_metrics()
        }
    
    def add_provider(self, config: ProviderConfig) -> bool:
        """
        Add a new provider dynamically.
        
        Args:
            config: Provider configuration
            
        Returns:
            bool: True if successful
        """
        try:
            provider = create_provider_from_env(
                slot=0,
                provider_name=config.name,
                api_key=config.api_key,
                base_url=config.base_url
            )
            
            if provider:
                self.providers[config.name] = provider
                self.configs[config.name] = config
                self.metrics[config.name] = ProviderMetrics(provider_name=config.name)
                
                if config.enabled:
                    self.active_providers.append(config.name)
                
                logger.info(f"Added provider: {config.name}")
                return True
            else:
                logger.error(f"Failed to create provider: {config.name}")
                return False
                
        except Exception as e:
            logger.error(f"Error adding provider {config.name}: {e}")
            return False
    
    def remove_provider(self, provider_name: str) -> bool:
        """
        Remove a provider.
        
        Args:
            provider_name: Name of provider to remove
            
        Returns:
            bool: True if successful
        """
        try:
            if provider_name in self.providers:
                del self.providers[provider_name]
                del self.configs[provider_name]
                del self.metrics[provider_name]
                
                if provider_name in self.active_providers:
                    self.active_providers.remove(provider_name)
                
                logger.info(f"Removed provider: {provider_name}")
                return True
            else:
                logger.warning(f"Provider {provider_name} not found")
                return False
                
        except Exception as e:
            logger.error(f"Error removing provider {provider_name}: {e}")
            return False
    
    def update_provider_config(self, provider_name: str, config: ProviderConfig) -> bool:
        """
        Update provider configuration.
        
        Args:
            provider_name: Name of provider
            config: New configuration
            
        Returns:
            bool: True if successful
        """
        try:
            if provider_name in self.configs:
                self.configs[provider_name] = config
                
                # Update active providers list if enabled status changed
                if config.enabled and provider_name not in self.active_providers:
                    self.active_providers.append(provider_name)
                elif not config.enabled and provider_name in self.active_providers:
                    self.active_providers.remove(provider_name)
                
                logger.info(f"Updated provider config: {provider_name}")
                return True
            else:
                logger.warning(f"Provider {provider_name} not found")
                return False
                
        except Exception as e:
            logger.error(f"Error updating provider {provider_name}: {e}")
            return False
    
    async def shutdown(self):
        """Shutdown provider service and cleanup resources"""
        if self._health_check_task:
            self._health_check_task.cancel()
        
        if self._metrics_cleanup_task:
            self._metrics_cleanup_task.cancel()
        
        logger.info("Provider service shutdown complete")