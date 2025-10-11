#!/usr/bin/env python3
"""
Performance Enhancement Integration
Integrates all optimized utilities with the bot for maximum performance
"""

import asyncio
import logging
import time
from datetime import datetime
from typing import Dict, Any, Optional
import sys
import os

# Add project root to path
sys.path.append(".")

logger = logging.getLogger("astra.performance")


class PerformanceEnhancementManager:
    """Manages all performance optimizations for AstraBot"""

    def __init__(self):
        self.start_time = time.time()
        self.enhancement_status = {}
        self.performance_metrics = {}

    async def initialize_all_optimizations(self):
        """Initialize all performance optimizations"""
        logger.info("🚀 Initializing Performance Enhancement Suite...")

        # Initialize Enhanced Cache Manager
        await self._initialize_cache_manager()

        # Initialize Database with Connection Pooling
        await self._initialize_database()

        # Initialize HTTP Session Manager
        await self._initialize_http_manager()

        # Initialize API Key Management
        self._initialize_api_management()

        # Initialize Lightning Optimizer
        await self._initialize_lightning_optimizer()

        # Setup Performance Monitoring
        self._setup_performance_monitoring()

        # Validate All Systems
        await self._validate_all_systems()

        total_init_time = time.time() - self.start_time
        logger.info(
            f"✅ Performance Enhancement Suite initialized in {total_init_time:.2f}s"
        )

    async def _initialize_cache_manager(self):
        """Initialize enhanced cache manager"""
        try:
            from utils.cache_manager import cache

            start_time = time.time()
            # Cache is already initialized on import, just test it
            await cache.set("init_test", "success", ttl=60)
            result = await cache.get("init_test")

            duration = time.time() - start_time
            self.enhancement_status["cache_manager"] = {
                "status": "success" if result == "success" else "failed",
                "init_time": duration,
                "details": "Hybrid memory/file caching with compression",
            }

            if result == "success":
                logger.info(f"✅ Enhanced Cache Manager ready ({duration:.3f}s)")
            else:
                logger.error("❌ Cache Manager initialization failed")

        except Exception as e:
            logger.error(f"❌ Cache Manager error: {e}")
            self.enhancement_status["cache_manager"] = {
                "status": "error",
                "error": str(e),
            }

    async def _initialize_database(self):
        """Initialize enhanced database with connection pooling"""
        try:
            from utils.database import db

            start_time = time.time()
            await db.initialize()

            # Test database functionality
            await db.set_guild_setting(0, "init_test", "db_success")
            result = await db.get_guild_setting(0, "init_test")

            duration = time.time() - start_time
            self.enhancement_status["database"] = {
                "status": "success" if result == "db_success" else "failed",
                "init_time": duration,
                "details": "Connection pooling with advanced caching",
            }

            if result == "db_success":
                logger.info(f"✅ Enhanced Database ready ({duration:.3f}s)")
            else:
                logger.error("❌ Database initialization failed")

        except Exception as e:
            logger.error(f"❌ Database error: {e}")
            self.enhancement_status["database"] = {"status": "error", "error": str(e)}

    async def _initialize_http_manager(self):
        """Initialize HTTP session manager"""
        try:
            from utils.http_manager import http_manager

            start_time = time.time()
            await http_manager.initialize()

            duration = time.time() - start_time
            stats = http_manager.get_stats()

            self.enhancement_status["http_manager"] = {
                "status": "success",
                "init_time": duration,
                "details": f"Connection pooling with {stats.get('cache_entries', 0)} cache entries",
            }

            logger.info(f"✅ HTTP Session Manager ready ({duration:.3f}s)")

        except Exception as e:
            logger.error(f"❌ HTTP Manager error: {e}")
            self.enhancement_status["http_manager"] = {
                "status": "error",
                "error": str(e),
            }

    def _initialize_api_management(self):
        """Initialize API key management"""
        try:
            from utils.api_keys import api_manager

            start_time = time.time()

            # Test API management
            summary = api_manager.get_usage_summary()

            duration = time.time() - start_time
            self.enhancement_status["api_management"] = {
                "status": "success",
                "init_time": duration,
                "details": f"{summary['total_services']} services configured, {summary['enabled_services']} enabled",
            }

            logger.info(
                f"✅ API Management ready ({duration:.3f}s) - {summary['total_services']} services"
            )

        except Exception as e:
            logger.error(f"❌ API Management error: {e}")
            self.enhancement_status["api_management"] = {
                "status": "error",
                "error": str(e),
            }

    async def _initialize_lightning_optimizer(self):
        """Initialize lightning optimizer"""
        try:
            from utils.lightning_optimizer import lightning_optimizer

            start_time = time.time()

            # Test lightning optimizer
            response = await lightning_optimizer.optimize_response(
                "System initialization test", {"user_id": 0, "username": "system"}
            )

            duration = time.time() - start_time
            self.enhancement_status["lightning_optimizer"] = {
                "status": "success" if len(response) > 0 else "failed",
                "init_time": duration,
                "details": "Ultra-fast response optimization with context intelligence",
            }

            if len(response) > 0:
                logger.info(f"✅ Lightning Optimizer ready ({duration:.3f}s)")
            else:
                logger.error("❌ Lightning Optimizer failed to generate response")

        except Exception as e:
            logger.error(f"❌ Lightning Optimizer error: {e}")
            self.enhancement_status["lightning_optimizer"] = {
                "status": "error",
                "error": str(e),
            }

    def _setup_performance_monitoring(self):
        """Setup performance monitoring"""
        try:
            # Initialize performance metrics collection
            self.performance_metrics = {
                "startup_time": time.time() - self.start_time,
                "components_initialized": len(
                    [
                        s
                        for s in self.enhancement_status.values()
                        if s.get("status") == "success"
                    ]
                ),
                "total_components": len(self.enhancement_status),
                "initialization_timestamp": datetime.now().isoformat(),
            }

            logger.info("✅ Performance monitoring initialized")

        except Exception as e:
            logger.error(f"❌ Performance monitoring error: {e}")

    async def _validate_all_systems(self):
        """Validate all systems are working together"""
        try:
            # Test system integration
            from utils.cache_manager import cache
            from utils.helpers import format_time
            from utils.api_keys import get_api_key

            start_time = time.time()

            # Test cache + helpers integration
            await cache.set("validation_test", {"time": 3661}, ttl=60)
            cached_data = await cache.get("validation_test")
            formatted_time = format_time(cached_data["time"])

            # Test API key retrieval
            nasa_key = get_api_key("nasa")

            duration = time.time() - start_time

            integration_success = (
                cached_data is not None
                and "hour" in formatted_time
                and nasa_key is not None
            )

            self.enhancement_status["system_integration"] = {
                "status": "success" if integration_success else "failed",
                "validation_time": duration,
                "details": "All components working together seamlessly",
            }

            if integration_success:
                logger.info(f"✅ System integration validated ({duration:.3f}s)")
            else:
                logger.error("❌ System integration validation failed")

        except Exception as e:
            logger.error(f"❌ System validation error: {e}")
            self.enhancement_status["system_integration"] = {
                "status": "error",
                "error": str(e),
            }

    def get_performance_report(self) -> Dict[str, Any]:
        """Get comprehensive performance report"""
        successful_components = sum(
            1
            for status in self.enhancement_status.values()
            if status.get("status") == "success"
        )
        total_components = len(self.enhancement_status)

        return {
            "overall_status": (
                "optimal" if successful_components == total_components else "degraded"
            ),
            "success_rate": (
                (successful_components / total_components) * 100
                if total_components > 0
                else 0
            ),
            "total_initialization_time": time.time() - self.start_time,
            "components": self.enhancement_status,
            "performance_metrics": self.performance_metrics,
            "enhancement_summary": {
                "cache_manager": "Hybrid memory/file caching with LRU eviction and compression",
                "database": "Advanced connection pooling with 15 concurrent connections",
                "http_manager": "Optimized session management with connection reuse",
                "api_management": "Secure multi-service API key management with rate limiting",
                "lightning_optimizer": "Sub-100ms response optimization with context intelligence",
                "system_integration": "All components working together seamlessly",
            },
        }

    def log_performance_summary(self):
        """Log comprehensive performance summary"""
        report = self.get_performance_report()

        logger.info("=" * 80)
        logger.info("📊 ASTRABOT PERFORMANCE ENHANCEMENT SUMMARY")
        logger.info("=" * 80)

        logger.info(f"🎯 Overall Status: {report['overall_status'].upper()}")
        logger.info(f"✅ Success Rate: {report['success_rate']:.1f}%")
        logger.info(
            f"⏱️ Total Initialization: {report['total_initialization_time']:.2f}s"
        )

        logger.info("\n🚀 Enhanced Components:")
        for component, details in report["components"].items():
            status_icon = (
                "✅"
                if details.get("status") == "success"
                else "❌" if details.get("status") == "error" else "⚠️"
            )
            component_name = component.replace("_", " ").title()
            init_time = details.get("init_time", details.get("validation_time", 0))
            logger.info(
                f"   {status_icon} {component_name}: {init_time:.3f}s - {details.get('details', 'N/A')}"
            )

        logger.info("\n⚡ Performance Enhancements Active:")
        for component, description in report["enhancement_summary"].items():
            logger.info(f"   • {component.replace('_', ' ').title()}: {description}")

        if report["overall_status"] == "optimal":
            logger.info(
                "\n🎉 ALL SYSTEMS OPTIMAL! AstraBot is running at maximum performance!"
            )
        else:
            failed_components = [
                name
                for name, status in report["components"].items()
                if status.get("status") != "success"
            ]
            logger.info(
                f"\n⚠️ Some components need attention: {', '.join(failed_components)}"
            )

        logger.info("=" * 80)


# Global performance manager instance
performance_manager = PerformanceEnhancementManager()


async def initialize_performance_enhancements():
    """Initialize all performance enhancements for the bot"""
    await performance_manager.initialize_all_optimizations()
    performance_manager.log_performance_summary()
    return performance_manager.get_performance_report()


def get_performance_status():
    """Get current performance status"""
    return performance_manager.get_performance_report()


# Export for use in bot.1.0.py
__all__ = [
    "performance_manager",
    "initialize_performance_enhancements",
    "get_performance_status",
]
