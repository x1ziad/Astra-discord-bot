"""
Performance Benchmark and Load Testing for Astra Bot
Tests system performance under various load conditions
"""

import asyncio
import time
import statistics
import psutil
import gc
from datetime import datetime
from typing import List, Dict, Any
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from utils.database import db
from config.config_manager import config_manager
from utils.http_client import get_session
from logger.enhanced_logger import setup_enhanced_logger


class PerformanceBenchmark:
    """Comprehensive performance benchmark suite"""

    def __init__(self):
        self.logger = setup_enhanced_logger("Benchmark", "INFO")
        self.results = {}

    async def run_all_benchmarks(self):
        """Run all performance benchmarks"""
        print("=" * 80)
        print("⚡ ASTRA BOT PERFORMANCE BENCHMARK SUITE")
        print("=" * 80)
        print(f"📅 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()

        benchmarks = [
            ("🗄️ Database Performance", self.benchmark_database),
            ("🌐 HTTP Client Performance", self.benchmark_http_client),
            ("🔧 Config System Performance", self.benchmark_config_system),
            ("🧠 Memory Usage Analysis", self.benchmark_memory),
            ("⚡ Concurrent Operations", self.benchmark_concurrency),
            ("📊 System Limits Testing", self.benchmark_system_limits),
        ]

        for name, benchmark_func in benchmarks:
            print(f"Running {name}...")
            print("-" * 60)

            try:
                start_time = time.time()
                result = await benchmark_func()
                end_time = time.time()

                self.results[name] = {
                    "result": result,
                    "duration": end_time - start_time,
                    "timestamp": datetime.now().isoformat(),
                }

                print(f"✅ {name} completed ({end_time - start_time:.2f}s)")
                print()

            except Exception as e:
                print(f"❌ {name} failed: {e}")
                self.results[name] = {"error": str(e)}
                print()

        await self.generate_performance_report()

    async def benchmark_database(self) -> Dict[str, Any]:
        """Benchmark database operations"""
        await db.initialize()

        # Test different operation types
        operations = {
            "single_write": [],
            "single_read": [],
            "batch_write": [],
            "batch_read": [],
            "mixed_operations": [],
        }

        # Single write operations
        print("Testing single write operations...")
        for i in range(100):
            start = time.time()
            await db.set(
                "benchmark", f"test_{i}", {"value": i, "data": f"test_data_{i}"}
            )
            operations["single_write"].append(time.time() - start)

        # Single read operations
        print("Testing single read operations...")
        for i in range(100):
            start = time.time()
            await db.get("benchmark", f"test_{i}")
            operations["single_read"].append(time.time() - start)

        # Batch operations
        print("Testing batch operations...")
        batch_start = time.time()
        tasks = []
        for i in range(100, 200):
            tasks.append(db.set("benchmark", f"batch_{i}", {"batch": True, "id": i}))
        await asyncio.gather(*tasks)
        operations["batch_write"].append(time.time() - batch_start)

        batch_start = time.time()
        tasks = []
        for i in range(100, 200):
            tasks.append(db.get("benchmark", f"batch_{i}"))
        await asyncio.gather(*tasks)
        operations["batch_read"].append(time.time() - batch_start)

        # Mixed operations
        print("Testing mixed operations...")
        for cycle in range(10):
            start = time.time()
            # Mixed read/write operations
            await db.set("benchmark", f"mixed_{cycle}", {"cycle": cycle})
            await db.get("benchmark", f"mixed_{cycle}")
            await db.set("benchmark", f"mixed_{cycle}_update", {"updated": True})
            operations["mixed_operations"].append(time.time() - start)

        # Calculate statistics
        results = {}
        for op_type, times in operations.items():
            if times:
                results[op_type] = {
                    "avg_time_ms": statistics.mean(times) * 1000,
                    "min_time_ms": min(times) * 1000,
                    "max_time_ms": max(times) * 1000,
                    "ops_per_second": (
                        len(times) / sum(times)
                        if op_type.endswith("_write") or op_type.endswith("_read")
                        else 1 / statistics.mean(times)
                    ),
                    "total_operations": len(times),
                }

        # Cleanup
        for i in range(200):
            await db.delete("benchmark", f"test_{i}")
            await db.delete("benchmark", f"batch_{i}")
        for i in range(10):
            await db.delete("benchmark", f"mixed_{i}")
            await db.delete("benchmark", f"mixed_{i}_update")

        print(
            f"  📊 Single writes: {results['single_write']['ops_per_second']:.0f} ops/sec"
        )
        print(
            f"  📊 Single reads:  {results['single_read']['ops_per_second']:.0f} ops/sec"
        )
        print(
            f"  📊 Batch writes:  {100/results['batch_write']['avg_time_ms']*1000:.0f} ops/sec"
        )

        return results

    async def benchmark_http_client(self) -> Dict[str, Any]:
        """Benchmark HTTP client performance"""
        session = await get_session()

        # Test different request patterns
        results = {}

        # Sequential requests
        print("Testing sequential HTTP requests...")
        times = []
        for i in range(10):
            start = time.time()
            async with session.get("https://httpbin.org/get", timeout=5) as response:
                await response.text()
            times.append(time.time() - start)

        results["sequential_requests"] = {
            "avg_time_ms": statistics.mean(times) * 1000,
            "requests_per_second": len(times) / sum(times),
        }

        # Concurrent requests
        print("Testing concurrent HTTP requests...")
        start = time.time()
        tasks = []
        for i in range(20):
            task = session.get("https://httpbin.org/get", timeout=10)
            tasks.append(task)

        responses = await asyncio.gather(
            *[task.__aenter__() for task in tasks], return_exceptions=True
        )
        for response in responses:
            if hasattr(response, "__aexit__"):
                await response.__aexit__(None, None, None)

        total_time = time.time() - start
        results["concurrent_requests"] = {
            "total_time_s": total_time,
            "requests_per_second": 20 / total_time,
            "avg_time_per_request_ms": (total_time / 20) * 1000,
        }

        # Close session
        if not session.closed:
            await session.close()

        print(
            f"  📊 Sequential: {results['sequential_requests']['requests_per_second']:.1f} req/sec"
        )
        print(
            f"  📊 Concurrent: {results['concurrent_requests']['requests_per_second']:.1f} req/sec"
        )

        return results

    async def benchmark_config_system(self) -> Dict[str, Any]:
        """Benchmark configuration system"""
        results = {}

        # Config access speed
        print("Testing config access speed...")
        times = []
        for i in range(1000):
            start = time.time()
            config = config_manager.get_bot_config()
            _ = config.name
            _ = config.version
            _ = config.features
            times.append(time.time() - start)

        results["config_access"] = {
            "avg_time_ms": statistics.mean(times) * 1000,
            "accesses_per_second": len(times) / sum(times),
        }

        # Feature checking
        print("Testing feature checking speed...")
        times = []
        for i in range(1000):
            start = time.time()
            _ = config_manager.feature_enabled("ai_chat")
            _ = config_manager.feature_enabled("space_content")
            _ = config_manager.feature_enabled("analytics")
            times.append(time.time() - start)

        results["feature_checking"] = {
            "avg_time_ms": statistics.mean(times) * 1000,
            "checks_per_second": len(times) / sum(times),
        }

        print(
            f"  📊 Config access: {results['config_access']['accesses_per_second']:.0f} ops/sec"
        )
        print(
            f"  📊 Feature checks: {results['feature_checking']['checks_per_second']:.0f} ops/sec"
        )

        return results

    async def benchmark_memory(self) -> Dict[str, Any]:
        """Analyze memory usage patterns"""
        process = psutil.Process()

        # Initial memory
        initial_memory = process.memory_info().rss / 1024 / 1024

        # Create load
        print("Creating memory load...")
        large_objects = []
        for i in range(100):
            large_objects.append(
                {
                    "id": i,
                    "data": "x" * 1000,  # 1KB per object
                    "nested": {"more": "data" * 100},
                }
            )

        peak_memory = process.memory_info().rss / 1024 / 1024

        # Cleanup and measure
        del large_objects
        gc.collect()

        final_memory = process.memory_info().rss / 1024 / 1024

        results = {
            "initial_memory_mb": initial_memory,
            "peak_memory_mb": peak_memory,
            "final_memory_mb": final_memory,
            "memory_increase_mb": peak_memory - initial_memory,
            "memory_recovered_mb": peak_memory - final_memory,
            "gc_efficiency_percent": (
                ((peak_memory - final_memory) / (peak_memory - initial_memory) * 100)
                if peak_memory > initial_memory
                else 0
            ),
        }

        print(f"  📊 Initial: {initial_memory:.1f} MB")
        print(f"  📊 Peak: {peak_memory:.1f} MB")
        print(f"  📊 Final: {final_memory:.1f} MB")
        print(f"  📊 GC Efficiency: {results['gc_efficiency_percent']:.1f}%")

        return results

    async def benchmark_concurrency(self) -> Dict[str, Any]:
        """Test concurrent operations performance"""
        results = {}

        # Test different concurrency levels
        for concurrency in [10, 50, 100]:
            print(f"Testing {concurrency} concurrent tasks...")

            async def dummy_task(task_id):
                # Simulate mixed workload
                await asyncio.sleep(0.001)  # Simulate I/O
                _ = [i**2 for i in range(100)]  # Simulate CPU work
                return task_id

            start = time.time()
            tasks = [dummy_task(i) for i in range(concurrency)]
            results_list = await asyncio.gather(*tasks)
            total_time = time.time() - start

            results[f"concurrency_{concurrency}"] = {
                "total_time_s": total_time,
                "tasks_per_second": concurrency / total_time,
                "avg_task_time_ms": (total_time / concurrency) * 1000,
                "completed_tasks": len(results_list),
            }

            print(f"    📊 {concurrency} tasks: {concurrency/total_time:.0f} tasks/sec")

        return results

    async def benchmark_system_limits(self) -> Dict[str, Any]:
        """Test system limits and resource usage"""
        process = psutil.Process()

        results = {
            "system_info": {
                "cpu_count": psutil.cpu_count(),
                "memory_total_gb": psutil.virtual_memory().total / (1024**3),
                "python_version": sys.version.split()[0],
            }
        }

        # Test task creation limits
        print("Testing task creation limits...")
        max_tasks = 0
        try:
            tasks = []
            for i in range(10000):  # Try up to 10k tasks
                task = asyncio.create_task(asyncio.sleep(0.1))
                tasks.append(task)
                max_tasks = i + 1

                if i % 1000 == 0:
                    memory_mb = process.memory_info().rss / 1024 / 1024
                    if memory_mb > 200:  # Stop if memory exceeds 200MB
                        break

            # Cancel all tasks
            for task in tasks:
                task.cancel()
            await asyncio.gather(*tasks, return_exceptions=True)

        except Exception as e:
            self.logger.warning(f"Task limit reached at {max_tasks}: {e}")

        results["task_limits"] = {
            "max_tasks_created": max_tasks,
            "memory_at_limit_mb": process.memory_info().rss / 1024 / 1024,
        }

        # Connection pool test
        print("Testing connection handling...")
        try:
            import aiohttp

            session = aiohttp.ClientSession()

            # Test connection pooling
            start = time.time()
            tasks = []
            for i in range(50):
                task = session.get("https://httpbin.org/get", timeout=1)
                tasks.append(task)

            responses = await asyncio.gather(
                *[task.__aenter__() for task in tasks], return_exceptions=True
            )
            for response in responses:
                if hasattr(response, "__aexit__"):
                    await response.__aexit__(None, None, None)

            connection_time = time.time() - start
            await session.close()

            results["connection_pooling"] = {
                "concurrent_connections": 50,
                "total_time_s": connection_time,
                "connections_per_second": 50 / connection_time,
            }

        except Exception as e:
            results["connection_pooling"] = {"error": str(e)}

        print(f"  📊 Max tasks: {max_tasks}")
        print(
            f"  📊 Memory at limit: {results['task_limits']['memory_at_limit_mb']:.1f} MB"
        )

        return results

    async def generate_performance_report(self):
        """Generate comprehensive performance report"""
        print("=" * 80)
        print("📊 PERFORMANCE BENCHMARK REPORT")
        print("=" * 80)

        process = psutil.Process()

        print(f"📅 Report Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(
            f"💻 System: {psutil.cpu_count()} CPU, {psutil.virtual_memory().total/(1024**3):.1f}GB RAM"
        )
        print(f"🐍 Python: {sys.version.split()[0]}")
        print(f"📊 Final Memory: {process.memory_info().rss / 1024 / 1024:.1f} MB")
        print()

        # Summary of key metrics
        print("🎯 KEY PERFORMANCE METRICS:")
        print("-" * 60)

        for benchmark_name, data in self.results.items():
            if "error" in data:
                print(f"❌ {benchmark_name}: FAILED - {data['error']}")
            else:
                print(f"✅ {benchmark_name}: {data['duration']:.2f}s")

        print()

        # Performance recommendations
        print("💡 PERFORMANCE RECOMMENDATIONS:")
        print("-" * 60)

        # Database performance
        if "🗄️ Database Performance" in self.results:
            db_result = self.results["🗄️ Database Performance"]["result"]
            if db_result.get("single_write", {}).get("ops_per_second", 0) < 100:
                print("⚠️ Database write performance is below optimal (< 100 ops/sec)")
            else:
                print("✅ Database performance is excellent")

        # Memory usage
        memory_mb = process.memory_info().rss / 1024 / 1024
        if memory_mb > 100:
            print(f"⚠️ Memory usage is high ({memory_mb:.1f} MB)")
        else:
            print("✅ Memory usage is optimal")

        # HTTP performance
        if "🌐 HTTP Client Performance" in self.results:
            http_result = self.results["🌐 HTTP Client Performance"]["result"]
            if (
                http_result.get("sequential_requests", {}).get("requests_per_second", 0)
                < 1
            ):
                print("⚠️ HTTP performance may be limited by network latency")
            else:
                print("✅ HTTP client performance is good")

        print()
        print("🎉 Performance benchmark completed successfully!")
        print("=" * 80)


async def main():
    """Run performance benchmark suite"""
    try:
        benchmark = PerformanceBenchmark()
        await benchmark.run_all_benchmarks()
        return 0
    except KeyboardInterrupt:
        print("\n🛑 Benchmark interrupted by user")
        return 1
    except Exception as e:
        print(f"\n💥 Benchmark crashed: {e}")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
