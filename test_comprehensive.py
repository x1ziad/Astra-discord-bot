#!/usr/bin/env python3
"""
Comprehensive Performance and Feature Test Suite for Astra Bot
Tests all components: Space features, AI engine, database, configuration, and performance
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
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import traceback

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

class AstraBotTestSuite:
    """Comprehensive test suite for Astra Bot"""
    
    def __init__(self):
        self.test_results: Dict[str, Any] = {}
        self.performance_metrics: Dict[str, float] = {}
        self.start_time = time.time()
        self.memory_usage = {}
        
    async def run_all_tests(self):
        """Run complete test suite"""
        print("🚀 Astra Bot - Comprehensive Test Suite")
        print("=" * 80)
        print(f"📅 Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🖥️  System: {psutil.cpu_count()} CPUs, {psutil.virtual_memory().total / (1024**3):.1f}GB RAM")
        print("=" * 80)
        
        # Track initial memory
        self.memory_usage['start'] = psutil.Process().memory_info().rss / 1024 / 1024
        
        # Test categories
        test_categories = [
            ("🔧 System & Dependencies", self.test_system_dependencies),
            ("⚙️ Configuration System", self.test_configuration_system),
            ("🗃️ Database Operations", self.test_database_operations),
            ("🚀 Space Features", self.test_space_features),
            ("🤖 AI Conversation Engine", self.test_ai_engine),
            ("📊 Performance Metrics", self.test_performance_metrics),
            ("🔗 API Connectivity", self.test_api_connectivity),
            ("💾 Memory & Resources", self.test_memory_usage),
            ("🏗️ Bot Architecture", self.test_bot_architecture),
            ("🎯 Integration Tests", self.test_integrations)
        ]
        
        for category_name, test_func in test_categories:
            print(f"\n{category_name}")
            print("-" * 60)
            
            start_time = time.time()
            try:
                await test_func()
                execution_time = time.time() - start_time
                self.performance_metrics[category_name] = execution_time
                print(f"✅ {category_name} completed in {execution_time:.2f}s")
            except Exception as e:
                execution_time = time.time() - start_time
                self.performance_metrics[category_name] = execution_time
                print(f"❌ {category_name} failed in {execution_time:.2f}s: {e}")
                self.test_results[category_name] = {"status": "failed", "error": str(e)}
        
        # Final summary
        await self.generate_final_report()
    
    async def test_system_dependencies(self):
        """Test system dependencies and Python packages"""
        print("  📦 Checking Python packages...")
        
        required_packages = [
            ("discord.py", "discord"),
            ("aiohttp", "aiohttp"),
            ("sqlite3", "sqlite3"),
            ("json", "json"),
            ("pathlib", "pathlib"),
            ("datetime", "datetime"),
            ("asyncio", "asyncio"),
            ("logging", "logging"),
            ("os", "os"),
            ("sys", "sys"),
            ("typing", "typing"),
            ("psutil", "psutil")
        ]
        
        optional_packages = [
            ("openai", "openai"),
            ("anthropic", "anthropic"),
            ("sklearn", "sklearn"),
            ("numpy", "numpy"),
            ("joblib", "joblib"),
            ("python-dotenv", "dotenv")
        ]
        
        required_status = {}
        optional_status = {}
        
        # Test required packages
        for package_name, import_name in required_packages:
            try:
                __import__(import_name)
                required_status[package_name] = "✅ Available"
                print(f"    ✅ {package_name}: Available")
            except ImportError:
                required_status[package_name] = "❌ Missing"
                print(f"    ❌ {package_name}: Missing (CRITICAL)")
        
        # Test optional packages
        for package_name, import_name in optional_packages:
            try:
                __import__(import_name)
                optional_status[package_name] = "✅ Available"
                print(f"    ✅ {package_name}: Available")
            except ImportError:
                optional_status[package_name] = "⭕ Optional"
                print(f"    ⭕ {package_name}: Optional (features may be limited)")
        
        # Test environment variables
        print("  🔐 Checking environment variables...")
        env_vars = {
            "DISCORD_TOKEN": os.getenv("DISCORD_TOKEN"),
            "NASA_API_KEY": os.getenv("NASA_API_KEY"),
            "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
            "ANTHROPIC_API_KEY": os.getenv("ANTHROPIC_API_KEY"),
            "NOTION_TOKEN": os.getenv("NOTION_TOKEN"),
            "NOTION_DATABASE_ID": os.getenv("NOTION_DATABASE_ID")
        }
        
        for var, value in env_vars.items():
            if var == "DISCORD_TOKEN":
                if value and value != "YOUR_DISCORD_BOT_TOKEN_HERE":
                    print(f"    ✅ {var}: Configured")
                else:
                    print(f"    🚫 {var}: Required but not set")
            elif var == "NASA_API_KEY":
                if value and value != "DEMO_KEY":
                    print(f"    ✅ {var}: Custom key configured")
                else:
                    print(f"    ⚠️ {var}: Using DEMO_KEY (limited)")
            else:
                if value:
                    print(f"    ✅ {var}: Configured")
                else:
                    print(f"    ⭕ {var}: Optional - not set")
        
        self.test_results["dependencies"] = {
            "required": required_status,
            "optional": optional_status,
            "environment": env_vars
        }
    
    async def test_configuration_system(self):
        """Test enhanced configuration system"""
        print("  ⚙️ Testing configuration loading...")
        
        try:
            from config.enhanced_config import config_manager, feature_enabled
            print("    ✅ Configuration module imported")
            
            # Test basic configuration access
            config_sections = ["discord", "database", "ai", "features", "performance"]
            for section in config_sections:
                config_data = config_manager.get(section, {})
                if config_data:
                    print(f"    ✅ {section} config: Loaded ({len(config_data)} settings)")
                else:
                    print(f"    ⚠️ {section} config: Empty or missing")
            
            # Test color system
            colors = ["space", "error", "success", "warning", "info"]
            for color in colors:
                color_value = config_manager.get_color(color)
                print(f"    ✅ Color '{color}': {hex(color_value)}")
            
            # Test feature flags
            features = ["enable_ai", "enable_moderation", "enable_analytics"]
            for feature in features:
                is_enabled = config_manager.is_feature_enabled(feature)
                print(f"    ✅ Feature '{feature}': {'Enabled' if is_enabled else 'Disabled'}")
            
            # Test configuration validation
            is_valid = config_manager.validate_config()
            print(f"    ✅ Configuration validation: {'Passed' if is_valid else 'Failed'}")
            
            self.test_results["configuration"] = {"status": "success", "sections": len(config_sections)}
            
        except Exception as e:
            print(f"    ❌ Configuration test failed: {e}")
            self.test_results["configuration"] = {"status": "failed", "error": str(e)}
    
    async def test_database_operations(self):
        """Test database operations and performance"""
        print("  🗃️ Testing database operations...")
        
        try:
            # Test database file creation
            db_path = Path("data/test_astra.db")
            db_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Create test database
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            
            # Test table creation
            start_time = time.time()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS test_conversations (
                    id INTEGER PRIMARY KEY,
                    user_id INTEGER,
                    message TEXT,
                    response TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            table_creation_time = time.time() - start_time
            print(f"    ✅ Table creation: {table_creation_time:.4f}s")
            
            # Test bulk insert performance
            test_data = [(i, f"Test message {i}", f"Test response {i}") for i in range(1000)]
            
            start_time = time.time()
            cursor.executemany(
                "INSERT INTO test_conversations (user_id, message, response) VALUES (?, ?, ?)",
                test_data
            )
            conn.commit()
            insert_time = time.time() - start_time
            print(f"    ✅ Bulk insert (1000 records): {insert_time:.4f}s ({1000/insert_time:.0f} records/sec)")
            
            # Test query performance
            start_time = time.time()
            cursor.execute("SELECT COUNT(*) FROM test_conversations")
            count = cursor.fetchone()[0]
            query_time = time.time() - start_time
            print(f"    ✅ Count query: {query_time:.4f}s ({count} records)")
            
            # Test indexed query
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_id ON test_conversations(user_id)")
            start_time = time.time()
            cursor.execute("SELECT * FROM test_conversations WHERE user_id = ? LIMIT 10", (500,))
            results = cursor.fetchall()
            indexed_query_time = time.time() - start_time
            print(f"    ✅ Indexed query: {indexed_query_time:.4f}s ({len(results)} results)")
            
            # Test database size
            db_size = db_path.stat().st_size / 1024  # KB
            print(f"    ✅ Database size: {db_size:.1f} KB")
            
            # Cleanup
            conn.close()
            db_path.unlink()  # Remove test database
            
            self.test_results["database"] = {
                "status": "success",
                "table_creation_time": table_creation_time,
                "insert_performance": f"{1000/insert_time:.0f} records/sec",
                "query_time": query_time,
                "db_size_kb": db_size
            }
            
        except Exception as e:
            print(f"    ❌ Database test failed: {e}")
            self.test_results["database"] = {"status": "failed", "error": str(e)}
    
    async def test_space_features(self):
        """Test all space-related features"""
        print("  🚀 Testing space features...")
        
        try:
            from cogs.space import Space
            from utils.http_client import get_session
            
            # Mock bot for testing
            class MockBot:
                def __init__(self):
                    import logging
                    self.logger = logging.getLogger("test")
                    self.logger.setLevel(logging.WARNING)  # Reduce noise
            
            # Initialize space cog
            start_time = time.time()
            mock_bot = MockBot()
            space_cog = Space(mock_bot)
            init_time = time.time() - start_time
            print(f"    ✅ Space cog initialization: {init_time:.4f}s")
            
            # Test space facts
            facts_count = len(space_cog.space_facts)
            print(f"    ✅ Space facts loaded: {facts_count} facts")
            
            # Test NASA API key configuration
            nasa_key = space_cog.nasa_api_key
            key_type = "Custom" if nasa_key != "DEMO_KEY" else "DEMO_KEY"
            print(f"    ✅ NASA API key: {key_type}")
            
            # Test rate limiting
            start_time = time.time()
            await space_cog._respect_rate_limit("test", 0.1)
            rate_limit_time = time.time() - start_time
            print(f"    ✅ Rate limiting: {rate_limit_time:.4f}s")
            
            # Test space facts retrieval performance
            start_time = time.time()
            for _ in range(100):
                fact = space_cog.space_facts[0]  # Access first fact
            fact_access_time = time.time() - start_time
            print(f"    ✅ Fact access (100 iterations): {fact_access_time:.4f}s")
            
            # Test topic extraction
            test_messages = [
                "I love space and astronomy",
                "Stellaris is a great game",
                "The ISS is amazing",
                "Mars colonization",
                "Black holes are fascinating"
            ]
            
            start_time = time.time()
            total_topics = 0
            for message in test_messages:
                topics = await space_cog._extract_message_topics(message)
                total_topics += len(topics)
            topic_extraction_time = time.time() - start_time
            print(f"    ✅ Topic extraction ({len(test_messages)} messages): {topic_extraction_time:.4f}s ({total_topics} topics)")
            
            self.test_results["space_features"] = {
                "status": "success",
                "facts_count": facts_count,
                "init_time": init_time,
                "nasa_key_type": key_type,
                "topic_extraction_time": topic_extraction_time
            }
            
        except Exception as e:
            print(f"    ❌ Space features test failed: {e}")
            self.test_results["space_features"] = {"status": "failed", "error": str(e)}
    
    async def test_ai_engine(self):
        """Test AI conversation engine performance"""
        print("  🤖 Testing AI conversation engine...")
        
        try:
            from ai.enhanced_conversation_engine import (
                EnhancedAIConversationEngine,
                get_conversation_engine,
                initialize_conversation_engine
            )
            
            # Test engine initialization
            start_time = time.time()
            ai_config = {"providers": {"fallback_enabled": True}}
            engine = initialize_conversation_engine(ai_config)
            init_time = time.time() - start_time
            print(f"    ✅ AI engine initialization: {init_time:.4f}s")
            
            # Test sentiment analysis
            test_messages = [
                "I'm so excited about space exploration!",
                "I'm confused about black holes",
                "This is frustrating",
                "That's amazing news!",
                "I feel neutral about this"
            ]
            
            start_time = time.time()
            sentiments = []
            for message in test_messages:
                sentiment = await engine.analyze_sentiment(message)
                sentiments.append(sentiment)
            sentiment_time = time.time() - start_time
            print(f"    ✅ Sentiment analysis ({len(test_messages)} messages): {sentiment_time:.4f}s")
            
            # Test topic detection
            start_time = time.time()
            topics_detected = []
            for message in test_messages:
                topics = await engine.detect_topics(message)
                topics_detected.extend(topics)
            topic_time = time.time() - start_time
            print(f"    ✅ Topic detection: {topic_time:.4f}s ({len(set(topics_detected))} unique topics)")
            
            # Test conversation processing
            start_time = time.time()
            response = await engine.process_conversation(
                message="Hello! Tell me about space",
                user_id=12345,
                guild_id=67890,
                channel_id=11111,
                context_data={}
            )
            conversation_time = time.time() - start_time
            print(f"    ✅ Conversation processing: {conversation_time:.4f}s")
            print(f"    ✅ Response length: {len(response)} characters")
            
            # Test analytics
            start_time = time.time()
            analytics = await engine.get_conversation_analytics()
            analytics_time = time.time() - start_time
            print(f"    ✅ Analytics generation: {analytics_time:.4f}s")
            
            # Test personality traits loading
            personality_count = len(engine.personality_traits.get('core_traits', []))
            print(f"    ✅ Personality traits: {personality_count} traits loaded")
            
            self.test_results["ai_engine"] = {
                "status": "success",
                "init_time": init_time,
                "sentiment_analysis_time": sentiment_time,
                "topic_detection_time": topic_time,
                "conversation_time": conversation_time,
                "response_length": len(response),
                "personality_traits": personality_count
            }
            
        except Exception as e:
            print(f"    ❌ AI engine test failed: {e}")
            self.test_results["ai_engine"] = {"status": "failed", "error": str(e)}
    
    async def test_performance_metrics(self):
        """Test system performance metrics"""
        print("  📊 Testing performance metrics...")
        
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        print(f"    ✅ CPU usage: {cpu_percent}%")
        
        # Memory usage
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        memory_available_gb = memory.available / (1024**3)
        print(f"    ✅ Memory usage: {memory_percent}% ({memory_available_gb:.1f}GB available)")
        
        # Disk usage
        disk = psutil.disk_usage('/')
        disk_percent = disk.percent
        disk_free_gb = disk.free / (1024**3)
        print(f"    ✅ Disk usage: {disk_percent}% ({disk_free_gb:.1f}GB free)")
        
        # Process memory
        process = psutil.Process()
        process_memory_mb = process.memory_info().rss / 1024 / 1024
        print(f"    ✅ Process memory: {process_memory_mb:.1f}MB")
        
        # Test file I/O performance
        test_file = Path("data/performance_test.txt")
        test_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Write test
        start_time = time.time()
        with open(test_file, 'w') as f:
            for i in range(10000):
                f.write(f"Test line {i}\n")
        write_time = time.time() - start_time
        
        # Read test
        start_time = time.time()
        with open(test_file, 'r') as f:
            lines = f.readlines()
        read_time = time.time() - start_time
        
        print(f"    ✅ File I/O: Write {write_time:.4f}s, Read {read_time:.4f}s ({len(lines)} lines)")
        
        # Cleanup
        test_file.unlink()
        
        self.test_results["performance"] = {
            "cpu_percent": cpu_percent,
            "memory_percent": memory_percent,
            "disk_percent": disk_percent,
            "process_memory_mb": process_memory_mb,
            "file_write_time": write_time,
            "file_read_time": read_time
        }
    
    async def test_api_connectivity(self):
        """Test external API connectivity and performance"""
        print("  🔗 Testing API connectivity...")
        
        apis_to_test = [
            {
                "name": "NASA APOD",
                "url": "https://api.nasa.gov/planetary/apod",
                "params": {"api_key": os.getenv("NASA_API_KEY", "DEMO_KEY")},
                "timeout": 10
            },
            {
                "name": "ISS Location",
                "url": "http://api.open-notify.org/iss-now.json",
                "params": {},
                "timeout": 10
            },
            {
                "name": "Astronauts in Space",
                "url": "http://api.open-notify.org/astros.json",
                "params": {},
                "timeout": 10
            }
        ]
        
        try:
            from utils.http_client import get_session
            session = await get_session()
            
            api_results = {}
            
            for api in apis_to_test:
                start_time = time.time()
                try:
                    async with session.get(
                        api["url"], 
                        params=api["params"], 
                        timeout=api["timeout"]
                    ) as response:
                        response_time = time.time() - start_time
                        status = response.status
                        
                        if status == 200:
                            data = await response.json()
                            data_size = len(str(data))
                            print(f"    ✅ {api['name']}: {response_time:.3f}s ({status}) {data_size} bytes")
                            api_results[api['name']] = {
                                "status": "success",
                                "response_time": response_time,
                                "http_status": status,
                                "data_size": data_size
                            }
                        else:
                            print(f"    ⚠️ {api['name']}: {response_time:.3f}s ({status})")
                            api_results[api['name']] = {
                                "status": "warning", 
                                "response_time": response_time,
                                "http_status": status
                            }
                            
                except asyncio.TimeoutError:
                    response_time = time.time() - start_time
                    print(f"    ❌ {api['name']}: Timeout after {response_time:.3f}s")
                    api_results[api['name']] = {
                        "status": "timeout",
                        "response_time": response_time
                    }
                except Exception as e:
                    response_time = time.time() - start_time
                    print(f"    ❌ {api['name']}: Error after {response_time:.3f}s - {e}")
                    api_results[api['name']] = {
                        "status": "error",
                        "response_time": response_time,
                        "error": str(e)
                    }
            
            self.test_results["api_connectivity"] = api_results
            
        except Exception as e:
            print(f"    ❌ API connectivity test failed: {e}")
            self.test_results["api_connectivity"] = {"status": "failed", "error": str(e)}
    
    async def test_memory_usage(self):
        """Test memory usage and resource management"""
        print("  💾 Testing memory usage...")
        
        # Track memory at different points
        current_memory = psutil.Process().memory_info().rss / 1024 / 1024
        memory_delta = current_memory - self.memory_usage['start']
        
        print(f"    ✅ Initial memory: {self.memory_usage['start']:.1f}MB")
        print(f"    ✅ Current memory: {current_memory:.1f}MB")
        print(f"    ✅ Memory delta: {memory_delta:+.1f}MB")
        
        # Test memory allocation/deallocation
        start_time = time.time()
        test_data = []
        for i in range(10000):
            test_data.append(f"Test data {i}" * 100)  # Create some data
        
        peak_memory = psutil.Process().memory_info().rss / 1024 / 1024
        
        # Clear the data
        test_data.clear()
        test_data = None
        
        end_memory = psutil.Process().memory_info().rss / 1024 / 1024
        allocation_time = time.time() - start_time
        
        print(f"    ✅ Peak memory during allocation: {peak_memory:.1f}MB")
        print(f"    ✅ Memory after cleanup: {end_memory:.1f}MB")
        print(f"    ✅ Allocation/cleanup time: {allocation_time:.3f}s")
        
        self.memory_usage['current'] = current_memory
        self.memory_usage['peak'] = peak_memory
        self.memory_usage['delta'] = memory_delta
        
        self.test_results["memory"] = {
            "initial_mb": self.memory_usage['start'],
            "current_mb": current_memory,
            "peak_mb": peak_memory,
            "delta_mb": memory_delta,
            "allocation_time": allocation_time
        }
    
    async def test_bot_architecture(self):
        """Test bot architecture and module loading"""
        print("  🏗️ Testing bot architecture...")
        
        try:
            # Test module imports
            modules_to_test = [
                ("config.enhanced_config", "Enhanced configuration"),
                ("ai.enhanced_conversation_engine", "AI conversation engine"),
                ("cogs.space", "Space cog"),
                ("cogs.advanced_ai", "Advanced AI cog"),
                ("utils.http_client", "HTTP client"),
                ("logger.logger", "Logger"),
            ]
            
            import_times = {}
            for module_name, description in modules_to_test:
                start_time = time.time()
                try:
                    __import__(module_name)
                    import_time = time.time() - start_time
                    import_times[module_name] = import_time
                    print(f"    ✅ {description}: {import_time:.4f}s")
                except Exception as e:
                    import_time = time.time() - start_time
                    import_times[module_name] = import_time
                    print(f"    ❌ {description}: Failed in {import_time:.4f}s - {e}")
            
            # Test data directory structure
            required_dirs = ["data", "data/space", "data/conversations", "data/analytics"]
            for dir_path in required_dirs:
                path = Path(dir_path)
                if path.exists():
                    print(f"    ✅ Directory {dir_path}: Exists")
                else:
                    path.mkdir(parents=True, exist_ok=True)
                    print(f"    ✅ Directory {dir_path}: Created")
            
            # Test configuration file
            config_file = Path("config.json")
            if config_file.exists():
                file_size = config_file.stat().st_size
                print(f"    ✅ Configuration file: {file_size} bytes")
            else:
                print(f"    ⚠️ Configuration file: Not found (using defaults)")
            
            self.test_results["architecture"] = {
                "status": "success",
                "import_times": import_times,
                "total_import_time": sum(import_times.values())
            }
            
        except Exception as e:
            print(f"    ❌ Architecture test failed: {e}")
            self.test_results["architecture"] = {"status": "failed", "error": str(e)}
    
    async def test_integrations(self):
        """Test feature integrations and end-to-end functionality"""
        print("  🎯 Testing integrations...")
        
        try:
            # Test configuration + AI engine integration
            start_time = time.time()
            from config.enhanced_config import config_manager
            from ai.enhanced_conversation_engine import initialize_conversation_engine
            
            ai_config = config_manager.get_ai_config()
            engine = initialize_conversation_engine(ai_config)
            integration_time = time.time() - start_time
            print(f"    ✅ Config + AI integration: {integration_time:.4f}s")
            
            # Test space cog + configuration integration
            start_time = time.time()
            from cogs.space import Space
            
            class MockBot:
                def __init__(self):
                    import logging
                    self.logger = logging.getLogger("test")
                    self.logger.setLevel(logging.WARNING)
            
            space_cog = Space(MockBot())
            space_color = config_manager.get_color("space")
            space_integration_time = time.time() - start_time
            print(f"    ✅ Space + Config integration: {space_integration_time:.4f}s")
            
            # Test end-to-end conversation flow
            start_time = time.time()
            response = await engine.process_conversation(
                message="Tell me about the International Space Station",
                user_id=12345,
                guild_id=67890,
                channel_id=11111,
                context_data={"channel_type": "TextChannel"}
            )
            e2e_time = time.time() - start_time
            print(f"    ✅ End-to-end conversation: {e2e_time:.4f}s ({len(response)} chars)")
            
            # Test analytics integration
            start_time = time.time()
            analytics = await engine.get_conversation_analytics()
            analytics_integration_time = time.time() - start_time
            print(f"    ✅ Analytics integration: {analytics_integration_time:.4f}s")
            
            self.test_results["integrations"] = {
                "status": "success",
                "config_ai_time": integration_time,
                "space_config_time": space_integration_time,
                "e2e_conversation_time": e2e_time,
                "analytics_time": analytics_integration_time,
                "response_length": len(response)
            }
            
        except Exception as e:
            print(f"    ❌ Integration test failed: {e}")
            self.test_results["integrations"] = {"status": "failed", "error": str(e)}
    
    async def generate_final_report(self):
        """Generate comprehensive final report"""
        total_time = time.time() - self.start_time
        final_memory = psutil.Process().memory_info().rss / 1024 / 1024
        
        print("\n" + "=" * 80)
        print("📊 FINAL TEST REPORT")
        print("=" * 80)
        
        # Summary stats
        total_tests = len(self.test_results)
        successful_tests = len([r for r in self.test_results.values() if r.get("status") == "success"])
        failed_tests = total_tests - successful_tests
        
        print(f"⏱️  Total execution time: {total_time:.2f}s")
        print(f"📈 Tests completed: {total_tests}")
        print(f"✅ Successful: {successful_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"🎯 Success rate: {(successful_tests/total_tests)*100:.1f}%")
        
        # Performance summary
        print(f"\n📊 Performance Summary:")
        print(f"💾 Memory usage: {self.memory_usage['start']:.1f}MB → {final_memory:.1f}MB (Δ{final_memory-self.memory_usage['start']:+.1f}MB)")
        
        # Fastest/slowest operations
        if self.performance_metrics:
            fastest = min(self.performance_metrics.items(), key=lambda x: x[1])
            slowest = max(self.performance_metrics.items(), key=lambda x: x[1])
            print(f"⚡ Fastest operation: {fastest[0]} ({fastest[1]:.3f}s)")
            print(f"🐌 Slowest operation: {slowest[0]} ({slowest[1]:.3f}s)")
        
        # Feature status
        print(f"\n🚀 Feature Status:")
        
        # Space features
        space_status = self.test_results.get("space_features", {}).get("status", "unknown")
        space_icon = "✅" if space_status == "success" else "❌"
        print(f"{space_icon} Space Features: {space_status.title()}")
        
        # AI features
        ai_status = self.test_results.get("ai_engine", {}).get("status", "unknown")
        ai_icon = "✅" if ai_status == "success" else "❌"
        print(f"{ai_icon} AI Conversation Engine: {ai_status.title()}")
        
        # Database
        db_status = self.test_results.get("database", {}).get("status", "unknown")
        db_icon = "✅" if db_status == "success" else "❌"
        print(f"{db_icon} Database Operations: {db_status.title()}")
        
        # Configuration
        config_status = self.test_results.get("configuration", {}).get("status", "unknown")
        config_icon = "✅" if config_status == "success" else "❌"
        print(f"{config_icon} Configuration System: {config_status.title()}")
        
        # API connectivity
        api_results = self.test_results.get("api_connectivity", {})
        if isinstance(api_results, dict) and "NASA APOD" in api_results:
            working_apis = len([api for api in api_results.values() if isinstance(api, dict) and api.get("status") == "success"])
            total_apis = len(api_results)
            print(f"🔗 API Connectivity: {working_apis}/{total_apis} APIs working")
        
        # Bot readiness assessment
        print(f"\n🤖 Bot Readiness Assessment:")
        
        # Check critical components
        critical_components = [
            ("Dependencies", self.test_results.get("dependencies", {}).get("required", {})),
            ("Configuration", config_status == "success"),
            ("Space Features", space_status == "success"),
            ("AI Engine", ai_status == "success")
        ]
        
        ready_components = 0
        for component_name, status in critical_components:
            if component_name == "Dependencies":
                # Check if required packages are available
                if isinstance(status, dict):
                    missing_required = [pkg for pkg, stat in status.items() if "Missing" in str(stat)]
                    if not missing_required:
                        print(f"✅ {component_name}: All required packages available")
                        ready_components += 1
                    else:
                        print(f"❌ {component_name}: Missing packages: {', '.join(missing_required)}")
            else:
                icon = "✅" if status else "❌"
                status_text = "Ready" if status else "Not Ready"
                print(f"{icon} {component_name}: {status_text}")
                if status:
                    ready_components += 1
        
        # Overall readiness
        readiness_percentage = (ready_components / len(critical_components)) * 100
        
        if readiness_percentage == 100:
            print(f"\n🎉 BOT STATUS: PRODUCTION READY ({readiness_percentage:.0f}%)")
            print(f"🚀 Ready to deploy with: python bot.1.0.py")
        elif readiness_percentage >= 75:
            print(f"\n⚠️ BOT STATUS: MOSTLY READY ({readiness_percentage:.0f}%)")
            print(f"💡 Minor issues to resolve before deployment")
        else:
            print(f"\n❌ BOT STATUS: NOT READY ({readiness_percentage:.0f}%)")
            print(f"🔧 Critical issues need to be resolved")
        
        # Environment recommendations
        print(f"\n💡 Recommendations:")
        discord_token = os.getenv("DISCORD_TOKEN")
        if not discord_token or discord_token == "YOUR_DISCORD_BOT_TOKEN_HERE":
            print(f"🚫 Set DISCORD_TOKEN environment variable (CRITICAL)")
        
        nasa_key = os.getenv("NASA_API_KEY")
        if not nasa_key or nasa_key == "DEMO_KEY":
            print(f"⭕ Set NASA_API_KEY for better API limits (optional)")
        
        openai_key = os.getenv("OPENAI_API_KEY")
        if not openai_key:
            print(f"⭕ Set OPENAI_API_KEY for enhanced AI features (optional)")
        
        # Save detailed report
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "execution_time": total_time,
            "memory_usage": self.memory_usage,
            "performance_metrics": self.performance_metrics,
            "test_results": self.test_results,
            "readiness_percentage": readiness_percentage,
            "summary": {
                "total_tests": total_tests,
                "successful_tests": successful_tests,
                "failed_tests": failed_tests,
                "success_rate": (successful_tests/total_tests)*100
            }
        }
        
        report_file = Path("data/test_report.json")
        report_file.parent.mkdir(parents=True, exist_ok=True)
        with open(report_file, 'w') as f:
            json.dump(report_data, f, indent=2, default=str)
        
        print(f"\n📄 Detailed report saved to: {report_file}")
        print("=" * 80)


async def main():
    """Run the comprehensive test suite"""
    test_suite = AstraBotTestSuite()
    await test_suite.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())
