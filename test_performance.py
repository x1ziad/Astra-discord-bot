#!/usr/bin/env python3
"""
Focused Performance Test for Astra Bot
Tests actual working functionality and performance metrics
"""

import asyncio
import aiohttp
import time
import psutil
import sys
import os
import json
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
import traceback

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

class FocusedTestSuite:
    """Focused test suite for working Astra Bot features"""
    
    def __init__(self):
        self.results = {}
        self.performance = {}
        self.start_time = time.time()
        self.start_memory = psutil.Process().memory_info().rss / 1024 / 1024
        
    async def run_tests(self):
        """Run focused performance tests"""
        print("🚀 Astra Bot - Focused Performance Test")
        print("=" * 70)
        print(f"📅 Started: {datetime.now().strftime('%H:%M:%S')}")
        print(f"💻 System: {psutil.cpu_count()} CPUs, {psutil.virtual_memory().total / (1024**3):.1f}GB RAM")
        print(f"💾 Initial Memory: {self.start_memory:.1f}MB")
        print("=" * 70)
        
        # Test suite
        tests = [
            ("🔧 Core Systems", self.test_core_systems),
            ("🗃️ Database Performance", self.test_database_performance),  
            ("🚀 Space API Performance", self.test_space_apis),
            ("🤖 AI Engine Performance", self.test_ai_performance),
            ("📊 System Performance", self.test_system_performance),
            ("🎯 End-to-End Tests", self.test_end_to_end)
        ]
        
        for test_name, test_func in tests:
            print(f"\n{test_name}")
            print("-" * 50)
            
            start = time.time()
            try:
                await test_func()
                duration = time.time() - start
                self.performance[test_name] = duration
                print(f"✅ Completed in {duration:.3f}s")
            except Exception as e:
                duration = time.time() - start
                self.performance[test_name] = duration
                print(f"❌ Failed in {duration:.3f}s: {e}")
                self.results[test_name] = {"error": str(e)}
        
        await self.generate_report()
    
    async def test_core_systems(self):
        """Test core system imports and initialization"""
        # Test imports with timing
        imports = [
            ("discord", "Discord.py"),
            ("aiohttp", "HTTP Client"),
            ("sqlite3", "Database"),
            ("config.enhanced_config", "Configuration"),
            ("ai.enhanced_conversation_engine", "AI Engine"),
            ("cogs.space", "Space Cog")
        ]
        
        for module, name in imports:
            start = time.time()
            try:
                __import__(module)
                duration = time.time() - start
                print(f"  ✅ {name}: {duration:.4f}s")
            except Exception as e:
                duration = time.time() - start
                print(f"  ❌ {name}: {duration:.4f}s - {e}")
        
        # Test configuration loading
        start = time.time()
        from config.enhanced_config import config_manager
        config_time = time.time() - start
        print(f"  ✅ Config loading: {config_time:.4f}s")
        
        # Test memory after imports
        current_memory = psutil.Process().memory_info().rss / 1024 / 1024
        memory_delta = current_memory - self.start_memory
        print(f"  📊 Memory after imports: {current_memory:.1f}MB (+{memory_delta:.1f}MB)")
    
    async def test_database_performance(self):
        """Test database operations with performance metrics"""
        db_path = Path("data/perf_test.db")
        db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Test database creation and operations
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Table creation
        start = time.time()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS perf_test (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                data TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        table_time = time.time() - start
        print(f"  ✅ Table creation: {table_time:.4f}s")
        
        # Bulk insert test
        test_data = [(i, f"Test data {i}") for i in range(5000)]
        
        start = time.time()
        cursor.executemany("INSERT INTO perf_test (user_id, data) VALUES (?, ?)", test_data)
        conn.commit()
        insert_time = time.time() - start
        ops_per_sec = len(test_data) / insert_time
        print(f"  ✅ Bulk insert ({len(test_data)} records): {insert_time:.4f}s ({ops_per_sec:.0f} ops/sec)")
        
        # Query performance test
        start = time.time()
        cursor.execute("SELECT COUNT(*) FROM perf_test")
        count = cursor.fetchone()[0]
        query_time = time.time() - start
        print(f"  ✅ Count query: {query_time:.4f}s ({count} records)")
        
        # Index creation and query
        start = time.time()
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_id ON perf_test(user_id)")
        index_time = time.time() - start
        
        start = time.time()
        cursor.execute("SELECT * FROM perf_test WHERE user_id < 100 LIMIT 50")
        results = cursor.fetchall()
        indexed_query_time = time.time() - start
        print(f"  ✅ Index creation: {index_time:.4f}s")
        print(f"  ✅ Indexed query: {indexed_query_time:.4f}s ({len(results)} results)")
        
        # Database size
        db_size = db_path.stat().st_size / 1024
        print(f"  📊 Database size: {db_size:.1f}KB")
        
        conn.close()
        db_path.unlink()  # Cleanup
        
        self.results["database"] = {
            "insert_ops_per_sec": ops_per_sec,
            "query_time_ms": query_time * 1000,
            "db_size_kb": db_size
        }
    
    async def test_space_apis(self):
        """Test space-related API performance"""
        from utils.http_client import get_session
        
        session = await get_session()
        
        apis = [
            {
                "name": "NASA APOD",
                "url": "https://api.nasa.gov/planetary/apod",
                "params": {"api_key": os.getenv("NASA_API_KEY", "DEMO_KEY")}
            },
            {
                "name": "ISS Location", 
                "url": "http://api.open-notify.org/iss-now.json",
                "params": {}
            },
            {
                "name": "Astronauts",
                "url": "http://api.open-notify.org/astros.json", 
                "params": {}
            }
        ]
        
        api_results = {}
        
        for api in apis:
            start = time.time()
            try:
                async with session.get(api["url"], params=api["params"], timeout=10) as response:
                    response_time = time.time() - start
                    if response.status == 200:
                        data = await response.json()
                        data_size = len(str(data))
                        print(f"  ✅ {api['name']}: {response_time:.3f}s ({data_size} bytes)")
                        api_results[api['name']] = {
                            "response_time": response_time,
                            "data_size": data_size,
                            "status": "success"
                        }
                    else:
                        print(f"  ⚠️ {api['name']}: {response_time:.3f}s (HTTP {response.status})")
                        api_results[api['name']] = {
                            "response_time": response_time,
                            "status": "warning",
                            "http_status": response.status
                        }
            except Exception as e:
                response_time = time.time() - start
                print(f"  ❌ {api['name']}: {response_time:.3f}s - {str(e)[:50]}")
                api_results[api['name']] = {
                    "response_time": response_time,
                    "status": "error",
                    "error": str(e)[:100]
                }
        
        self.results["apis"] = api_results
        
        # Test space cog initialization
        start = time.time()
        from cogs.space import Space
        
        class MockBot:
            def __init__(self):
                import logging
                self.logger = logging.getLogger("test")
                self.logger.setLevel(logging.WARNING)
        
        space_cog = Space(MockBot())
        init_time = time.time() - start
        facts_count = len(space_cog.space_facts)
        print(f"  ✅ Space cog init: {init_time:.4f}s ({facts_count} facts)")
        
        # Test rate limiting
        start = time.time()
        await space_cog._respect_rate_limit("test", 0.001)
        rate_limit_time = time.time() - start
        print(f"  ✅ Rate limiting: {rate_limit_time:.4f}s")
    
    async def test_ai_performance(self):
        """Test AI engine performance"""
        from ai.enhanced_conversation_engine import initialize_conversation_engine
        
        # Initialize AI engine
        start = time.time()
        ai_config = {"providers": {"fallback_enabled": True}}
        engine = initialize_conversation_engine(ai_config)
        init_time = time.time() - start
        print(f"  ✅ AI engine init: {init_time:.4f}s")
        
        # Test conversation processing
        test_messages = [
            "Hello, how are you?",
            "Tell me about space exploration",
            "What's the weather like on Mars?",
            "I'm feeling excited about astronomy!",
            "Can you explain black holes?"
        ]
        
        total_time = 0
        total_chars = 0
        
        for i, message in enumerate(test_messages):
            start = time.time()
            try:
                response = await engine.process_conversation(
                    message=message,
                    user_id=12345 + i,
                    guild_id=67890,
                    channel_id=11111,
                    context_data={}
                )
                process_time = time.time() - start
                total_time += process_time
                total_chars += len(response)
                print(f"  ✅ Message {i+1}: {process_time:.4f}s ({len(response)} chars)")
            except Exception as e:
                process_time = time.time() - start
                print(f"  ❌ Message {i+1}: {process_time:.4f}s - {str(e)[:50]}")
        
        avg_time = total_time / len(test_messages)
        avg_chars = total_chars / len(test_messages)
        print(f"  📊 Average: {avg_time:.4f}s per message ({avg_chars:.0f} chars)")
        
        # Test analytics
        start = time.time()
        try:
            analytics = await engine.get_conversation_analytics()
            analytics_time = time.time() - start
            print(f"  ✅ Analytics: {analytics_time:.4f}s")
        except Exception as e:
            analytics_time = time.time() - start
            print(f"  ❌ Analytics: {analytics_time:.4f}s - {str(e)[:50]}")
        
        self.results["ai"] = {
            "init_time": init_time,
            "avg_response_time": avg_time,
            "avg_response_chars": avg_chars,
            "analytics_time": analytics_time
        }
    
    async def test_system_performance(self):
        """Test system performance metrics"""
        # CPU usage test
        start = time.time()
        cpu_percent = psutil.cpu_percent(interval=0.5)
        cpu_time = time.time() - start
        print(f"  ✅ CPU usage: {cpu_percent}% (measured in {cpu_time:.3f}s)")
        
        # Memory usage
        memory = psutil.virtual_memory()
        process_memory = psutil.Process().memory_info().rss / 1024 / 1024
        memory_delta = process_memory - self.start_memory
        print(f"  ✅ System memory: {memory.percent}% used ({memory.available / (1024**3):.1f}GB available)")
        print(f"  ✅ Process memory: {process_memory:.1f}MB (+{memory_delta:.1f}MB from start)")
        
        # Disk I/O test
        test_file = Path("data/io_test.txt")
        test_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Write performance
        start = time.time()
        with open(test_file, 'w') as f:
            for i in range(1000):
                f.write(f"Performance test line {i}\n")
        write_time = time.time() - start
        
        # Read performance  
        start = time.time()
        with open(test_file, 'r') as f:
            lines = f.readlines()
        read_time = time.time() - start
        
        file_size = test_file.stat().st_size / 1024
        print(f"  ✅ File I/O: Write {write_time:.4f}s, Read {read_time:.4f}s ({file_size:.1f}KB)")
        
        test_file.unlink()  # Cleanup
        
        # Network connectivity test (simple)
        start = time.time()
        try:
            from utils.http_client import get_session
            session = await get_session()
            async with session.get("https://httpbin.org/status/200", timeout=5) as response:
                network_time = time.time() - start
                print(f"  ✅ Network: {network_time:.3f}s (status {response.status})")
        except Exception as e:
            network_time = time.time() - start
            print(f"  ❌ Network: {network_time:.3f}s - {str(e)[:50]}")
        
        self.results["system"] = {
            "cpu_percent": cpu_percent,
            "memory_percent": memory.percent,
            "process_memory_mb": process_memory,
            "memory_delta_mb": memory_delta,
            "write_time": write_time,
            "read_time": read_time,
            "network_time": network_time
        }
    
    async def test_end_to_end(self):
        """Test end-to-end functionality"""
        print("  🔄 Running end-to-end scenario...")
        
        # Simulate a user interaction flow
        start = time.time()
        
        # 1. Load configuration
        from config.enhanced_config import config_manager
        config_load_time = time.time()
        
        # 2. Initialize AI engine
        from ai.enhanced_conversation_engine import initialize_conversation_engine
        ai_config = config_manager.get_ai_config()
        engine = initialize_conversation_engine(ai_config)
        ai_init_time = time.time()
        
        # 3. Initialize space cog
        from cogs.space import Space
        
        class MockBot:
            def __init__(self):
                import logging
                self.logger = logging.getLogger("test")
                self.logger.setLevel(logging.WARNING)
        
        space_cog = Space(MockBot())
        space_init_time = time.time()
        
        # 4. Process a conversation
        response = await engine.process_conversation(
            message="Tell me a space fact and explain why space exploration is important",
            user_id=99999,
            guild_id=88888,
            channel_id=77777,
            context_data={"channel_type": "TextChannel"}
        )
        conversation_time = time.time()
        
        # 5. Get a space fact
        space_fact = space_cog.space_facts[0]
        fact_time = time.time()
        
        # 6. Get analytics
        analytics = await engine.get_conversation_analytics()
        analytics_time = time.time()
        
        total_time = analytics_time - start
        
        print(f"  ✅ Config load: {(config_load_time - start):.4f}s")
        print(f"  ✅ AI init: {(ai_init_time - config_load_time):.4f}s")
        print(f"  ✅ Space init: {(space_init_time - ai_init_time):.4f}s")
        print(f"  ✅ Conversation: {(conversation_time - space_init_time):.4f}s")
        print(f"  ✅ Space fact: {(fact_time - conversation_time):.4f}s")
        print(f"  ✅ Analytics: {(analytics_time - fact_time):.4f}s")
        print(f"  📊 Total E2E: {total_time:.4f}s")
        print(f"  📝 Response: {len(response)} characters")
        print(f"  📚 Space fact: {len(space_fact)} characters")
        
        self.results["e2e"] = {
            "total_time": total_time,
            "response_length": len(response),
            "fact_length": len(space_fact),
            "steps_completed": 6
        }
    
    async def generate_report(self):
        """Generate final performance report"""
        total_time = time.time() - self.start_time
        final_memory = psutil.Process().memory_info().rss / 1024 / 1024
        memory_delta = final_memory - self.start_memory
        
        print("\n" + "=" * 70)
        print("📊 PERFORMANCE REPORT")
        print("=" * 70)
        
        print(f"⏱️  Total test time: {total_time:.3f}s")
        print(f"💾 Memory usage: {self.start_memory:.1f}MB → {final_memory:.1f}MB (Δ{memory_delta:+.1f}MB)")
        
        # Performance summary
        if self.performance:
            fastest = min(self.performance.items(), key=lambda x: x[1])
            slowest = max(self.performance.items(), key=lambda x: x[1])
            print(f"⚡ Fastest: {fastest[0]} ({fastest[1]:.3f}s)")
            print(f"🐌 Slowest: {slowest[0]} ({slowest[1]:.3f}s)")
        
        # Key metrics
        print(f"\n🎯 Key Performance Metrics:")
        
        if "database" in self.results:
            db = self.results["database"]
            print(f"  🗃️ Database: {db.get('insert_ops_per_sec', 0):.0f} inserts/sec")
        
        if "ai" in self.results:
            ai = self.results["ai"]
            print(f"  🤖 AI responses: {ai.get('avg_response_time', 0):.3f}s average")
        
        if "apis" in self.results:
            successful_apis = len([api for api in self.results["apis"].values() if api.get("status") == "success"])
            total_apis = len(self.results["apis"])
            print(f"  🔗 API connectivity: {successful_apis}/{total_apis} working")
        
        if "e2e" in self.results:
            e2e = self.results["e2e"]
            print(f"  🎯 End-to-end: {e2e.get('total_time', 0):.3f}s complete flow")
        
        # Environment check
        print(f"\n🔧 Environment Status:")
        discord_token = os.getenv("DISCORD_TOKEN")
        if discord_token and discord_token != "YOUR_DISCORD_BOT_TOKEN_HERE":
            print(f"  ✅ Discord token: Configured")
            bot_ready = True
        else:
            print(f"  🚫 Discord token: Not configured")
            bot_ready = False
        
        nasa_key = os.getenv("NASA_API_KEY")
        if nasa_key and nasa_key != "DEMO_KEY":
            print(f"  ✅ NASA API: Custom key")
        else:
            print(f"  ⚠️ NASA API: Using DEMO_KEY (limited)")
        
        # Overall assessment
        print(f"\n🚀 Bot Status:")
        if bot_ready:
            print(f"  ✅ READY FOR DEPLOYMENT")
            print(f"  🎮 Run with: python bot.1.0.py")
        else:
            print(f"  ❌ NEEDS DISCORD TOKEN")
            print(f"  💡 Set DISCORD_TOKEN environment variable")
        
        print(f"\n📈 Performance Grade:")
        if memory_delta < 50 and total_time < 10:
            print(f"  🏆 EXCELLENT - Fast and efficient")
        elif memory_delta < 100 and total_time < 20:
            print(f"  ✅ GOOD - Well optimized")
        elif memory_delta < 200 and total_time < 30:
            print(f"  ⚠️ FAIR - Acceptable performance")
        else:
            print(f"  ❌ NEEDS OPTIMIZATION")
        
        # Save detailed report
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "execution_time": total_time,
            "memory_start_mb": self.start_memory,
            "memory_end_mb": final_memory,
            "memory_delta_mb": memory_delta,
            "performance_timings": self.performance,
            "detailed_results": self.results,
            "bot_ready": bot_ready
        }
        
        report_file = Path("data/performance_report.json")
        report_file.parent.mkdir(parents=True, exist_ok=True)
        with open(report_file, 'w') as f:
            json.dump(report_data, f, indent=2, default=str)
        
        print(f"📄 Detailed report: {report_file}")
        print("=" * 70)


async def main():
    """Run the focused performance test"""
    suite = FocusedTestSuite()
    await suite.run_tests()


if __name__ == "__main__":
    asyncio.run(main())
