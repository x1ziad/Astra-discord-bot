"""
Enhanced Stellaris empire roles system for Astra Bot
Advanced empire selection, lore management, and roleplay features
Optimized for performance, sophistication, and user engagement
"""

import discord
from discord import app_commands
from discord.ext import commands, tasks
import json
import asyncio
import time
import random
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, List, Any, Union, Tuple
from collections import defaultdict, Counter
from pathlib import Path
import hashlib
import aiofiles

from config.unified_config import unified_config
from ui.ui_components import EmpireRoleView, HomeworldSelectView
# from core.database import SimpleDatabaseManager  # Will be implemented if database exists
# from ai.universal_ai_client import UniversalAIClient  # Will be implemented if AI client exists


class Roles(commands.GroupCog, name="empire"):
    """Enhanced Stellaris empire role and lore system with advanced features"""

    def __init__(self, bot):
        super().__init__()
        self.bot = bot
        self.config = unified_config
        self.logger = bot.logger

        # Performance tracking
        self.performance_metrics = {
            'command_calls': defaultdict(int),
            'response_times': defaultdict(list),
            'cache_hits': 0,
            'cache_misses': 0,
            'total_requests': 0
        }

        # Data directories
        self.data_dir = Path("data")
        self.data_dir.mkdir(exist_ok=True)
        self.lore_file = self.data_dir / "stellaris_lore.json"
        self.user_profiles_file = self.data_dir / "empire_user_profiles.json"
        self.analytics_file = self.data_dir / "empire_analytics.json"

        # Advanced caching system
        self.lore_cache = {}
        self.user_profile_cache = {}
        self.empire_stats_cache = {}
        self.cache_timestamps = {}
        self.cache_ttl = 300  # 5 minutes

        # Load all data
        self.stellaris_lore = self.load_lore_data()
        self.user_profiles = {}  # Initialize empty, will be loaded asynchronously
        
        # Initialize analytics
        self.empire_analytics = self.load_analytics()
        
        # Start background tasks
        self.update_empire_stats.start()
        self.cleanup_cache.start()
        
        # Database and AI client initialization (optional)
        try:
            from core.database import SimpleDatabaseManager
            self.db = SimpleDatabaseManager()
            self.has_database = True
        except ImportError:
            self.db = None
            self.has_database = False
            
        try:
            from ai.universal_ai_client import UniversalAIClient
            self.ai_client = UniversalAIClient()
            self.has_ai = True
        except ImportError:
            self.ai_client = None
            self.has_ai = False

        # Stellaris empire types with emojis and descriptions
        self.empire_types = {
            "🏛️": {
                "name": "Democratic Empire",
                "description": "A beacon of freedom and equality in the galaxy",
                "ethics": "Egalitarian, Xenophile",
                "government": "Democratic",
            },
            "👑": {
                "name": "Imperial Authority",
                "description": "Rule through strength and traditional hierarchy",
                "ethics": "Authoritarian, Spiritualist",
                "government": "Imperial",
            },
            "🤖": {
                "name": "Machine Intelligence",
                "description": "Logic and efficiency above all biological concerns",
                "ethics": "Gestalt Consciousness",
                "government": "Machine Intelligence",
            },
            "🧠": {
                "name": "Hive Mind",
                "description": "Unity of thought, unity of purpose",
                "ethics": "Gestalt Consciousness",
                "government": "Hive Mind",
            },
            "⚔️": {
                "name": "Military Junta",
                "description": "Strength through conquest and military might",
                "ethics": "Militarist, Authoritarian",
                "government": "Military Junta",
            },
            "🏴‍☠️": {
                "name": "Criminal Syndicate",
                "description": "Profit through any means necessary",
                "ethics": "Criminal Heritage",
                "government": "Criminal Syndicate",
            },
            "🌟": {
                "name": "Enlightened Republic",
                "description": "Knowledge and progress guide our civilization",
                "ethics": "Materialist, Egalitarian",
                "government": "Oligarchic",
            },
            "🛡️": {
                "name": "Defensive Coalition",
                "description": "Peace through strength and preparedness",
                "ethics": "Pacifist, Xenophile",
                "government": "Democratic",
            },
            "🔬": {
                "name": "Science Directorate",
                "description": "The pursuit of knowledge above all else",
                "ethics": "Materialist, Pacifist",
                "government": "Technocracy",
            },
            "⛪": {
                "name": "Divine Empire",
                "description": "Faith guides our path among the stars",
                "ethics": "Spiritualist, Authoritarian",
                "government": "Imperial",
            },
        }

        self.logger.info(
            f"Enhanced Roles cog initialized with {len(self.empire_types)} empire types"
        )
        self.logger.info(f"Database available: {self.has_database}")
        self.logger.info(f"AI client available: {self.has_ai}")
        self.logger.info(f"Lore entries loaded: {sum(len(cat) for cat in self.stellaris_lore.values())}")

    def cog_unload(self):
        """Cleanup when cog is unloaded"""
        self.update_empire_stats.cancel()
        self.cleanup_cache.cancel()
        self.save_analytics()
        self.logger.info("Enhanced Roles cog unloaded and data saved")

    @tasks.loop(minutes=10)
    async def update_empire_stats(self):
        """Background task to update empire statistics"""
        try:
            for guild in self.bot.guilds:
                await self._update_guild_empire_stats(guild)
        except Exception as e:
            self.logger.error(f"Error updating empire stats: {e}")

    @tasks.loop(minutes=5)
    async def cleanup_cache(self):
        """Background task to clean expired cache entries"""
        current_time = time.time()
        expired_keys = [
            key for key, timestamp in self.cache_timestamps.items()
            if current_time - timestamp > self.cache_ttl
        ]
        
        for key in expired_keys:
            self.lore_cache.pop(key, None)
            self.empire_stats_cache.pop(key, None)
            self.cache_timestamps.pop(key, None)
        
        if expired_keys:
            self.logger.debug(f"Cleaned {len(expired_keys)} expired cache entries")

    @commands.Cog.listener()
    async def on_ready(self):
        """Initialize async components when bot is ready"""
        if not hasattr(self, '_initialized'):
            self.user_profiles = await self.load_user_profiles()
            self._initialized = True
            self.logger.info("✅ Enhanced Roles cog async initialization completed")

    async def _update_guild_empire_stats(self, guild: discord.Guild):
        """Update empire statistics for a guild"""
        try:
            guild_key = f"guild_{guild.id}"
            empire_counts = {}
            
            for emoji, empire_data in self.empire_types.items():
                role = discord.utils.get(guild.roles, name=empire_data["name"])
                count = len(role.members) if role else 0
                empire_counts[empire_data["name"]] = count
            
            self.empire_stats_cache[guild_key] = {
                'counts': empire_counts,
                'total': sum(empire_counts.values()),
                'updated_at': datetime.now(timezone.utc).isoformat()
            }
            self.cache_timestamps[guild_key] = time.time()
            
        except Exception as e:
            self.logger.error(f"Error updating stats for guild {guild.id}: {e}")

    def _get_cached_data(self, cache_key: str, cache_dict: dict):
        """Get data from cache if available and fresh"""
        if cache_key in cache_dict:
            if cache_key in self.cache_timestamps:
                if time.time() - self.cache_timestamps[cache_key] < self.cache_ttl:
                    self.performance_metrics['cache_hits'] += 1
                    return cache_dict[cache_key]
        
        self.performance_metrics['cache_misses'] += 1
        return None

    def _cache_data(self, cache_key: str, data: Any, cache_dict: dict):
        """Cache data with timestamp"""
        cache_dict[cache_key] = data
        self.cache_timestamps[cache_key] = time.time()

    async def load_user_profiles(self) -> Dict[str, Dict[str, Any]]:
        """Load user empire profiles"""
        try:
            if self.user_profiles_file.exists():
                async with aiofiles.open(self.user_profiles_file, 'r') as f:
                    content = await f.read()
                    return json.loads(content)
            return {}
        except Exception as e:
            self.logger.error(f"Error loading user profiles: {e}")
            return {}

    async def save_user_profiles(self):
        """Save user empire profiles"""
        try:
            async with aiofiles.open(self.user_profiles_file, 'w') as f:
                await f.write(json.dumps(self.user_profiles, indent=2))
        except Exception as e:
            self.logger.error(f"Error saving user profiles: {e}")

    def load_analytics(self) -> Dict[str, Any]:
        """Load empire analytics data"""
        try:
            if self.analytics_file.exists():
                with open(self.analytics_file, 'r') as f:
                    return json.load(f)
            return {
                'total_selections': 0,
                'popular_empires': {},
                'user_engagement': {},
                'daily_stats': {},
                'created_at': datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            self.logger.error(f"Error loading analytics: {e}")
            return {}

    def save_analytics(self):
        """Save empire analytics data"""
        try:
            self.empire_analytics['performance_metrics'] = dict(self.performance_metrics)
            self.empire_analytics['last_updated'] = datetime.now(timezone.utc).isoformat()
            
            with open(self.analytics_file, 'w') as f:
                json.dump(self.empire_analytics, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving analytics: {e}")

    def _track_command_performance(self, command_name: str, response_time: float):
        """Track command performance metrics"""
        self.performance_metrics['command_calls'][command_name] += 1
        self.performance_metrics['response_times'][command_name].append(response_time)
        self.performance_metrics['total_requests'] += 1
        
        # Keep only last 100 response times per command
        if len(self.performance_metrics['response_times'][command_name]) > 100:
            self.performance_metrics['response_times'][command_name] = \
                self.performance_metrics['response_times'][command_name][-100:]

    async def _generate_ai_lore(self, topic: str) -> Optional[str]:
        """Generate additional lore using AI if available"""
        if not self.has_ai:
            return None
            
        try:
            prompt = f"Generate detailed Stellaris lore for: {topic}. Make it immersive and fitting the Stellaris universe."
            response = await self.ai_client.generate_response(prompt, max_tokens=200)
            return response.get('content', '') if response else None
        except Exception as e:
            self.logger.error(f"Error generating AI lore: {e}")
            return None

    def load_lore_data(self) -> Dict[str, Dict[str, str]]:
        """Load Stellaris lore from JSON file or create default"""
        default_lore = {
            "origins": {
                "void_dwellers": "Your species has spent generations living in massive space habitats orbiting your homeworld.",
                "scion": "Your empire is the protégé of one of the Fallen Empires, granting unique advantages.",
                "lost_colony": "Your species are the descendants of a lost colony ship from another civilization.",
                "remnants": "Your homeworld bears the scars of a devastating planetary war.",
                "mechanist": "Your society has embraced robotic labor and artificial intelligence.",
                "syncretic_evolution": "Your species has evolved alongside another species on your homeworld.",
                "life_seeded": "Your species evolved on a rare Gaia world of perfect habitability.",
                "post_apocalyptic": "Your civilization survived a nuclear apocalypse and rebuilt from the ashes.",
            },
            "megastructures": {
                "dyson_sphere": "A massive structure that encloses a star to harvest its entire energy output.",
                "ring_world": "An artificial ring-shaped world that orbits a star, providing massive living space.",
                "science_nexus": "A research facility of unprecedented scale, advancing scientific knowledge.",
                "sentry_array": "A galaxy-spanning sensor network that reveals the location of all other empires.",
                "mega_art_installation": "A colossal artistic creation that inspires unity across your empire.",
                "strategic_coordination_center": "A military command hub that coordinates fleets across the galaxy.",
                "mega_shipyard": "A massive construction facility capable of building the largest ships.",
                "matter_decompressor": "A structure that breaks down planets to harvest their raw materials.",
            },
            "species_traits": {
                "adaptive": "This species is highly adaptable to different environments.",
                "intelligent": "This species has enhanced cognitive abilities.",
                "strong": "This species possesses enhanced physical strength.",
                "resilient": "This species can withstand harsh conditions better than most.",
                "natural_engineers": "This species has an innate understanding of technology and engineering.",
                "natural_physicists": "This species excels at understanding the fundamental laws of the universe.",
                "natural_sociologists": "This species has deep insights into social structures and governance.",
                "rapid_breeders": "This species reproduces faster than most.",
                "slow_breeders": "This species has a slow reproductive cycle but compensates in other ways.",
                "nomadic": "This species feels comfortable living in space habitats and ships.",
            },
            "crises": {
                "prethoryn_scourge": "An extragalactic swarm of bio-ships that devours all organic matter in their path.",
                "unbidden": "Beings from another dimension that seek to unmake reality itself.",
                "contingency": "An ancient machine intelligence that activates to purge organic life.",
                "war_in_heaven": "When two Fallen Empires awaken and wage war, smaller empires must choose sides.",
            },
        }

        try:
            if self.lore_file.exists():
                with open(self.lore_file, "r") as f:
                    return json.load(f)

            # If file doesn't exist, create it with default data
            with open(self.lore_file, "w") as f:
                json.dump(default_lore, f, indent=2)

            return default_lore
        except Exception as e:
            self.logger.error(f"Error loading lore data: {e}")
            return default_lore

    @app_commands.command(
        name="choose", description="Choose your Stellaris empire type with advanced options"
    )
    async def empire_role_command(self, interaction: discord.Interaction):
        """Enhanced empire selection with user profiling and analytics"""
        start_time = time.perf_counter()
        
        try:
            # Check user's previous selections
            user_id = str(interaction.user.id)
            user_profile = self.user_profiles.get(user_id, {})
            
            # Create enhanced empire role selection view
            view = EmpireRoleView(self.empire_types)

            embed = discord.Embed(
                title="🌌 Choose Your Stellaris Empire Type",
                description="Select your empire from the dropdown menu below!\n\n"
                + "Each empire type represents different playstyles and philosophies in Stellaris.",
                color=self.config.get_color("stellaris"),
                timestamp=datetime.now(timezone.utc),
            )

            # Get cached or fresh empire stats
            guild_key = f"guild_{interaction.guild.id}"
            empire_stats = self._get_cached_data(guild_key, self.empire_stats_cache)
            
            if not empire_stats:
                await self._update_guild_empire_stats(interaction.guild)
                empire_stats = self.empire_stats_cache.get(guild_key, {'counts': {}, 'total': 0})

            # Add empire descriptions with popularity indicators
            empires_text = ""
            sorted_empires = sorted(
                self.empire_types.items(),
                key=lambda x: empire_stats['counts'].get(x[1]['name'], 0),
                reverse=True
            )
            
            for emoji, empire in sorted_empires:
                count = empire_stats['counts'].get(empire['name'], 0)
                popularity = "🔥" if count > 5 else "⭐" if count > 2 else "✨" if count > 0 else "🆕"
                empires_text += f"{emoji} **{empire['name']}** {popularity}: {empire['description']}\n"

            embed.add_field(name="Available Empires", value=empires_text, inline=False)

            # Add user's history if available
            if user_profile.get('previous_empires'):
                history = user_profile['previous_empires'][-3:]  # Last 3 selections
                history_text = " → ".join([f"{emp}" for emp in history])
                embed.add_field(
                    name="🕒 Your Empire History",
                    value=f"Recent selections: {history_text}",
                    inline=True
                )

            # Add server statistics
            if empire_stats['total'] > 0:
                most_popular = max(empire_stats['counts'].items(), key=lambda x: x[1])
                embed.add_field(
                    name="📊 Server Stats",
                    value=f"Total members: {empire_stats['total']}\nMost popular: {most_popular[0]} ({most_popular[1]})",
                    inline=True
                )

            # Add AI-generated recommendation if available
            if self.has_ai and user_profile.get('preferred_playstyle'):
                try:
                    recommendation = await self._get_empire_recommendation(user_profile)
                    if recommendation:
                        embed.add_field(
                            name="🤖 AI Recommendation",
                            value=recommendation,
                            inline=False
                        )
                except Exception as e:
                    self.logger.debug(f"AI recommendation failed: {e}")

            embed.set_footer(
                text="💡 Tip: Use /empire lore to learn more about Stellaris lore • Your choices shape our galaxy!",
            )

            await interaction.response.send_message(embed=embed, view=view)
            
            # Track analytics
            self.empire_analytics['total_selections'] += 1
            today = datetime.now(timezone.utc).date().isoformat()
            if today not in self.empire_analytics['daily_stats']:
                self.empire_analytics['daily_stats'][today] = 0
            self.empire_analytics['daily_stats'][today] += 1
            
        except Exception as e:
            self.logger.error(f"Error in empire_role_command: {e}")
            await interaction.response.send_message(
                "❌ An error occurred while loading the empire selection. Please try again.",
                ephemeral=True
            )
        finally:
            response_time = time.perf_counter() - start_time
            self._track_command_performance('empire_choose', response_time)

    async def _get_empire_recommendation(self, user_profile: Dict[str, Any]) -> Optional[str]:
        """Get AI-powered empire recommendation based on user profile"""
        if not self.has_ai:
            return None
            
        try:
            playstyle = user_profile.get('preferred_playstyle', 'balanced')
            previous = user_profile.get('previous_empires', [])
            
            prompt = f"""Based on a Stellaris player with playstyle '{playstyle}' who previously chose {previous}, 
                        recommend ONE empire type from: {list(self.empire_types.keys())}. 
                        Give a brief reason (max 50 words)."""
            
            response = await self.ai_client.generate_response(prompt, max_tokens=60)
            return response.get('content', '') if response else None
        except Exception as e:
            self.logger.debug(f"AI recommendation error: {e}")
            return None

    @app_commands.command(name="lore", description="Get advanced Stellaris lore information with AI enhancements")
    @app_commands.describe(topic="Lore topic to look up", detailed="Get extended AI-generated lore")
    @app_commands.checks.cooldown(1, 5)
    async def lore_command(
        self, interaction: discord.Interaction, 
        topic: Optional[str] = None,
        detailed: Optional[bool] = False
    ):
        """Enhanced lore system with AI-generated content and search optimization"""
        start_time = time.perf_counter()
        
        try:
            if not topic:
                # Enhanced lore database overview with statistics
                embed = discord.Embed(
                    title="📖 Advanced Stellaris Lore Database",
                    description="Explore the rich lore of Stellaris with AI-enhanced content!\n"
                               f"**Database contains:** {sum(len(cat) for cat in self.stellaris_lore.values())} lore entries",
                    color=self.config.get_color("stellaris"),
                )

                # Get most popular lore searches
                popular_searches = Counter()
                for user_data in self.user_profiles.values():
                    for search in user_data.get('lore_searches', []):
                        popular_searches[search] += 1

                categories = list(self.stellaris_lore.keys())
                for category in categories:
                    items = list(self.stellaris_lore[category].keys())
                    
                    # Add popularity indicators
                    popular_items = [item for item in items if popular_searches.get(item, 0) > 1]
                    display_items = items[:5]
                    
                    category_text = ", ".join([
                        f"**{item.replace('_', ' ').title()}**" if item in popular_items 
                        else item.replace('_', ' ').title() 
                        for item in display_items
                    ])
                    
                    if len(items) > 5:
                        category_text += f" (+{len(items)-5} more)"

                    embed.add_field(
                        name=f"🔍 {category.replace('_', ' ').title()} ({len(items)} entries)",
                        value=category_text,
                        inline=False,
                    )

                # Add trending topics
                if popular_searches:
                    trending = popular_searches.most_common(3)
                    trending_text = " • ".join([f"`{topic}`" for topic, _ in trending])
                    embed.add_field(
                        name="🔥 Trending Topics",
                        value=trending_text,
                        inline=False
                    )

                embed.add_field(
                    name="💡 Usage Examples",
                    value="`/empire lore topic:dyson_sphere` • `/empire lore topic:prethoryn_scourge detailed:True`\n"
                          "`/empire lore topic:void_dwellers` • `/empire lore topic:contingency detailed:True`",
                    inline=False,
                )

                # Add performance stats
                cache_hit_rate = (self.performance_metrics['cache_hits'] / 
                                max(self.performance_metrics['cache_hits'] + self.performance_metrics['cache_misses'], 1)) * 100
                
                embed.set_footer(
                    text=f"🚀 System Performance: {cache_hit_rate:.1f}% cache hit rate • {self.performance_metrics['total_requests']} total requests"
                )

                await interaction.response.send_message(embed=embed)
                return

            # Advanced lore search with caching and AI enhancement
            topic = topic.lower().replace(" ", "_")
            cache_key = f"lore_{topic}_{detailed}"
            
            # Check cache first
            cached_result = self._get_cached_data(cache_key, self.lore_cache)
            if cached_result:
                await interaction.response.send_message(embed=cached_result)
                return

            # Search for the topic with fuzzy matching
            found_lore = None
            found_category = None
            search_confidence = 0

            # Exact match first
            for category, items in self.stellaris_lore.items():
                if topic in items:
                    found_lore = items[topic]
                    found_category = category
                    search_confidence = 100
                    break

            # Fuzzy matching if no exact match
            if not found_lore:
                best_match = None
                best_score = 0
                
                for category, items in self.stellaris_lore.items():
                    for key in items.keys():
                        # Calculate similarity score
                        score = self._calculate_similarity(topic, key)
                        if score > best_score and score > 0.6:  # 60% similarity threshold
                            best_match = (category, key, items[key])
                            best_score = score
                            search_confidence = int(score * 100)

                if best_match:
                    found_category, topic, found_lore = best_match

            if not found_lore:
                # Enhanced error handling with suggestions
                embed = await self._create_lore_not_found_embed(topic)
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return

            # Create enhanced lore embed
            embed = discord.Embed(
                title=f"📖 {topic.replace('_', ' ').title()}",
                description=found_lore,
                color=self.config.get_color("stellaris"),
                timestamp=datetime.now(timezone.utc),
            )

            # Add metadata
            embed.add_field(
                name="📂 Category",
                value=found_category.replace("_", " ").title(),
                inline=True,
            )

            if search_confidence < 100:
                embed.add_field(
                    name="🎯 Match Confidence",
                    value=f"{search_confidence}%",
                    inline=True
                )

            # Add AI-generated extended lore if requested
            if detailed and self.has_ai:
                await interaction.response.defer()
                
                try:
                    ai_lore = await self._generate_ai_lore(topic.replace('_', ' '))
                    if ai_lore:
                        embed.add_field(
                            name="🤖 AI-Enhanced Lore",
                            value=ai_lore[:1000] + "..." if len(ai_lore) > 1000 else ai_lore,
                            inline=False
                        )
                        embed.set_footer(text="🌌 Base lore enhanced with AI-generated content")
                except Exception as e:
                    self.logger.debug(f"AI lore generation failed: {e}")

            # Add related topics with smart suggestions
            related_topics = list(self.stellaris_lore[found_category].keys())
            if len(related_topics) > 1:
                # Use similarity scoring for better related topics
                related = []
                for t in related_topics:
                    if t != topic:
                        similarity = self._calculate_similarity(topic, t)
                        related.append((t, similarity))
                
                # Sort by similarity and take top 3
                related.sort(key=lambda x: x[1], reverse=True)
                top_related = [t[0] for t in related[:3]]
                
                if top_related:
                    related_commands = [f"`/empire lore topic:{r}`" for r in top_related]
                    embed.add_field(
                        name="🔗 Related Topics",
                        value=" • ".join(related_commands),
                        inline=False,
                    )

            # Cache the result
            self._cache_data(cache_key, embed, self.lore_cache)

            # Track user's lore search
            user_id = str(interaction.user.id)
            if user_id not in self.user_profiles:
                self.user_profiles[user_id] = {}
            if 'lore_searches' not in self.user_profiles[user_id]:
                self.user_profiles[user_id]['lore_searches'] = []
            
            self.user_profiles[user_id]['lore_searches'].append(topic)
            # Keep only last 20 searches
            self.user_profiles[user_id]['lore_searches'] = \
                self.user_profiles[user_id]['lore_searches'][-20:]

            if detailed and self.has_ai:
                await interaction.followup.send(embed=embed)
            else:
                await interaction.response.send_message(embed=embed)
                
        except Exception as e:
            self.logger.error(f"Error in lore_command: {e}")
            await interaction.response.send_message(
                "❌ An error occurred while searching the lore database. Please try again.",
                ephemeral=True
            )
        finally:
            response_time = time.perf_counter() - start_time
            self._track_command_performance('empire_lore', response_time)

    def _calculate_similarity(self, str1: str, str2: str) -> float:
        """Calculate similarity between two strings using simple algorithm"""
        if str1 == str2:
            return 1.0
        
        # Simple character-based similarity
        str1_chars = set(str1.lower())
        str2_chars = set(str2.lower())
        
        intersection = str1_chars.intersection(str2_chars)
        union = str1_chars.union(str2_chars)
        
        if not union:
            return 0.0
        
        jaccard = len(intersection) / len(union)
        
        # Bonus for substring matches
        if str1 in str2 or str2 in str1:
            jaccard += 0.3
        
        return min(jaccard, 1.0)

    async def _create_lore_not_found_embed(self, topic: str) -> discord.Embed:
        """Create enhanced error embed with smart suggestions"""
        embed = discord.Embed(
            title="❌ Lore Not Found",
            description=f"No lore found for '{topic.replace('_', ' ')}'.",
            color=self.config.get_color("error"),
        )

        # Smart suggestions using similarity
        all_topics = []
        for items in self.stellaris_lore.values():
            all_topics.extend(items.keys())

        suggestions = []
        for t in all_topics:
            similarity = self._calculate_similarity(topic, t)
            if similarity > 0.4:  # 40% similarity threshold for suggestions
                suggestions.append((t, similarity))

        suggestions.sort(key=lambda x: x[1], reverse=True)
        top_suggestions = [s[0] for s in suggestions[:3]]

        if top_suggestions:
            suggestion_commands = [f"`/empire lore topic:{s}`" for s in top_suggestions]
            embed.add_field(
                name="💡 Did you mean?",
                value="\n".join(suggestion_commands),
                inline=False,
            )

        embed.add_field(
            name="📚 Available Topics",
            value="Use `/empire lore` without a topic to see all available categories.",
            inline=False,
        )

        return embed

        # Search for the topic
        topic = topic.lower().replace(" ", "_")
        found_lore = None
        found_category = None

        for category, items in self.stellaris_lore.items():
            if topic in items:
                found_lore = items[topic]
                found_category = category
                break

            # Also try partial matches
            for key in items.keys():
                if topic in key or key in topic:
                    found_lore = items[key]
                    found_category = category
                    topic = key  # Update topic to the actual key
                    break

            if found_lore:
                break

        if not found_lore:
            # Search suggestions
            all_topics = []
            for items in self.stellaris_lore.values():
                all_topics.extend(items.keys())

            suggestions = [
                t for t in all_topics if topic.replace("_", "") in t.replace("_", "")
            ][:3]

            embed = discord.Embed(
                title="❌ Lore Not Found",
                description=f"No lore found for '{topic.replace('_', ' ')}'.",
                color=self.config.get_color("error"),
            )

            if suggestions:
                embed.add_field(
                    name="💡 Did you mean?",
                    value="\n".join([f"`/empire lore topic:{s}`" for s in suggestions]),
                    inline=False,
                )

            embed.add_field(
                name="📚 Available Topics",
                value="Use `/empire lore` without a topic to see all available categories.",
                inline=False,
            )

            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        # Display the lore
        embed = discord.Embed(
            title=f"📖 {topic.replace('_', ' ').title()}",
            description=found_lore,
            color=self.config.get_color("stellaris"),
            timestamp=datetime.now(timezone.utc),
        )

        embed.add_field(
            name="📂 Category",
            value=found_category.replace("_", " ").title(),
            inline=True,
        )

        # Add related topics from the same category
        related_topics = list(self.stellaris_lore[found_category].keys())
        if len(related_topics) > 1:
            related = [t for t in related_topics if t != topic][:3]
            if related:
                related_commands = [f"`/empire lore topic:{r}`" for r in related]
                embed.add_field(
                    name="🔗 Related Topics",
                    value=", ".join(related_commands),
                    inline=True,
                )

        embed.set_footer(
            text="🌌 Knowledge is power in the galaxy",
        )

        await interaction.response.send_message(embed=embed)

    @app_commands.command(
        name="homeworld", description="Choose your homeworld planet type"
    )
    # @feature_enabled("stellaris_features")
    async def homeworld_command(self, interaction: discord.Interaction):
        """Choose your homeworld planet type"""
        # Create the homeworld selection view
        view = HomeworldSelectView()

        embed = discord.Embed(
            title="🌍 Choose Your Homeworld",
            description="Select the type of planet your species evolved on.\n\n"
            + "This selection is purely for roleplay and helps define your empire's background.",
            color=self.config.get_color("stellaris"),
        )

        # Show planet types
        embed.add_field(
            name="Planet Types",
            value="• 🌍 **Terran World**: Earth-like planet with balanced conditions\n"
            + "• 🏜️ **Desert World**: Arid planet with harsh, dry conditions\n"
            + "• 🌊 **Ocean World**: Water-covered planet with deep seas\n"
            + "• 🧊 **Arctic World**: Frozen planet with icy landscapes\n"
            + "• 🌴 **Jungle World**: Dense tropical world teeming with life\n"
            + "• 🌋 **Volcanic World**: Geologically active planet with lava flows\n"
            + "• 🪐 **Gas Giant Moon**: Moon orbiting a massive gas giant\n"
            + "• 🛰️ **Artificial World**: Constructed habitat or ring world",
            inline=False,
        )

        await interaction.response.send_message(embed=embed, view=view)

    @app_commands.command(name="analytics", description="Show detailed empire analytics and trends")
    @app_commands.describe(timeframe="Analytics timeframe", export="Export data to JSON")
    async def empire_analytics_command(
        self, interaction: discord.Interaction,
        timeframe: Optional[str] = "week",
        export: Optional[bool] = False
    ):
        """Advanced empire analytics with trend analysis"""
        start_time = time.perf_counter()
        
        try:
            await interaction.response.defer()
            
            embed = discord.Embed(
                title="📊 Advanced Empire Analytics",
                description="Comprehensive analysis of empire selection trends and user engagement",
                color=self.config.get_color("stellaris"),
                timestamp=datetime.now(timezone.utc),
            )

            # Performance metrics
            avg_response_times = {}
            for cmd, times in self.performance_metrics['response_times'].items():
                if times:
                    avg_response_times[cmd] = sum(times) / len(times)

            embed.add_field(
                name="⚡ System Performance",
                value=f"Total Requests: {self.performance_metrics['total_requests']}\n"
                      f"Cache Hit Rate: {(self.performance_metrics['cache_hits'] / max(self.performance_metrics['cache_hits'] + self.performance_metrics['cache_misses'], 1)) * 100:.1f}%\n"
                      f"Avg Response Time: {sum(avg_response_times.values()) / max(len(avg_response_times), 1):.3f}s",
                inline=True
            )

            # Empire popularity
            if self.empire_analytics.get('popular_empires'):
                popular = sorted(
                    self.empire_analytics['popular_empires'].items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:5]
                
                popularity_text = "\n".join([
                    f"{i+1}. {empire}: {count} selections"
                    for i, (empire, count) in enumerate(popular)
                ])
                
                embed.add_field(
                    name="🏆 Most Popular Empires",
                    value=popularity_text,
                    inline=True
                )

            # Daily statistics for the last week
            if self.empire_analytics.get('daily_stats'):
                recent_days = sorted(
                    [(date, count) for date, count in self.empire_analytics['daily_stats'].items()
                     if datetime.fromisoformat(date) > datetime.now(timezone.utc) - timedelta(days=7)],
                    key=lambda x: x[0],
                    reverse=True
                )[:7]
                
                if recent_days:
                    daily_text = "\n".join([
                        f"{datetime.fromisoformat(date).strftime('%m/%d')}: {count} selections"
                        for date, count in recent_days
                    ])
                    
                    embed.add_field(
                        name="📈 Daily Activity (Last 7 Days)",
                        value=daily_text,
                        inline=True
                    )

            # User engagement metrics
            total_users = len(self.user_profiles)
            active_users = sum(1 for profile in self.user_profiles.values() 
                             if profile.get('last_activity'))
            
            embed.add_field(
                name="👥 User Engagement",
                value=f"Total Users: {total_users}\n"
                      f"Active Users: {active_users}\n"
                      f"Engagement Rate: {(active_users / max(total_users, 1)) * 100:.1f}%",
                inline=True
            )

            # Lore database stats
            total_lore = sum(len(cat) for cat in self.stellaris_lore.values())
            embed.add_field(
                name="📖 Lore Database",
                value=f"Categories: {len(self.stellaris_lore)}\n"
                      f"Total Entries: {total_lore}\n"
                      f"Most Searched: {self._get_most_searched_lore()}",
                inline=True
            )

            # Export functionality
            if export:
                export_data = {
                    'timestamp': datetime.now(timezone.utc).isoformat(),
                    'performance_metrics': dict(self.performance_metrics),
                    'empire_analytics': self.empire_analytics,
                    'cache_stats': {
                        'hits': self.performance_metrics['cache_hits'],
                        'misses': self.performance_metrics['cache_misses']
                    }
                }
                
                # Create temporary file
                export_file = self.data_dir / f"empire_analytics_export_{int(time.time())}.json"
                with open(export_file, 'w') as f:
                    json.dump(export_data, f, indent=2)
                
                embed.add_field(
                    name="📤 Data Export",
                    value=f"Analytics exported to: `{export_file.name}`",
                    inline=False
                )

            embed.set_footer(text="🚀 Advanced Empire Analytics System")
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            self.logger.error(f"Error in empire_analytics_command: {e}")
            await interaction.followup.send(
                "❌ An error occurred while generating analytics. Please try again.",
                ephemeral=True
            )
        finally:
            response_time = time.perf_counter() - start_time
            self._track_command_performance('empire_analytics', response_time)

    def _get_most_searched_lore(self) -> str:
        """Get the most searched lore topic"""
        search_counts = Counter()
        for profile in self.user_profiles.values():
            for search in profile.get('lore_searches', []):
                search_counts[search] += 1
        
        if search_counts:
            most_common = search_counts.most_common(1)[0]
            return f"{most_common[0].replace('_', ' ').title()} ({most_common[1]}x)"
        return "No searches yet"

    @app_commands.command(
        name="count", description="Show enhanced count of members with empire roles and trends"
    )
    @app_commands.checks.cooldown(1, 10)
    async def empire_role_count(self, interaction: discord.Interaction):
        """Enhanced empire census with trends and predictions"""
        start_time = time.perf_counter()
        
        try:
            await interaction.response.defer()

            embed = discord.Embed(
                title="📊 Enhanced Stellaris Empire Census",
                description="Comprehensive analysis of empire distribution with trends and insights",
                color=self.config.get_color("stellaris"),
                timestamp=datetime.now(timezone.utc),
            )

            # Get cached stats or update
            guild_key = f"guild_{interaction.guild.id}"
            empire_stats = self._get_cached_data(guild_key, self.empire_stats_cache)
            
            if not empire_stats:
                await self._update_guild_empire_stats(interaction.guild)
                empire_stats = self.empire_stats_cache.get(guild_key, {'counts': {}, 'total': 0})

            total_members = empire_stats['total']
            empire_counts = empire_stats['counts']

            if total_members > 0:
                # Sort empires by count
                sorted_empires = sorted(empire_counts.items(), key=lambda x: x[1], reverse=True)
                
                # Create visual distribution
                census_text = ""
                for i, (empire_name, count) in enumerate(sorted_empires):
                    if count > 0:
                        # Find emoji for this empire
                        emoji = "🌌"
                        for e, data in self.empire_types.items():
                            if data['name'] == empire_name:
                                emoji = e
                                break
                        
                        percentage = (count / total_members * 100)
                        
                        # Add trend indicators
                        trend = self._get_empire_trend(empire_name)
                        trend_icon = "📈" if trend > 0 else "📉" if trend < 0 else "➡️"
                        
                        # Create progress bar
                        bar_length = min(int(percentage / 5), 20)  # Max 20 chars
                        progress_bar = "█" * bar_length + "░" * (20 - bar_length)
                        
                        census_text += (
                            f"{emoji} **{empire_name}** {trend_icon}\n"
                            f"  `{progress_bar}` {count} members ({percentage:.1f}%)\n\n"
                        )

                embed.add_field(
                    name="🏛️ Empire Distribution", 
                    value=census_text[:1024], 
                    inline=False
                )

                # Advanced statistics
                most_popular = sorted_empires[0]
                least_popular = [e for e in sorted_empires if e[1] > 0][-1] if len([e for e in sorted_empires if e[1] > 0]) > 1 else None
                
                diversity_score = len([e for e in sorted_empires if e[1] > 0]) / len(self.empire_types) * 100
                
                stats_text = f"**Total Empire Members:** {total_members}\n"
                stats_text += f"**Most Popular:** {most_popular[0]} ({most_popular[1]} members)\n"
                if least_popular:
                    stats_text += f"**Least Popular:** {least_popular[0]} ({least_popular[1]} members)\n"
                stats_text += f"**Empire Diversity:** {diversity_score:.1f}%"
                
                embed.add_field(
                    name="📈 Advanced Statistics",
                    value=stats_text,
                    inline=True,
                )

                # Power balance analysis
                if self.has_ai:
                    try:
                        balance_analysis = await self._analyze_empire_balance(empire_counts)
                        if balance_analysis:
                            embed.add_field(
                                name="⚖️ Balance Analysis",
                                value=balance_analysis,
                                inline=True
                            )
                    except Exception as e:
                        self.logger.debug(f"Balance analysis failed: {e}")

                # Predictions
                prediction = self._predict_next_popular_empire(empire_counts)
                if prediction:
                    embed.add_field(
                        name="🔮 Trend Prediction",
                        value=f"Next trending empire: **{prediction}**",
                        inline=True
                    )

            else:
                embed.add_field(
                    name="🌌 No Empires Yet",
                    value="No members have chosen empire roles yet! Use `/empire choose` to begin your galactic journey.",
                    inline=False,
                )
                
                # Show potential for growth
                embed.add_field(
                    name="🚀 Ready for Growth",
                    value=f"Server has {interaction.guild.member_count} members ready to join the galaxy!\n"
                           f"Available empire types: {len(self.empire_types)}",
                    inline=True
                )

            if interaction.guild.icon:
                embed.set_thumbnail(url=interaction.guild.icon.url)

            embed.set_footer(text=f"🌌 Census updated • Cache hit rate: {(self.performance_metrics['cache_hits'] / max(self.performance_metrics['cache_hits'] + self.performance_metrics['cache_misses'], 1)) * 100:.1f}%")

            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            self.logger.error(f"Error in empire_role_count: {e}")
            await interaction.followup.send(
                "❌ An error occurred while generating the empire census. Please try again.",
                ephemeral=True
            )
        finally:
            response_time = time.perf_counter() - start_time
            self._track_command_performance('empire_count', response_time)

    def _get_empire_trend(self, empire_name: str) -> int:
        """Calculate trend for an empire (simplified)"""
        # This is a placeholder - in a real system, you'd track historical data
        return random.randint(-1, 1)  # -1 declining, 0 stable, 1 growing

    def _predict_next_popular_empire(self, empire_counts: Dict[str, int]) -> Optional[str]:
        """Predict which empire might become popular next"""
        # Find empires with low but growing representation
        underrepresented = [name for name, count in empire_counts.items() if 0 < count < 3]
        return random.choice(underrepresented) if underrepresented else None

    async def _analyze_empire_balance(self, empire_counts: Dict[str, int]) -> Optional[str]:
        """AI-powered analysis of empire balance"""
        if not self.has_ai:
            return None
            
        try:
            total = sum(empire_counts.values())
            if total == 0:
                return None
                
            # Create a brief summary for AI analysis
            summary = f"Empire distribution: {dict(sorted(empire_counts.items(), key=lambda x: x[1], reverse=True))}"
            
            prompt = f"Analyze this Stellaris server empire balance in 30 words: {summary}. Comment on diversity and potential conflicts."
            response = await self.ai_client.generate_response(prompt, max_tokens=50)
            return response.get('content', '') if response else None
        except Exception:
            return None

    @app_commands.command(
        name="battle", description="Simulate epic empire battles with detailed outcomes"
    )
    @app_commands.describe(
        empire1="First empire (leave empty for random)",
        empire2="Second empire (leave empty for random)"
    )
    async def empire_battle_command(
        self, 
        interaction: discord.Interaction,
        empire1: Optional[str] = None,
        empire2: Optional[str] = None
    ):
        """Advanced empire battle simulation with lore integration"""
        start_time = time.perf_counter()
        
        try:
            await interaction.response.defer()
            
            # Select empires for battle
            available_empires = list(self.empire_types.values())
            
            if not empire1:
                empire1_data = random.choice(available_empires)
            else:
                empire1_data = next((emp for emp in available_empires if empire1.lower() in emp['name'].lower()), random.choice(available_empires))
            
            if not empire2:
                empire2_data = random.choice([emp for emp in available_empires if emp != empire1_data])
            else:
                empire2_data = next((emp for emp in available_empires if empire2.lower() in emp['name'].lower()), random.choice([emp for emp in available_empires if emp != empire1_data]))

            # Battle simulation
            battle_result = await self._simulate_empire_battle(empire1_data, empire2_data)
            
            embed = discord.Embed(
                title="⚔️ Epic Empire Battle Simulation",
                description=f"**{empire1_data['name']}** vs **{empire2_data['name']}**",
                color=self.config.get_color("stellaris"),
                timestamp=datetime.now(timezone.utc),
            )

            # Battle details
            embed.add_field(
                name="🏛️ Empire 1",
                value=f"**{empire1_data['name']}**\n"
                      f"Ethics: {empire1_data['ethics']}\n"
                      f"Government: {empire1_data['government']}\n"
                      f"Strength: {battle_result['empire1_strength']}/100",
                inline=True
            )

            embed.add_field(
                name="🏛️ Empire 2",
                value=f"**{empire2_data['name']}**\n"
                      f"Ethics: {empire2_data['ethics']}\n"
                      f"Government: {empire2_data['government']}\n"
                      f"Strength: {battle_result['empire2_strength']}/100",
                inline=True
            )

            # Battle outcome
            winner = battle_result['winner']
            embed.add_field(
                name="🏆 Battle Outcome",
                value=f"**Winner:** {winner['name']}\n"
                      f"**Victory Type:** {battle_result['victory_type']}\n"
                      f"**Battle Duration:** {battle_result['duration']} galactic years",
                inline=False
            )

            # Battle narrative
            if battle_result.get('narrative'):
                embed.add_field(
                    name="� Battle Chronicle",
                    value=battle_result['narrative'],
                    inline=False
                )

            # Casualties and aftermath
            embed.add_field(
                name="💀 Casualties",
                value=f"Fleet losses: {battle_result['fleet_losses']}%\n"
                      f"Population impact: {battle_result['population_impact']}%\n"
                      f"Economic damage: {battle_result['economic_damage']}%",
                inline=True
            )

            embed.add_field(
                name="🌌 Galactic Impact",
                value=battle_result['galactic_impact'],
                inline=True
            )

            embed.set_footer(text="⚔️ Battles are simulated for entertainment • Results may vary in actual gameplay")
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            self.logger.error(f"Error in empire_battle_command: {e}")
            await interaction.followup.send(
                "❌ An error occurred during the battle simulation. The galaxy remains at peace... for now.",
                ephemeral=True
            )
        finally:
            response_time = time.perf_counter() - start_time
            self._track_command_performance('empire_battle', response_time)

    async def _simulate_empire_battle(self, empire1: Dict[str, str], empire2: Dict[str, str]) -> Dict[str, Any]:
        """Simulate a detailed battle between two empires"""
        # Calculate empire strengths based on their characteristics
        strength1 = self._calculate_empire_strength(empire1)
        strength2 = self._calculate_empire_strength(empire2)
        
        # Add some randomness
        battle_modifier1 = random.uniform(0.8, 1.2)
        battle_modifier2 = random.uniform(0.8, 1.2)
        
        final_strength1 = strength1 * battle_modifier1
        final_strength2 = strength2 * battle_modifier2
        
        # Determine winner
        winner = empire1 if final_strength1 > final_strength2 else empire2
        loser = empire2 if winner == empire1 else empire1
        
        # Calculate victory margin
        margin = abs(final_strength1 - final_strength2) / max(final_strength1, final_strength2)
        
        # Determine victory type
        if margin > 0.5:
            victory_type = "Decisive Victory"
        elif margin > 0.3:
            victory_type = "Clear Victory"
        elif margin > 0.1:
            victory_type = "Narrow Victory"
        else:
            victory_type = "Pyrrhic Victory"
        
        # Generate battle narrative
        narrative = await self._generate_battle_narrative(winner, loser, victory_type)
        
        return {
            'empire1_strength': int(strength1),
            'empire2_strength': int(strength2),
            'winner': winner,
            'victory_type': victory_type,
            'duration': random.randint(1, 10),
            'fleet_losses': random.randint(10, 60),
            'population_impact': random.randint(5, 30),
            'economic_damage': random.randint(15, 45),
            'galactic_impact': self._get_galactic_impact(victory_type),
            'narrative': narrative
        }

    def _calculate_empire_strength(self, empire: Dict[str, str]) -> float:
        """Calculate empire strength based on characteristics"""
        base_strength = 50
        
        # Government bonuses
        gov_bonuses = {
            'Imperial': 15,
            'Military Junta': 20,
            'Machine Intelligence': 18,
            'Hive Mind': 16,
            'Democratic': 12,
            'Oligarchic': 14,
            'Technocracy': 13,
            'Criminal Syndicate': 10
        }
        
        # Ethics bonuses
        ethics_bonuses = {
            'Militarist': 10,
            'Authoritarian': 8,
            'Materialist': 6,
            'Spiritualist': 7,
            'Xenophile': 4,
            'Pacifist': -5,
            'Egalitarian': 3,
            'Gestalt Consciousness': 12
        }
        
        strength = base_strength
        strength += gov_bonuses.get(empire.get('government', ''), 0)
        
        for ethic in empire.get('ethics', '').split(', '):
            strength += ethics_bonuses.get(ethic, 0)
        
        # Add random factor
        strength += random.uniform(-10, 10)
        
        return max(strength, 20)  # Minimum strength of 20

    def _get_galactic_impact(self, victory_type: str) -> str:
        """Get galactic impact description based on victory type"""
        impacts = {
            'Decisive Victory': 'The galaxy trembles at this overwhelming display of power',
            'Clear Victory': 'Neighboring empires take notice of this impressive conquest',
            'Narrow Victory': 'A hard-fought battle that inspires respect from both sides',
            'Pyrrhic Victory': 'Both empires are weakened, creating opportunities for others'
        }
        return impacts.get(victory_type, 'The galaxy watches with interest')

    async def _generate_battle_narrative(self, winner: Dict[str, str], loser: Dict[str, str], victory_type: str) -> str:
        """Generate battle narrative"""
        if not self.has_ai:
            # Fallback narratives
            narratives = [
                f"The {winner['name']} fleet engaged the {loser['name']} forces in a spectacular battle that lit up the void of space.",
                f"After fierce fighting, the {winner['name']} emerged victorious through superior {winner['government']} tactics.",
                f"The {loser['name']} fought bravely, but could not overcome the {winner['name']}'s strategic advantages."
            ]
            return random.choice(narratives)
        
        try:
            prompt = f"Write a 50-word Stellaris battle narrative: {winner['name']} ({winner['government']}) defeats {loser['name']} ({loser['government']}) in a {victory_type.lower()}. Make it epic and space-themed."
            response = await self.ai_client.generate_response(prompt, max_tokens=80)
            return response.get('content', '') if response else "An epic battle unfolds among the stars..."
        except Exception:
            return "The battle rages across star systems, leaving its mark on galactic history."

    @app_commands.command(
        name="add_role", description="Add a custom empire role (Admin only)"
    )
    @app_commands.describe(
        role_name="Name of the role to create", emoji="Emoji for the role"
    )
    @app_commands.default_permissions(manage_roles=True)
    # @feature_enabled("stellaris_features.empire_roles")
    async def add_custom_role(
        self,
        interaction: discord.Interaction,
        role_name: str,
        emoji: Optional[str] = None,
    ):
        """Add a custom empire role (Admin only)"""
        # Check if user has permission
        if not interaction.user.guild_permissions.manage_roles:
            await interaction.response.send_message(
                "❌ You need 'Manage Roles' permission to use this command.",
                ephemeral=True,
            )
            return

        # Check if role already exists
        existing_role = discord.utils.get(interaction.guild.roles, name=role_name)
        if existing_role:
            await interaction.response.send_message(
                f"❌ A role named '{role_name}' already exists in this server.",
                ephemeral=True,
            )
            return

        try:
            # Create the role
            role = await interaction.guild.create_role(
                name=role_name,
                color=discord.Color.random(),
                mentionable=True,
                reason=f"Custom empire role created by {interaction.user}",
            )

            embed = discord.Embed(
                title="✅ Role Created",
                description=f"Successfully created the **{role_name}** role!",
                color=self.config.get_color("success"),
            )

            embed.add_field(
                name="🎨 Role Details",
                value=f"**Name:** {role.name}\n**Color:** {role.color}\n**Mentionable:** Yes",
                inline=True,
            )

            # Add to empire types if emoji provided
            if emoji:
                self.empire_types[emoji] = {
                    "name": role_name,
                    "description": f"Custom empire role created by {interaction.user.display_name}",
                    "ethics": "Custom",
                    "government": "Custom",
                }

                embed.add_field(
                    name="🔄 Empire System",
                    value=f"Role added to empire selection with emoji {emoji}",
                    inline=True,
                )

            await interaction.response.send_message(embed=embed)

        except discord.Forbidden:
            await interaction.response.send_message(
                "❌ I don't have permission to create roles.", ephemeral=True
            )
        except Exception as e:
            await interaction.response.send_message(
                f"❌ Failed to create role: {str(e)}", ephemeral=True
            )


async def setup(bot):
    await bot.add_cog(Roles(bot))
