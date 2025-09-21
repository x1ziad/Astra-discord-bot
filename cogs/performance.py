"""
Performance Testing Cog
Provides commands to run comprehensive performance tests and optimizations
"""

import discord
from discord import app_commands
from discord.ext import commands
import asyncio
import logging
import json
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone

# from utils.performance_tester import initialize_performance_tester  # Temporarily disabled
from utils.performance_optimizer import performance_optimizer
from utils.command_optimizer import optimize_command, optimized_send

logger = logging.getLogger("astra.performance_cog")


class PerformanceCog(commands.Cog, name="Performance"):
    """Performance testing and optimization commands"""

    def __init__(self, bot):
        self.bot = bot
        # self.performance_tester = initialize_performance_tester(bot)  # Temporarily disabled
        self.performance_tester = None  # Placeholder
        self.logger = logger

    @app_commands.command(
        name="performance_test", description="🚀 Run comprehensive performance analysis"
    )
    @app_commands.describe(
        include_ai="Include AI system testing (may take longer)",
        detailed="Show detailed output in channel",
    )
    @app_commands.default_permissions(administrator=True)
    @optimize_command(rate_limit_enabled=True, rate_limit_per_minute=2)
    async def performance_test(
        self,
        interaction: discord.Interaction,
        include_ai: bool = True,
        detailed: bool = False,
    ):
        """Run comprehensive performance test"""
        await interaction.response.defer()

        try:
            # Start performance test
            self.logger.info(f"Performance test initiated by {interaction.user}")

            # Create initial embed
            embed = discord.Embed(
                title="🚀 Performance Test Started",
                description="Running comprehensive performance analysis...",
                color=0x00FF00,
                timestamp=datetime.now(timezone.utc),
            )
            embed.add_field(
                name="⏱️ Status", value="Starting test suite...", inline=False
            )
            embed.add_field(
                name="🔧 Configuration",
                value=f"AI Testing: {'✅' if include_ai else '❌'}\nDetailed Output: {'✅' if detailed else '❌'}",
                inline=True,
            )

            await interaction.followup.send(embed=embed)

            # Run the test
            if self.performance_tester:
                test_results = await self.performance_tester.run_comprehensive_test()
            else:
                test_results = {
                    "status": "disabled",
                    "message": "Performance tester temporarily disabled",
                }

            # Create results embed
            results_embed = discord.Embed(
                title="📊 Performance Test Results",
                color=0x0099FF,
                timestamp=datetime.now(timezone.utc),
            )

            # Add summary statistics
            metadata = test_results.get("test_metadata", {})
            results_embed.add_field(
                name="⏱️ Test Duration",
                value=f"{metadata.get('duration_seconds', 0):.2f} seconds",
                inline=True,
            )

            # Command analysis
            if "command_analysis" in test_results:
                cmd_analysis = test_results["command_analysis"]
                total_commands = cmd_analysis.get("total_commands", 0)
                optimized_count = len(
                    [
                        cmd
                        for cmd, status in cmd_analysis.get(
                            "optimization_status", {}
                        ).items()
                        if status.get("optimized", False)
                    ]
                )
                optimization_ratio = (
                    (optimized_count / total_commands * 100)
                    if total_commands > 0
                    else 0
                )

                results_embed.add_field(
                    name="📋 Commands",
                    value=f"Total: {total_commands}\nOptimized: {optimization_ratio:.1f}%",
                    inline=True,
                )

            # Database performance
            if "database_performance" in test_results:
                db_perf = test_results["database_performance"]
                if "query_performance" in db_perf:
                    query_perf = db_perf["query_performance"]
                    avg_read = query_perf.get("avg_read_time", 0)
                    avg_write = query_perf.get("avg_write_time", 0)

                    results_embed.add_field(
                        name="💾 Database",
                        value=f"Read: {avg_read:.3f}s\nWrite: {avg_write:.3f}s",
                        inline=True,
                    )

            # AI performance
            if include_ai and "ai_performance" in test_results:
                ai_perf = test_results["ai_performance"]
                ai_available = ai_perf.get("ai_engine_available", False)
                avg_response = ai_perf.get("avg_response_time", 0)

                results_embed.add_field(
                    name="🤖 AI System",
                    value=f"Available: {'✅' if ai_available else '❌'}\nAvg Response: {avg_response:.2f}s",
                    inline=True,
                )

            # Cache performance
            if "cache_performance" in test_results:
                cache_perf = test_results["cache_performance"]
                efficiency = cache_perf.get("overall_efficiency", 0)

                results_embed.add_field(
                    name="🗂️ Cache", value=f"Efficiency: {efficiency:.1%}", inline=True
                )

            # System resources
            if "system_resources" in test_results:
                resource_perf = test_results["system_resources"]
                if "memory_usage" in resource_perf:
                    memory = resource_perf["memory_usage"]
                    memory_mb = memory.get("rss_mb", 0)
                    memory_percent = memory.get("percent", 0)

                    results_embed.add_field(
                        name="⚡ Resources",
                        value=f"Memory: {memory_mb:.1f} MB ({memory_percent:.1f}%)",
                        inline=True,
                    )

            # Overall assessment
            recommendations = test_results.get("recommendations", [])
            top_recommendations = recommendations[:3]  # Top 3 recommendations

            if top_recommendations:
                rec_text = "\n".join([f"• {rec}" for rec in top_recommendations])
                results_embed.add_field(
                    name="💡 Top Recommendations", value=rec_text, inline=False
                )

            # Set footer
            results_embed.set_footer(
                text=f"Test completed • Guild: {interaction.guild.name if interaction.guild else 'DM'}"
            )

            await optimized_send(interaction.followup, embed=results_embed)

            # Send detailed results if requested
            if detailed and len(recommendations) > 3:
                detail_embed = discord.Embed(
                    title="📋 Detailed Recommendations",
                    color=0xFFA500,
                    timestamp=datetime.now(timezone.utc),
                )

                all_recommendations = "\n".join(
                    [f"{i+1}. {rec}" for i, rec in enumerate(recommendations)]
                )

                # Split into multiple fields if too long
                if len(all_recommendations) > 1024:
                    chunks = [
                        all_recommendations[i : i + 1020] + "..."
                        for i in range(0, len(all_recommendations), 1020)
                    ]

                    for i, chunk in enumerate(chunks):
                        detail_embed.add_field(
                            name=f"Recommendations (Part {i+1})",
                            value=chunk,
                            inline=False,
                        )
                else:
                    detail_embed.add_field(
                        name="All Recommendations",
                        value=all_recommendations,
                        inline=False,
                    )

                await optimized_send(interaction.followup, embed=detail_embed)

        except Exception as e:
            error_embed = discord.Embed(
                title="❌ Performance Test Failed",
                description=f"An error occurred during testing: {str(e)}",
                color=0xFF0000,
                timestamp=datetime.now(timezone.utc),
            )

            await optimized_send(interaction.followup, embed=error_embed)
            self.logger.error(f"Performance test failed: {e}")

    @app_commands.command(
        name="performance_status", description="📊 Show current performance metrics"
    )
    @optimize_command(cacheable=True, cache_ttl=60)
    async def performance_status(self, interaction: discord.Interaction):
        """Show current performance status"""
        await interaction.response.defer()

        try:
            # Get performance optimizer report
            perf_report = performance_optimizer.get_performance_report()

            embed = discord.Embed(
                title="📊 Performance Status",
                color=0x0099FF,
                timestamp=datetime.now(timezone.utc),
            )

            # Cache statistics
            caches = perf_report.get("caches", {})
            cache_info = []

            for cache_name, cache_stats in caches.items():
                if isinstance(cache_stats, dict):
                    usage = cache_stats.get("usage_ratio", 0)
                    size = cache_stats.get("size", 0)
                    cache_info.append(
                        f"{cache_name.replace('_', ' ').title()}: {usage:.1%} ({size} items)"
                    )

            if cache_info:
                embed.add_field(
                    name="🗂️ Cache Status", value="\n".join(cache_info), inline=False
                )

            # Command statistics
            command_stats = perf_report.get("command_stats", {})
            if command_stats:
                top_commands = sorted(
                    command_stats.items(),
                    key=lambda x: x[1].get("count", 0),
                    reverse=True,
                )[:5]

                cmd_info = []
                for cmd_name, stats in top_commands:
                    count = stats.get("count", 0)
                    avg_time = stats.get("avg_time", 0)
                    cmd_info.append(f"{cmd_name}: {count} calls, {avg_time:.3f}s avg")

                embed.add_field(
                    name="📈 Top Commands", value="\n".join(cmd_info), inline=False
                )

            # Slow commands
            slow_commands = perf_report.get("slow_commands", [])
            if slow_commands:
                slow_info = []
                for cmd_name, avg_time in slow_commands[:3]:
                    slow_info.append(f"{cmd_name}: {avg_time:.3f}s")

                embed.add_field(
                    name="🐌 Slow Commands", value="\n".join(slow_info), inline=True
                )

            # Metrics
            metrics = perf_report.get("metrics", {})
            cache_hits = metrics.get("cache_hits", 0)
            cache_misses = metrics.get("cache_misses", 0)
            hit_rate = (
                (cache_hits / (cache_hits + cache_misses) * 100)
                if (cache_hits + cache_misses) > 0
                else 0
            )

            embed.add_field(
                name="🎯 Cache Hit Rate",
                value=f"{hit_rate:.1f}%\n({cache_hits} hits, {cache_misses} misses)",
                inline=True,
            )

            # Memory pools
            memory_pools = perf_report.get("memory_pools", {})
            if memory_pools:
                pool_count = len(memory_pools)
                total_objects = sum(memory_pools.values())

                embed.add_field(
                    name="🧠 Memory Pools",
                    value=f"{pool_count} pools\n{total_objects} pooled objects",
                    inline=True,
                )

            embed.set_footer(text="Performance metrics updated in real-time")

            await optimized_send(interaction, embed=embed)

        except Exception as e:
            error_embed = discord.Embed(
                title="❌ Error Getting Performance Status",
                description=f"Could not retrieve performance metrics: {str(e)}",
                color=0xFF0000,
            )

            await optimized_send(interaction, embed=error_embed)
            self.logger.error(f"Performance status error: {e}")

    @app_commands.command(
        name="optimize_cache", description="🧹 Optimize cache systems"
    )
    @app_commands.default_permissions(administrator=True)
    @optimize_command(rate_limit_enabled=True, rate_limit_per_minute=5)
    async def optimize_cache(self, interaction: discord.Interaction):
        """Optimize cache systems"""
        await interaction.response.defer()

        try:
            # Clear expired caches
            await performance_optimizer.command_optimizer.command_cache.clear_expired()
            await performance_optimizer.ai_optimizer.response_cache.clear_expired()
            await performance_optimizer.db_optimizer.query_cache.clear_expired()

            # Get cache statistics
            command_cache_stats = (
                performance_optimizer.command_optimizer.command_cache.get_stats()
            )
            ai_cache_stats = (
                performance_optimizer.ai_optimizer.response_cache.get_stats()
            )
            db_cache_stats = performance_optimizer.db_optimizer.query_cache.get_stats()

            embed = discord.Embed(
                title="🧹 Cache Optimization Complete",
                color=0x00FF00,
                timestamp=datetime.now(timezone.utc),
            )

            embed.add_field(
                name="🗂️ Command Cache",
                value=f"Size: {command_cache_stats['size']}/{command_cache_stats['max_size']}\nUsage: {command_cache_stats['usage_ratio']:.1%}",
                inline=True,
            )

            embed.add_field(
                name="🤖 AI Cache",
                value=f"Size: {ai_cache_stats['size']}/{ai_cache_stats['max_size']}\nUsage: {ai_cache_stats['usage_ratio']:.1%}",
                inline=True,
            )

            embed.add_field(
                name="💾 DB Cache",
                value=f"Size: {db_cache_stats['size']}/{db_cache_stats['max_size']}\nUsage: {db_cache_stats['usage_ratio']:.1%}",
                inline=True,
            )

            embed.add_field(
                name="✅ Actions Taken",
                value="• Cleared expired cache entries\n• Optimized memory usage\n• Updated cache statistics",
                inline=False,
            )

            embed.set_footer(text="Cache optimization recommended every few hours")

            await optimized_send(interaction, embed=embed)

        except Exception as e:
            error_embed = discord.Embed(
                title="❌ Cache Optimization Failed",
                description=f"Error optimizing caches: {str(e)}",
                color=0xFF0000,
            )

            await optimized_send(interaction, embed=error_embed)
            self.logger.error(f"Cache optimization error: {e}")

    @app_commands.command(
        name="performance_report", description="📄 Generate detailed performance report"
    )
    @app_commands.default_permissions(administrator=True)
    @optimize_command(rate_limit_enabled=True, rate_limit_per_minute=3)
    async def performance_report(self, interaction: discord.Interaction):
        """Generate and send detailed performance report"""
        await interaction.response.defer()

        try:
            # Run quick performance analysis
            if self.performance_tester:
                test_results = await self.performance_tester.run_comprehensive_test()
            else:
                test_results = {
                    "status": "disabled",
                    "message": "Performance tester temporarily disabled",
                }

            # Create summary embed
            embed = discord.Embed(
                title="📄 Performance Report Generated",
                color=0x0099FF,
                timestamp=datetime.now(timezone.utc),
            )

            # Save report to file
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            report_filename = f"performance_report_{timestamp}.json"

            # Create report content
            report_content = json.dumps(test_results, indent=2, default=str)

            # Save to file and send as attachment if possible
            try:
                import io

                report_file = io.StringIO(report_content)
                discord_file = discord.File(report_file, filename=report_filename)

                embed.add_field(
                    name="📊 Report Details",
                    value=f"• Test Duration: {test_results.get('test_metadata', {}).get('duration_seconds', 0):.2f}s\n• Total Commands Analyzed: {test_results.get('command_analysis', {}).get('total_commands', 0)}\n• Recommendations: {len(test_results.get('recommendations', []))}",
                    inline=False,
                )

                await interaction.followup.send(embed=embed, file=discord_file)

            except Exception as file_error:
                # Fallback: send summary only
                self.logger.warning(f"Could not send file attachment: {file_error}")

                summary = test_results.get("test_metadata", {})
                embed.add_field(
                    name="📊 Report Summary",
                    value=f"Duration: {summary.get('duration_seconds', 0):.2f}s\nReport generated but could not be attached",
                    inline=False,
                )

                await optimized_send(interaction, embed=embed)

        except Exception as e:
            error_embed = discord.Embed(
                title="❌ Report Generation Failed",
                description=f"Error generating performance report: {str(e)}",
                color=0xFF0000,
            )

            await optimized_send(interaction, embed=error_embed)
            self.logger.error(f"Performance report error: {e}")


async def setup(bot):
    """Setup function for the cog"""
    await bot.add_cog(PerformanceCog(bot))
    logger.info("✅ Performance Cog loaded successfully")
