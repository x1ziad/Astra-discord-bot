#!/usr/bin/env python3
"""
Standalone Performance Analysis for Astra Bot
Independent analysis that doesn't require environment variables
"""

import asyncio
import json
import sqlite3
import time
import psutil
import sys
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List
import traceback


class StandalonePerformanceAnalyzer:
    """Standalone performance analysis without dependencies"""

    def __init__(self):
        self.start_time = time.time()
        self.project_root = Path(__file__).parent
        self.results = {
            "analysis_timestamp": datetime.now(timezone.utc).isoformat(),
            "project_path": str(self.project_root),
            "system_performance": {},
            "file_analysis": {},
            "database_analysis": {},
            "code_quality": {},
            "architecture_analysis": {},
            "deployment_readiness": {},
            "performance_metrics": {},
            "recommendations": [],
        }

    def run_analysis(self) -> Dict[str, Any]:
        """Run comprehensive analysis"""
        print("🔍 Astra Bot Performance & Architecture Analysis")
        print("=" * 60)

        try:
            # System performance
            print("📊 Analyzing System Performance...")
            self.analyze_system_performance()

            # File structure analysis
            print("📁 Analyzing Project Structure...")
            self.analyze_project_structure()

            # Database analysis
            print("🗄️  Analyzing Databases...")
            self.analyze_databases()

            # Code quality analysis
            print("⚡ Analyzing Code Quality...")
            self.analyze_code_quality()

            # Architecture analysis
            print("🏗️  Analyzing Architecture...")
            self.analyze_architecture()

            # Deployment readiness
            print("🚀 Checking Deployment Readiness...")
            self.analyze_deployment_readiness()

            # Performance projections
            print("📈 Calculating Performance Projections...")
            self.calculate_performance_projections()

            # Generate recommendations
            print("💡 Generating Recommendations...")
            self.generate_recommendations()

            self.results["analysis_duration"] = time.time() - self.start_time
            print(f"✅ Analysis completed in {self.results['analysis_duration']:.2f}s")

            return self.results

        except Exception as e:
            print(f"❌ Analysis failed: {e}")
            traceback.print_exc()
            self.results["error"] = str(e)
            return self.results

    def analyze_system_performance(self):
        """Analyze current system performance"""
        try:
            # System metrics
            cpu_count = psutil.cpu_count()
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage("/")

            # Process metrics
            process = psutil.Process()
            process_memory = process.memory_info()

            self.results["system_performance"] = {
                "cpu": {
                    "cores": cpu_count,
                    "usage_percent": cpu_percent,
                    "performance_rating": self._rate_cpu_performance(
                        cpu_percent, cpu_count
                    ),
                },
                "memory": {
                    "total_gb": memory.total / (1024**3),
                    "available_gb": memory.available / (1024**3),
                    "usage_percent": memory.percent,
                    "process_memory_mb": process_memory.rss / (1024**2),
                    "performance_rating": self._rate_memory_performance(memory.percent),
                },
                "disk": {
                    "usage_percent": disk.percent,
                    "free_gb": disk.free / (1024**3),
                    "performance_rating": self._rate_disk_performance(disk.percent),
                },
                "process": {
                    "threads": process.num_threads(),
                    "open_files": (
                        len(process.open_files())
                        if hasattr(process, "open_files")
                        else 0
                    ),
                    "cpu_percent": process.cpu_percent(),
                },
            }

        except Exception as e:
            self.results["system_performance"] = {"error": str(e)}

    def analyze_project_structure(self):
        """Analyze project file structure"""
        try:
            structure_analysis = {
                "total_files": 0,
                "python_files": 0,
                "total_size_mb": 0,
                "directories": {},
                "file_types": {},
                "large_files": [],
                "complexity_score": 0,
            }

            # Count files and analyze structure
            for path in self.project_root.rglob("*"):
                if path.is_file():
                    structure_analysis["total_files"] += 1
                    size_mb = path.stat().st_size / (1024**2)
                    structure_analysis["total_size_mb"] += size_mb

                    # Track file types
                    ext = path.suffix.lower()
                    if ext not in structure_analysis["file_types"]:
                        structure_analysis["file_types"][ext] = 0
                    structure_analysis["file_types"][ext] += 1

                    # Python files
                    if ext == ".py":
                        structure_analysis["python_files"] += 1

                    # Large files (>1MB)
                    if size_mb > 1:
                        structure_analysis["large_files"].append(
                            {
                                "path": str(path.relative_to(self.project_root)),
                                "size_mb": round(size_mb, 2),
                            }
                        )

                elif path.is_dir() and not path.name.startswith("."):
                    dir_name = str(path.relative_to(self.project_root))
                    if dir_name and "/" not in dir_name:  # Top-level directories only
                        structure_analysis["directories"][dir_name] = len(
                            list(path.rglob("*.py"))
                        )

            # Calculate complexity score
            structure_analysis["complexity_score"] = self._calculate_complexity_score(
                structure_analysis
            )

            self.results["file_analysis"] = structure_analysis

        except Exception as e:
            self.results["file_analysis"] = {"error": str(e)}

    def analyze_databases(self):
        """Analyze database files"""
        db_analysis = {
            "databases": [],
            "total_size_mb": 0,
            "performance_projection": {},
        }

        try:
            data_dir = self.project_root / "data"
            if data_dir.exists():
                for db_file in data_dir.glob("*.db"):
                    db_info = self._analyze_database(db_file)
                    db_analysis["databases"].append(db_info)
                    db_analysis["total_size_mb"] += db_info.get("size_mb", 0)

            # Performance projection
            db_analysis["performance_projection"] = self._project_database_performance(
                db_analysis["total_size_mb"]
            )

            self.results["database_analysis"] = db_analysis

        except Exception as e:
            self.results["database_analysis"] = {"error": str(e)}

    def _analyze_database(self, db_path: Path) -> Dict[str, Any]:
        """Analyze individual database"""
        try:
            db_info = {
                "name": db_path.name,
                "size_mb": db_path.stat().st_size / (1024**2),
                "tables": {},
                "performance_metrics": {},
            }

            with sqlite3.connect(db_path) as conn:
                # Get tables
                tables = conn.execute(
                    "SELECT name FROM sqlite_master WHERE type='table'"
                ).fetchall()

                total_records = 0
                for (table_name,) in tables:
                    try:
                        start_time = time.time()
                        count = conn.execute(
                            f"SELECT COUNT(*) FROM {table_name}"
                        ).fetchone()[0]
                        query_time = (time.time() - start_time) * 1000

                        db_info["tables"][table_name] = {
                            "records": count,
                            "query_time_ms": query_time,
                        }
                        total_records += count

                    except Exception:
                        db_info["tables"][table_name] = {"error": "Access denied"}

                # Performance metrics
                start_time = time.time()
                conn.execute("SELECT 1").fetchone()
                simple_query_time = (time.time() - start_time) * 1000

                db_info["performance_metrics"] = {
                    "total_records": total_records,
                    "simple_query_time_ms": simple_query_time,
                    "estimated_concurrent_capacity": self._estimate_db_capacity(
                        db_info["size_mb"], simple_query_time
                    ),
                }

            return db_info

        except Exception as e:
            return {"name": db_path.name, "error": str(e)}

    def analyze_code_quality(self):
        """Analyze code quality metrics"""
        try:
            quality_analysis = {
                "python_files_analyzed": 0,
                "total_lines": 0,
                "comment_lines": 0,
                "blank_lines": 0,
                "code_lines": 0,
                "functions": 0,
                "classes": 0,
                "imports": 0,
                "complexity_indicators": {},
                "ai_components": {},
                "documentation_coverage": 0,
            }

            # Analyze key Python files
            key_files = [
                "ai/consolidated_ai_engine.py",
                "ai/user_profiling.py",
                "ai/proactive_engagement.py",
                "cogs/advanced_ai.py",
                "config/enhanced_config.py",
            ]

            for file_path in key_files:
                full_path = self.project_root / file_path
                if full_path.exists():
                    file_analysis = self._analyze_python_file(full_path)
                    quality_analysis["python_files_analyzed"] += 1

                    # Aggregate metrics
                    quality_analysis["total_lines"] += file_analysis.get(
                        "total_lines", 0
                    )
                    quality_analysis["code_lines"] += file_analysis.get("code_lines", 0)
                    quality_analysis["comment_lines"] += file_analysis.get(
                        "comment_lines", 0
                    )
                    quality_analysis["functions"] += file_analysis.get("functions", 0)
                    quality_analysis["classes"] += file_analysis.get("classes", 0)
                    quality_analysis["imports"] += file_analysis.get("imports", 0)

                    # AI-specific analysis
                    if "ai/" in file_path:
                        quality_analysis["ai_components"][file_path] = {
                            "complexity": file_analysis.get("complexity_score", 0),
                            "ai_features": file_analysis.get("ai_features", []),
                        }

            # Calculate metrics
            if quality_analysis["total_lines"] > 0:
                quality_analysis["comment_ratio"] = (
                    quality_analysis["comment_lines"] / quality_analysis["total_lines"]
                )
                quality_analysis["documentation_coverage"] = min(
                    100, quality_analysis["comment_ratio"] * 200
                )

            quality_analysis["code_quality_score"] = self._calculate_code_quality_score(
                quality_analysis
            )

            self.results["code_quality"] = quality_analysis

        except Exception as e:
            self.results["code_quality"] = {"error": str(e)}

    def _analyze_python_file(self, file_path: Path) -> Dict[str, Any]:
        """Analyze a single Python file"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            lines = content.split("\n")
            analysis = {
                "total_lines": len(lines),
                "code_lines": 0,
                "comment_lines": 0,
                "blank_lines": 0,
                "functions": 0,
                "classes": 0,
                "imports": 0,
                "complexity_score": 0,
                "ai_features": [],
            }

            # Analyze line by line
            for line in lines:
                stripped = line.strip()

                if not stripped:
                    analysis["blank_lines"] += 1
                elif (
                    stripped.startswith("#")
                    or stripped.startswith('"""')
                    or stripped.startswith("'''")
                ):
                    analysis["comment_lines"] += 1
                else:
                    analysis["code_lines"] += 1

                # Count structures
                if stripped.startswith("def "):
                    analysis["functions"] += 1
                elif stripped.startswith("class "):
                    analysis["classes"] += 1
                elif stripped.startswith("import ") or stripped.startswith("from "):
                    analysis["imports"] += 1

            # AI features detection
            ai_keywords = [
                "ai",
                "artificial",
                "intelligence",
                "machine learning",
                "neural",
                "sentiment",
                "personality",
                "proactive",
                "engagement",
                "conversation",
                "embedding",
                "vector",
                "model",
                "prediction",
                "classification",
            ]

            content_lower = content.lower()
            for keyword in ai_keywords:
                if keyword in content_lower:
                    analysis["ai_features"].append(keyword)

            analysis["complexity_score"] = self._calculate_file_complexity(analysis)

            return analysis

        except Exception as e:
            return {"error": str(e)}

    def analyze_architecture(self):
        """Analyze bot architecture"""
        try:
            architecture = {
                "components": {
                    "ai_engine": self._check_component("ai/consolidated_ai_engine.py"),
                    "user_profiling": self._check_component("ai/user_profiling.py"),
                    "proactive_engagement": self._check_component(
                        "ai/proactive_engagement.py"
                    ),
                    "advanced_ai_cog": self._check_component("cogs/advanced_ai.py"),
                    "config_system": self._check_component("config/enhanced_config.py"),
                    "database_system": self._check_component("utils/database.py"),
                    "error_handling": self._check_component("utils/error_handler.py"),
                    "logging_system": self._check_component(
                        "logger/enhanced_logger.py"
                    ),
                },
                "integration_score": 0,
                "scalability_rating": "",
                "ai_sophistication": "",
                "architecture_strengths": [],
                "architecture_weaknesses": [],
            }

            # Calculate integration score
            working_components = sum(
                1 for comp in architecture["components"].values() if comp["exists"]
            )
            total_components = len(architecture["components"])
            architecture["integration_score"] = (
                working_components / total_components
            ) * 100

            # Analyze AI sophistication
            ai_features = []
            if architecture["components"]["ai_engine"]["exists"]:
                ai_features.extend(["consolidated_engine", "multi_provider"])
            if architecture["components"]["user_profiling"]["exists"]:
                ai_features.extend(["personality_learning", "behavior_analysis"])
            if architecture["components"]["proactive_engagement"]["exists"]:
                ai_features.extend(["proactive_responses", "context_awareness"])

            architecture["ai_sophistication"] = self._rate_ai_sophistication(
                ai_features
            )
            architecture["scalability_rating"] = self._rate_scalability(architecture)

            # Strengths and weaknesses
            if len(ai_features) >= 4:
                architecture["architecture_strengths"].append(
                    "Advanced AI capabilities"
                )
            if architecture["integration_score"] > 80:
                architecture["architecture_strengths"].append(
                    "Good component integration"
                )
            if architecture["components"]["config_system"]["exists"]:
                architecture["architecture_strengths"].append(
                    "Flexible configuration system"
                )

            if architecture["integration_score"] < 70:
                architecture["architecture_weaknesses"].append(
                    "Missing core components"
                )
            if not architecture["components"]["error_handling"]["exists"]:
                architecture["architecture_weaknesses"].append("Limited error handling")

            self.results["architecture_analysis"] = architecture

        except Exception as e:
            self.results["architecture_analysis"] = {"error": str(e)}

    def analyze_deployment_readiness(self):
        """Analyze deployment readiness"""
        try:
            deployment = {
                "configuration_files": {},
                "dependencies": {},
                "deployment_targets": {},
                "performance_readiness": {},
                "security_considerations": {},
                "readiness_score": 0,
            }

            # Check configuration files
            config_files = [
                "Dockerfile",
                "requirements.txt",
                "railway.toml",
                "Procfile",
                "config.json",
                ".env",
            ]

            for file_name in config_files:
                file_path = self.project_root / file_name
                deployment["configuration_files"][file_name] = {
                    "exists": file_path.exists(),
                    "size_kb": (
                        file_path.stat().st_size / 1024 if file_path.exists() else 0
                    ),
                }

            # Analyze dependencies
            requirements_file = self.project_root / "requirements.txt"
            if requirements_file.exists():
                with open(requirements_file, "r") as f:
                    deps = f.read().strip().split("\n")
                    deployment["dependencies"] = {
                        "total_dependencies": len(
                            [d for d in deps if d.strip() and not d.startswith("#")]
                        ),
                        "has_ai_dependencies": any(
                            "openai" in d or "anthropic" in d for d in deps
                        ),
                        "has_discord_dependency": any("discord" in d for d in deps),
                        "estimated_install_time": len(deps) * 0.5,  # rough estimate
                    }

            # Deployment targets
            deployment["deployment_targets"] = {
                "railway": deployment["configuration_files"]["railway.toml"]["exists"],
                "docker": deployment["configuration_files"]["Dockerfile"]["exists"],
                "heroku": deployment["configuration_files"]["Procfile"]["exists"],
                "local": True,  # Always possible
            }

            # Performance readiness
            system_perf = self.results.get("system_performance", {})
            deployment["performance_readiness"] = {
                "memory_sufficient": system_perf.get("memory", {}).get("total_gb", 0)
                >= 1,
                "cpu_adequate": system_perf.get("cpu", {}).get("cores", 0) >= 1,
                "expected_response_time_ms": self._estimate_response_times(),
                "concurrent_user_capacity": self._estimate_user_capacity(),
            }

            # Calculate readiness score
            score_factors = [
                deployment["configuration_files"]["requirements.txt"]["exists"] * 20,
                deployment["dependencies"].get("has_discord_dependency", False) * 20,
                deployment["deployment_targets"]["railway"] * 15,
                deployment["performance_readiness"]["memory_sufficient"] * 25,
                deployment["performance_readiness"]["cpu_adequate"] * 20,
            ]

            deployment["readiness_score"] = sum(score_factors)

            self.results["deployment_readiness"] = deployment

        except Exception as e:
            self.results["deployment_readiness"] = {"error": str(e)}

    def calculate_performance_projections(self):
        """Calculate expected performance metrics"""
        try:
            projections = {
                "response_times": {},
                "throughput": {},
                "scalability": {},
                "resource_usage": {},
            }

            # Response time projections
            system_perf = self.results.get("system_performance", {})
            cpu_score = system_perf.get("cpu", {}).get("performance_rating", "moderate")
            memory_score = system_perf.get("memory", {}).get(
                "performance_rating", "moderate"
            )

            base_response_time = {
                "excellent": 200,
                "good": 500,
                "moderate": 1000,
                "poor": 2000,
            }.get(cpu_score, 1000)

            projections["response_times"] = {
                "simple_commands_ms": base_response_time * 0.5,
                "ai_responses_ms": base_response_time * 2,
                "complex_analysis_ms": base_response_time * 5,
                "database_queries_ms": 50,
                "image_generation_ms": 10000,  # Typically external API
            }

            # Throughput projections
            cpu_cores = system_perf.get("cpu", {}).get("cores", 1)
            memory_gb = system_perf.get("memory", {}).get("total_gb", 1)

            projections["throughput"] = {
                "messages_per_second": min(cpu_cores * 10, memory_gb * 5),
                "concurrent_conversations": min(cpu_cores * 5, memory_gb * 2),
                "ai_requests_per_minute": cpu_cores * 30,
                "database_operations_per_second": 100,
            }

            # Scalability projections
            projections["scalability"] = {
                "max_guilds": 1000,
                "max_concurrent_users": projections["throughput"][
                    "concurrent_conversations"
                ]
                * 10,
                "storage_growth_mb_per_day": 10,
                "memory_growth_per_user_kb": 50,
            }

            # Resource usage projections
            projections["resource_usage"] = {
                "idle_memory_mb": 100,
                "active_memory_mb": 300,
                "peak_memory_mb": 500,
                "cpu_usage_idle": 5,
                "cpu_usage_active": 20,
                "cpu_usage_peak": 60,
            }

            self.results["performance_metrics"] = projections

        except Exception as e:
            self.results["performance_metrics"] = {"error": str(e)}

    def generate_recommendations(self):
        """Generate performance and optimization recommendations"""
        recommendations = []

        try:
            # System performance recommendations
            system_perf = self.results.get("system_performance", {})
            memory_usage = system_perf.get("memory", {}).get("usage_percent", 0)
            cpu_usage = system_perf.get("cpu", {}).get("usage_percent", 0)

            if memory_usage > 80:
                recommendations.append(
                    {
                        "category": "system",
                        "priority": "high",
                        "issue": "High memory usage detected",
                        "recommendation": "Consider upgrading RAM or optimizing memory usage",
                        "expected_impact": "Improved stability and response times",
                    }
                )

            if cpu_usage > 70:
                recommendations.append(
                    {
                        "category": "system",
                        "priority": "medium",
                        "issue": "High CPU usage",
                        "recommendation": "Optimize CPU-intensive operations or upgrade hardware",
                        "expected_impact": "Better concurrent user handling",
                    }
                )

            # Architecture recommendations
            arch_analysis = self.results.get("architecture_analysis", {})
            integration_score = arch_analysis.get("integration_score", 0)

            if integration_score < 80:
                recommendations.append(
                    {
                        "category": "architecture",
                        "priority": "high",
                        "issue": "Missing core components",
                        "recommendation": "Implement missing components for full functionality",
                        "expected_impact": "Complete feature set and better reliability",
                    }
                )

            # Database recommendations
            db_analysis = self.results.get("database_analysis", {})
            total_db_size = db_analysis.get("total_size_mb", 0)

            if total_db_size > 50:
                recommendations.append(
                    {
                        "category": "database",
                        "priority": "medium",
                        "issue": "Database size growing large",
                        "recommendation": "Implement data archiving and cleanup routines",
                        "expected_impact": "Maintained query performance over time",
                    }
                )

            # Performance optimization recommendations
            projections = self.results.get("performance_metrics", {})
            ai_response_time = projections.get("response_times", {}).get(
                "ai_responses_ms", 0
            )

            if ai_response_time > 3000:
                recommendations.append(
                    {
                        "category": "performance",
                        "priority": "medium",
                        "issue": "AI responses may be slow",
                        "recommendation": "Implement response caching and optimize AI calls",
                        "expected_impact": "Faster user interactions",
                    }
                )

            # Deployment recommendations
            deployment = self.results.get("deployment_readiness", {})
            readiness_score = deployment.get("readiness_score", 0)

            if readiness_score < 80:
                recommendations.append(
                    {
                        "category": "deployment",
                        "priority": "high",
                        "issue": "Deployment configuration incomplete",
                        "recommendation": "Complete deployment configuration files",
                        "expected_impact": "Smooth production deployment",
                    }
                )

            # AI-specific recommendations
            ai_sophistication = arch_analysis.get("ai_sophistication", "")
            if ai_sophistication == "basic":
                recommendations.append(
                    {
                        "category": "ai",
                        "priority": "low",
                        "issue": "Basic AI capabilities",
                        "recommendation": "Enhance AI features with advanced personality learning",
                        "expected_impact": "More engaging user interactions",
                    }
                )

            # Code quality recommendations
            code_quality = self.results.get("code_quality", {})
            comment_ratio = code_quality.get("comment_ratio", 0)

            if comment_ratio < 0.2:
                recommendations.append(
                    {
                        "category": "maintenance",
                        "priority": "low",
                        "issue": "Low code documentation",
                        "recommendation": "Add more code comments and documentation",
                        "expected_impact": "Easier maintenance and development",
                    }
                )

            self.results["recommendations"] = recommendations

        except Exception as e:
            self.results["recommendations"] = [{"error": str(e)}]

    # Helper methods
    def _rate_cpu_performance(self, usage: float, cores: int) -> str:
        if cores >= 4 and usage < 50:
            return "excellent"
        elif cores >= 2 and usage < 70:
            return "good"
        elif usage < 85:
            return "moderate"
        else:
            return "poor"

    def _rate_memory_performance(self, usage: float) -> str:
        if usage < 60:
            return "excellent"
        elif usage < 75:
            return "good"
        elif usage < 85:
            return "moderate"
        else:
            return "poor"

    def _rate_disk_performance(self, usage: float) -> str:
        if usage < 70:
            return "excellent"
        elif usage < 85:
            return "good"
        elif usage < 95:
            return "moderate"
        else:
            return "poor"

    def _calculate_complexity_score(self, structure: Dict) -> int:
        score = 0
        score += min(structure["python_files"] * 2, 50)
        score += min(len(structure["directories"]) * 5, 25)
        score += min(structure["total_files"], 25)
        return score

    def _project_database_performance(self, size_mb: float) -> Dict:
        return {
            "estimated_query_time_ms": max(1, size_mb * 0.1),
            "max_concurrent_users": max(10, int(1000 / max(1, size_mb * 0.1))),
            "recommended_cleanup_frequency_days": max(7, int(size_mb / 10)),
        }

    def _estimate_db_capacity(self, size_mb: float, query_time_ms: float) -> int:
        if query_time_ms < 10:
            return int(100 / max(size_mb * 0.01, 1))
        else:
            return int(50 / max(size_mb * 0.01, 1))

    def _calculate_code_quality_score(self, quality: Dict) -> int:
        score = 50  # Base score
        score += min(quality["comment_ratio"] * 100, 30)
        score += min(quality["functions"] / 10, 10)
        score += min(quality["classes"] / 5, 10)
        return min(score, 100)

    def _calculate_file_complexity(self, analysis: Dict) -> int:
        return analysis["functions"] + analysis["classes"] * 2

    def _check_component(self, path: str) -> Dict:
        component_path = self.project_root / path
        return {
            "exists": component_path.exists(),
            "size_kb": (
                component_path.stat().st_size / 1024 if component_path.exists() else 0
            ),
        }

    def _rate_ai_sophistication(self, features: List[str]) -> str:
        feature_count = len(features)
        if feature_count >= 5:
            return "advanced"
        elif feature_count >= 3:
            return "intermediate"
        elif feature_count >= 1:
            return "basic"
        else:
            return "minimal"

    def _rate_scalability(self, architecture: Dict) -> str:
        score = architecture["integration_score"]
        if score >= 90:
            return "excellent"
        elif score >= 75:
            return "good"
        elif score >= 60:
            return "moderate"
        else:
            return "limited"

    def _estimate_response_times(self) -> int:
        system_perf = self.results.get("system_performance", {})
        cpu_rating = system_perf.get("cpu", {}).get("performance_rating", "moderate")

        times = {"excellent": 300, "good": 600, "moderate": 1200, "poor": 2500}

        return times.get(cpu_rating, 1200)

    def _estimate_user_capacity(self) -> int:
        system_perf = self.results.get("system_performance", {})
        memory_gb = system_perf.get("memory", {}).get("total_gb", 1)
        cpu_cores = system_perf.get("cpu", {}).get("cores", 1)

        return int(min(memory_gb * 100, cpu_cores * 50))

    def generate_report(self) -> str:
        """Generate comprehensive analysis report"""
        report = []
        report.append("🚀 ASTRA BOT PERFORMANCE & ARCHITECTURE ANALYSIS")
        report.append("=" * 70)
        report.append(f"📅 Analysis Date: {self.results['analysis_timestamp']}")
        report.append(
            f"⏱️  Analysis Duration: {self.results.get('analysis_duration', 0):.2f}s"
        )
        report.append(f"📁 Project Path: {self.results['project_path']}")
        report.append("")

        # System Performance Summary
        system_perf = self.results.get("system_performance", {})
        if system_perf and "error" not in system_perf:
            report.append("🖥️  SYSTEM PERFORMANCE")
            report.append("-" * 40)
            report.append(
                f"CPU: {system_perf.get('cpu', {}).get('cores', 0)} cores, {system_perf.get('cpu', {}).get('usage_percent', 0):.1f}% usage ({system_perf.get('cpu', {}).get('performance_rating', 'unknown')})"
            )
            report.append(
                f"Memory: {system_perf.get('memory', {}).get('total_gb', 0):.1f}GB total, {system_perf.get('memory', {}).get('usage_percent', 0):.1f}% usage ({system_perf.get('memory', {}).get('performance_rating', 'unknown')})"
            )
            report.append(
                f"Process Memory: {system_perf.get('memory', {}).get('process_memory_mb', 0):.1f}MB"
            )
            report.append("")

        # Architecture Analysis
        arch_analysis = self.results.get("architecture_analysis", {})
        if arch_analysis and "error" not in arch_analysis:
            report.append("🏗️  ARCHITECTURE ANALYSIS")
            report.append("-" * 40)
            report.append(
                f"Integration Score: {arch_analysis.get('integration_score', 0):.1f}/100"
            )
            report.append(
                f"AI Sophistication: {arch_analysis.get('ai_sophistication', 'unknown')}"
            )
            report.append(
                f"Scalability Rating: {arch_analysis.get('scalability_rating', 'unknown')}"
            )

            # Component status
            components = arch_analysis.get("components", {})
            working = sum(1 for comp in components.values() if comp.get("exists"))
            total = len(components)
            report.append(f"Components: {working}/{total} available")
            report.append("")

        # Performance Projections
        projections = self.results.get("performance_metrics", {})
        if projections and "error" not in projections:
            report.append("📈 EXPECTED PERFORMANCE")
            report.append("-" * 40)
            response_times = projections.get("response_times", {})
            throughput = projections.get("throughput", {})

            report.append(
                f"AI Response Time: {response_times.get('ai_responses_ms', 0)}ms"
            )
            report.append(
                f"Simple Commands: {response_times.get('simple_commands_ms', 0)}ms"
            )
            report.append(
                f"Concurrent Users: {throughput.get('concurrent_conversations', 0)}"
            )
            report.append(
                f"Messages/Second: {throughput.get('messages_per_second', 0)}"
            )
            report.append("")

        # Database Analysis
        db_analysis = self.results.get("database_analysis", {})
        if db_analysis and "error" not in db_analysis:
            report.append("🗄️  DATABASE ANALYSIS")
            report.append("-" * 40)
            databases = db_analysis.get("databases", [])
            report.append(f"Databases Found: {len(databases)}")
            report.append(f"Total Size: {db_analysis.get('total_size_mb', 0):.2f}MB")

            for db in databases[:3]:  # Show first 3 databases
                if "error" not in db:
                    table_count = len(db.get("tables", {}))
                    report.append(
                        f"  • {db['name']}: {table_count} tables, {db.get('size_mb', 0):.2f}MB"
                    )
            report.append("")

        # Deployment Readiness
        deployment = self.results.get("deployment_readiness", {})
        if deployment and "error" not in deployment:
            report.append("🚀 DEPLOYMENT READINESS")
            report.append("-" * 40)
            report.append(
                f"Readiness Score: {deployment.get('readiness_score', 0)}/100"
            )

            config_files = deployment.get("configuration_files", {})
            ready_configs = sum(
                1 for conf in config_files.values() if conf.get("exists")
            )
            total_configs = len(config_files)
            report.append(f"Config Files: {ready_configs}/{total_configs} ready")

            targets = deployment.get("deployment_targets", {})
            ready_targets = [name for name, ready in targets.items() if ready]
            report.append(
                f"Deployment Targets: {', '.join(ready_targets) if ready_targets else 'Local only'}"
            )
            report.append("")

        # Code Quality
        code_quality = self.results.get("code_quality", {})
        if code_quality and "error" not in code_quality:
            report.append("⚡ CODE QUALITY")
            report.append("-" * 40)
            report.append(
                f"Files Analyzed: {code_quality.get('python_files_analyzed', 0)}"
            )
            report.append(f"Total Lines: {code_quality.get('total_lines', 0):,}")
            report.append(f"Functions: {code_quality.get('functions', 0)}")
            report.append(f"Classes: {code_quality.get('classes', 0)}")
            report.append(
                f"Documentation Coverage: {code_quality.get('documentation_coverage', 0):.1f}%"
            )
            report.append(
                f"Code Quality Score: {code_quality.get('code_quality_score', 0)}/100"
            )
            report.append("")

        # AI Components
        if code_quality and code_quality.get("ai_components"):
            report.append("🤖 AI COMPONENTS")
            report.append("-" * 40)
            for component, info in code_quality["ai_components"].items():
                complexity = info.get("complexity", 0)
                features = len(info.get("ai_features", []))
                report.append(
                    f"• {component}: Complexity {complexity}, Features {features}"
                )
            report.append("")

        # Recommendations
        recommendations = self.results.get("recommendations", [])
        if recommendations and not (
            len(recommendations) == 1 and "error" in recommendations[0]
        ):
            report.append("💡 RECOMMENDATIONS")
            report.append("-" * 40)

            # Group by priority
            high_priority = [r for r in recommendations if r.get("priority") == "high"]
            medium_priority = [
                r for r in recommendations if r.get("priority") == "medium"
            ]
            low_priority = [r for r in recommendations if r.get("priority") == "low"]

            for priority_group, emoji, name in [
                (high_priority, "🔴", "HIGH PRIORITY"),
                (medium_priority, "🟡", "MEDIUM PRIORITY"),
                (low_priority, "🟢", "LOW PRIORITY"),
            ]:
                if priority_group:
                    report.append(f"\n{emoji} {name}:")
                    for rec in priority_group:
                        report.append(
                            f"• [{rec.get('category', '').upper()}] {rec.get('issue', '')}"
                        )
                        report.append(f"  → {rec.get('recommendation', '')}")
                        if rec.get("expected_impact"):
                            report.append(f"  📊 Impact: {rec['expected_impact']}")
                        report.append("")

        # Overall Assessment
        report.append("📊 OVERALL ASSESSMENT")
        report.append("-" * 40)

        # Calculate overall score
        scores = []
        if arch_analysis.get("integration_score"):
            scores.append(arch_analysis["integration_score"])
        if deployment.get("readiness_score"):
            scores.append(deployment["readiness_score"])
        if code_quality.get("code_quality_score"):
            scores.append(code_quality["code_quality_score"])

        overall_score = sum(scores) / len(scores) if scores else 0

        report.append(f"Overall Performance Score: {overall_score:.1f}/100")

        if overall_score >= 90:
            report.append("Status: 🟢 Excellent - Production Ready")
            report.append(
                "Assessment: Your bot is well-architected and ready for deployment!"
            )
        elif overall_score >= 75:
            report.append("Status: 🟡 Good - Minor Optimizations Needed")
            report.append("Assessment: Your bot is solid with room for improvement.")
        elif overall_score >= 60:
            report.append("Status: 🟠 Moderate - Some Issues to Address")
            report.append(
                "Assessment: Your bot has good foundations but needs optimization."
            )
        else:
            report.append("Status: 🔴 Needs Improvement")
            report.append("Assessment: Several areas need attention before deployment.")

        report.append("")
        report.append("🎉 Analysis Complete!")
        report.append("")
        report.append("💡 Next Steps:")
        if high_priority := [r for r in recommendations if r.get("priority") == "high"]:
            report.append(f"1. Address {len(high_priority)} high-priority issues first")
        else:
            report.append("1. No critical issues found!")

        if medium_priority := [
            r for r in recommendations if r.get("priority") == "medium"
        ]:
            report.append(f"2. Optimize {len(medium_priority)} performance areas")

        report.append("3. Monitor system performance in production")
        report.append("4. Regularly update and maintain the codebase")

        return "\n".join(report)


if __name__ == "__main__":
    analyzer = StandalonePerformanceAnalyzer()

    # Run analysis
    results = analyzer.run_analysis()

    # Generate and display report
    report = analyzer.generate_report()
    print("\n" + report)

    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = f"data/performance_analysis_{timestamp}.json"
    report_file = f"data/performance_report_{timestamp}.txt"

    os.makedirs("data", exist_ok=True)

    # Save detailed results
    with open(results_file, "w") as f:
        json.dump(results, f, indent=2, default=str)

    # Save report
    with open(report_file, "w") as f:
        f.write(report)

    print(f"\n📄 Detailed results saved to: {results_file}")
    print(f"📄 Report saved to: {report_file}")
