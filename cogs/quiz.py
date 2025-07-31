"""
Quiz system for Astra Bot
Provides interactive space and Stellaris quizzes with leaderboards
"""

import discord
from discord import app_commands
from discord.ext import commands
import random
import json
import os
import asyncio
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, List, Any, Union

from config.enhanced_config import config_manager, feature_enabled
from ui.ui_components import QuizView, LeaderboardView


class Quiz(commands.GroupCog, name="quiz"):
    """Quiz commands for testing your knowledge of space and Stellaris"""

    def __init__(self, bot):
        super().__init__()
        self.bot = bot
        self.config = config_manager
        self.logger = bot.logger
        
        # Data file paths
        self.data_dir = Path("data/quiz")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.leaderboard_file = self.data_dir / "quiz_leaderboard.json"
        self.user_stats_file = self.data_dir / "user_quiz_stats.json"
        
        # Load leaderboard and stats
        self.leaderboard = self.load_json_file(self.leaderboard_file, {})
        self.user_stats = self.load_json_file(self.user_stats_file, {})
        
        # Load quiz questions
        self.questions = self._load_questions()
        
        self.logger.info(f"Quiz cog initialized with {sum(len(v) for v in self.questions.values())} questions")
    
    def _load_questions(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load quiz questions from file or use default questions"""
        # Default questions for space category
        space_questions = [
            {
                "question": "Which planet has the most moons?",
                "options": ["A. Earth", "B. Jupiter", "C. Saturn", "D. Mars"],
                "answer": "C",
                "difficulty": "medium",
                "points": 10,
            },
            {
                "question": "What is the name of our galaxy?",
                "options": [
                    "A. Andromeda",
                    "B. Milky Way",
                    "C. Triangulum",
                    "D. Whirlpool",
                ],
                "answer": "B",
                "difficulty": "easy",
                "points": 5,
            },
            {
                "question": "How long does it take light from the Sun to reach Earth?",
                "options": [
                    "A. 8 seconds",
                    "B. 8 minutes",
                    "C. 8 hours",
                    "D. 8 days",
                ],
                "answer": "B",
                "difficulty": "medium",
                "points": 10,
            },
            {
                "question": "What is the largest planet in our solar system?",
                "options": ["A. Saturn", "B. Earth", "C. Jupiter", "D. Neptune"],
                "answer": "C",
                "difficulty": "easy",
                "points": 5,
            },
            {
                "question": "Which space telescope was launched in 1990?",
                "options": [
                    "A. James Webb",
                    "B. Hubble",
                    "C. Spitzer",
                    "D. Kepler",
                ],
                "answer": "B",
                "difficulty": "medium",
                "points": 10,
            },
            {
                "question": "What is the closest star to Earth (besides the Sun)?",
                "options": [
                    "A. Alpha Centauri",
                    "B. Proxima Centauri",
                    "C. Sirius",
                    "D. Vega",
                ],
                "answer": "B",
                "difficulty": "hard",
                "points": 15,
            },
        ]
        
        # Default questions for Stellaris category
        stellaris_questions = [
            {
                "question": "In Stellaris, what is a Megastructure?",
                "options": [
                    "A. A colony ship",
                    "B. A diplomatic treaty",
                    "C. A massive space construction",
                    "D. A star",
                ],
                "answer": "C",
                "difficulty": "easy",
                "points": 5,
            },
            {
                "question": "What are the three main ethics axes in Stellaris?",
                "options": [
                    "A. Order, Chaos, Neutral",
                    "B. Authoritarian/Egalitarian, Xenophobe/Xenophile, Militarist/Pacifist",
                    "C. Good, Evil, Neutral",
                    "D. Democratic, Autocratic, Oligarchic",
                ],
                "answer": "B",
                "difficulty": "medium",
                "points": 10,
            },
            {
                "question": "What is the maximum number of civic points you can have?",
                "options": ["A. 2", "B. 3", "C. 4", "D. 5"],
                "answer": "B",
                "difficulty": "medium",
                "points": 10,
            },
            {
                "question": "Which crisis can devour entire stars?",
                "options": [
                    "A. Prethoryn Scourge",
                    "B. Unbidden",
                    "C. Contingency",
                    "D. None of them",
                ],
                "answer": "A",
                "difficulty": "hard",
                "points": 15,
            },
            {
                "question": "What does 'Tall' gameplay focus on in Stellaris?",
                "options": [
                    "A. Many planets, rapid expansion",
                    "B. Few planets, high development",
                    "C. Military conquest",
                    "D. Diplomatic alliances",
                ],
                "answer": "B",
                "difficulty": "medium",
                "points": 10,
            },
        ]
        
        # Try to load custom questions
        questions = {"space": space_questions, "stellaris": stellaris_questions}
        
        try:
            custom_questions_file = self.data_dir / "custom_questions.json"
            if custom_questions_file.exists():
                with open(custom_questions_file, "r") as f:
                    custom_questions = json.load(f)
                    
                    # Validate and merge custom questions
                    for category, question_list in custom_questions.items():
                        if isinstance(question_list, list):
                            if category not in questions:
                                questions[category] = []
                            
                            # Add valid questions
                            for q in question_list:
                                if self._validate_question(q):
                                    questions[category].append(q)
                                    
                self.logger.info(f"Loaded custom questions: {sum(len(v) for v in custom_questions.values())} questions")
                
        except Exception as e:
            self.logger.error(f"Error loading custom questions: {e}")
            
        return questions
    
    def _validate_question(self, question: Dict[str, Any]) -> bool:
        """Validate that a question has all required fields"""
        required_fields = ["question", "options", "answer", "difficulty", "points"]
        if not all(field in question for field in required_fields):
            return False
            
        if not isinstance(question["options"], list) or len(question["options"]) < 2:
            return False
            
        if question["answer"] not in "ABCD"[:len(question["options"])]:
            return False
            
        return True
    
    def load_json_file(self, filename: Path, default: Any) -> Any:
        """Load JSON file or return default if not found"""
        try:
            if filename.exists():
                with open(filename, "r") as f:
                    return json.load(f)
            return default
        except Exception as e:
            self.logger.error(f"Error loading {filename}: {e}")
            return default

    def save_json_file(self, filename: Path, data: Any) -> bool:
        """Save data to JSON file"""
        try:
            with open(filename, "w") as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            self.logger.error(f"Error saving {filename}: {e}")
            return False
    
    def update_user_stats(self, user_id: int, guild_id: int, correct: bool, points: int, category: str):
        """Update user statistics"""
        user_key = f"{guild_id}-{user_id}"
        
        if user_key not in self.user_stats:
            self.user_stats[user_key] = {
                "total_questions": 0,
                "correct_answers": 0,
                "total_points": 0,
                "categories": {},
                "streak": 0,
                "best_streak": 0,
                "last_answer": None,
            }
        
        stats = self.user_stats[user_key]
        stats["total_questions"] += 1
        stats["last_answer"] = datetime.now().isoformat()
        
        if correct:
            stats["correct_answers"] += 1
            stats["total_points"] += points
            stats["streak"] += 1
            if stats["streak"] > stats["best_streak"]:
                stats["best_streak"] = stats["streak"]
        else:
            stats["streak"] = 0
        
        # Update category stats
        if category not in stats["categories"]:
            stats["categories"][category] = {"total": 0, "correct": 0}
            
        stats["categories"][category]["total"] += 1
        if correct:
            stats["categories"][category]["correct"] += 1
        
        # Update leaderboard
        if str(guild_id) not in self.leaderboard:
            self.leaderboard[str(guild_id)] = {}
            
        accuracy = (stats["correct_answers"] / stats["total_questions"]) * 100
            
        self.leaderboard[str(guild_id)][str(user_id)] = {
            "points": stats["total_points"],
            "accuracy": accuracy,
            "total_questions": stats["total_questions"],
            "streak": stats["streak"],
            "best_streak": stats["best_streak"],
        }
        
        # Save data
        self.save_json_file(self.user_stats_file, self.user_stats)
        self.save_json_file(self.leaderboard_file, self.leaderboard)
        
        # Return current stats for convenience
        return {
            "correct": correct,
            "points": points if correct else 0,
            "streak": stats["streak"],
            "total_points": stats["total_points"],
            "accuracy": accuracy
        }
    
    @app_commands.command(name="start", description="Start an interactive quiz")
    @app_commands.describe(category="Quiz category (space, stellaris, or random)")
    @app_commands.checks.cooldown(1, 10)
    @feature_enabled("quiz_system")
    async def quiz_command(self, interaction: discord.Interaction, category: Optional[str] = None):
        """Start an interactive quiz with a random question"""
        # Determine category
        available_categories = list(self.questions.keys())
        
        if not available_categories:
            await interaction.response.send_message(
                "❌ No quiz questions available. Please contact an administrator.",
                ephemeral=True
            )
            return
            
        if category and category.lower() in available_categories:
            selected_category = category.lower()
            questions_pool = self.questions[selected_category]
        elif category and category.lower() == "random":
            selected_category = "random"
            questions_pool = [q for category_questions in self.questions.values() for q in category_questions]
        else:
            selected_category = random.choice(available_categories)
            questions_pool = self.questions[selected_category]
        
        if not questions_pool:
            await interaction.response.send_message(
                f"❌ No questions available in the {selected_category} category.",
                ephemeral=True
            )
            return
        
        # Select a random question
        question_data = random.choice(questions_pool)
        options_text = "\n".join(question_data["options"])
        
        # Create embed with difficulty and points
        difficulty_emoji = {"easy": "🟢", "medium": "🟡", "hard": "🔴"}
        
        embed = discord.Embed(
            title=f"🚀 Quiz Time! ({selected_category.title()})",
            description=f"{question_data['question']}\n\n{options_text}",
            color=self.config.get_color("primary"),
            timestamp=datetime.utcnow(),
        )
        
        embed.add_field(
            name="📊 Info",
            value=f"{difficulty_emoji.get(question_data['difficulty'], '⚪')} {question_data['difficulty'].title()} • {question_data['points']} points",
            inline=False,
        )
        
        embed.set_footer(text="Select an answer • 30 seconds to respond")
        
        # Create interactive view with answer buttons
        async def quiz_callback(user, answer=None, timeout=False):
            if timeout:
                timeout_embed = discord.Embed(
                    title="⏰ Time's Up!",
                    description=f"The correct answer was **{question_data['answer']}**.",
                    color=self.config.get_color("warning"),
                )
                if interaction.message:
                    await interaction.followup.send(embed=timeout_embed)
                return
                
            if not user:
                return
                
            correct = answer == question_data["answer"]
            
            # Update user stats
            result = self.update_user_stats(
                user.id,
                interaction.guild.id,
                correct,
                question_data["points"] if correct else 0,
                selected_category if selected_category != "random" else "general"
            )
            
            if correct:
                result_embed = discord.Embed(
                    title="✅ Correct!",
                    description=f"Well done, {user.mention}! You earned **{question_data['points']} points**!",
                    color=self.config.get_color("success"),
                )
                
                if result["streak"] > 1:
                    result_embed.add_field(
                        name="🔥 Streak",
                        value=f"You're on a {result['streak']} question streak!",
                        inline=True,
                    )
                    
            else:
                result_embed = discord.Embed(
                    title="❌ Incorrect",
                    description=f"Sorry {user.mention}, the correct answer was **{question_data['answer']}**.",
                    color=self.config.get_color("error"),
                )
            
            # Add stats field
            result_embed.add_field(
                name="📊 Your Stats",
                value=f"**Total Points:** {result['total_points']}\n"
                      f"**Accuracy:** {result['accuracy']:.1f}%",
                inline=True
            )
            
            # Add button for new quiz
            view = discord.ui.View()
            view.add_item(discord.ui.Button(
                label="New Quiz",
                style=discord.ButtonStyle.primary,
                custom_id="new_quiz"
            ))
            
            await interaction.followup.send(embed=result_embed, view=view)
        
        # Send the quiz
        view = QuizView(question_data, quiz_callback)
        await interaction.response.send_message(embed=embed, view=view)
    
    @app_commands.command(name="leaderboard", description="View the quiz leaderboard")
    @app_commands.describe(sort_by="How to sort the leaderboard")
    @app_commands.choices(sort_by=[
        app_commands.Choice(name="Points", value="points"),
        app_commands.Choice(name="Accuracy", value="accuracy"),
        app_commands.Choice(name="Questions Answered", value="questions"),
        app_commands.Choice(name="Streak", value="streak")
    ])
    @app_commands.checks.cooldown(1, 15)
    @feature_enabled("quiz_system")
    async def leaderboard_command(self, interaction: discord.Interaction, sort_by: Optional[str] = "points"):
        """Show quiz leaderboard with sorting options"""
        guild_id = str(interaction.guild.id)
        
        if guild_id not in self.leaderboard or not self.leaderboard[guild_id]:
            embed = discord.Embed(
                title="📊 Quiz Leaderboard",
                description="No quiz data yet! Use `/quiz start` to get started.",
                color=self.config.get_color("warning"),
            )
            await interaction.response.send_message(embed=embed)
            return
        
        # Update display names in leaderboard
        for user_id, stats in self.leaderboard[guild_id].items():
            try:
                user = await self.bot.fetch_user(int(user_id))
                stats["display_name"] = user.display_name if user else "Unknown User"
            except:
                stats["display_name"] = "Unknown User"
        
        # Create interactive leaderboard
        leaderboard_view = LeaderboardView(self.leaderboard[guild_id], sort_by or "points")
        embed = leaderboard_view.create_leaderboard_embed(sort_by or "points")
        
        await interaction.response.send_message(embed=embed, view=leaderboard_view)
    
    @app_commands.command(name="stats", description="View your quiz statistics")
    @app_commands.describe(user="User to view statistics for (default: yourself)")
    @app_commands.checks.cooldown(1, 10)
    @feature_enabled("quiz_system")
    async def stats_command(self, interaction: discord.Interaction, user: Optional[discord.User] = None):
        """Show detailed quiz statistics for a user"""
        target_user = user or interaction.user
        user_key = f"{interaction.guild.id}-{target_user.id}"
        
        if user_key not in self.user_stats:
            embed = discord.Embed(
                title="📊 Quiz Statistics",
                description=f"{'You haven' if target_user == interaction.user else f'{target_user.display_name} hasn'}'t answered any quiz questions yet!",
                color=self.config.get_color("warning"),
            )
            await interaction.response.send_message(embed=embed)
            return
        
        stats = self.user_stats[user_key]
        accuracy = (stats["correct_answers"] / stats["total_questions"]) * 100 if stats["total_questions"] > 0 else 0
        
        embed = discord.Embed(
            title=f"📊 {target_user.display_name}'s Quiz Stats",
            color=self.config.get_color("primary"),
            timestamp=datetime.utcnow(),
        )
        
        embed.set_thumbnail(url=target_user.display_avatar.url)
        
        embed.add_field(
            name="🎯 Overall Performance",
            value=f"**Total Questions:** {stats['total_questions']}\n"
                  f"**Correct Answers:** {stats['correct_answers']}\n"
                  f"**Accuracy:** {accuracy:.1f}%\n"
                  f"**Total Points:** {stats['total_points']}",
            inline=True,
        )
        
        embed.add_field(
            name="🔥 Streaks",
            value=f"**Current Streak:** {stats['streak']}\n"
                  f"**Best Streak:** {stats['best_streak']}",
            inline=True,
        )
        
        # Category breakdown
        if stats["categories"]:
            category_text = ""
            for category, cat_stats in stats["categories"].items():
                cat_accuracy = (cat_stats["correct"] / cat_stats["total"]) * 100 if cat_stats["total"] > 0 else 0
                category_text += f"**{category.title()}:** {cat_stats['correct']}/{cat_stats['total']} ({cat_accuracy:.1f}%)\n"
                
            embed.add_field(name="📚 By Category", value=category_text, inline=False)
        
        # Rank in server
        guild_id = str(interaction.guild.id)
        if guild_id in self.leaderboard and str(target_user.id) in self.leaderboard[guild_id]:
            sorted_users = sorted(
                self.leaderboard[guild_id].items(),
                key=lambda x: x[1]["points"],
                reverse=True,
            )
            
            rank = next(
                (
                    i + 1
                    for i, (uid, _) in enumerate(sorted_users)
                    if uid == str(target_user.id)
                ),
                "N/A",
            )
            
            embed.add_field(
                name="🏆 Server Rank",
                value=f"#{rank} out of {len(sorted_users)} players",
                inline=True,
            )
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="categories", description="View available quiz categories")
    @app_commands.checks.cooldown(1, 5)
    @feature_enabled("quiz_system")
    async def categories_command(self, interaction: discord.Interaction):
        """Show available quiz categories"""
        if not self.questions:
            await interaction.response.send_message(
                "❌ No quiz categories available. Please contact an administrator.",
                ephemeral=True
            )
            return
            
        embed = discord.Embed(
            title="📚 Quiz Categories",
            description="Choose a category for your next quiz!",
            color=self.config.get_color("primary"),
        )
        
        for category, questions in self.questions.items():
            question_count = len(questions)
            
            # Count questions by difficulty
            difficulties = {}
            for q in questions:
                diff = q.get("difficulty", "unknown")
                difficulties[diff] = difficulties.get(diff, 0) + 1
                
            diff_text = " • ".join([f"{count} {diff}" for diff, count in difficulties.items()])
            
            embed.add_field(
                name=f"🌟 {category.title()}",
                value=f"**{question_count} questions**\n{diff_text}",
                inline=True,
            )
        
        embed.add_field(
            name="🎲 Usage",
            value="Use `/quiz start` with these options:\n"
                 + "\n".join([f"• `/quiz start category:{cat}`" for cat in self.questions.keys()])
                 + "\n• `/quiz start category:random`",
            inline=False,
        )
        
        await interaction.response.send_message(embed=embed)
    
    # Admin commands for quiz management
    @app_commands.command(name="add", description="Add a new quiz question (Admin only)")
    @app_commands.checks.cooldown(1, 10)
    @feature_enabled("quiz_system")
    @app_commands.default_permissions(manage_guild=True)
    async def add_question(self, interaction: discord.Interaction):
        """Add a new quiz question (Admin only)"""
        # Check if user has permission
        if not interaction.user.guild_permissions.administrator and not self.config.has_role_permission(interaction.user, "quiz_master"):
            await interaction.response.send_message(
                "❌ You need Quiz Master permissions to add questions.",
                ephemeral=True
            )
            return
            
        # For this command, we'd typically use a modal for input
        # Since this is a placeholder, we'll show how it would be implemented
        await interaction.response.send_message(
            "🚧 This feature is under development.\n\n"
            "To add questions manually, edit the file `data/quiz/custom_questions.json` with this structure:\n"
            "```json\n"
            "{\n"
            "  \"space\": [\n"
            "    {\n"
            "      \"question\": \"Your question text?\",\n"
            "      \"options\": [\"A. Option 1\", \"B. Option 2\", \"C. Option 3\", \"D. Option 4\"],\n"
            "      \"answer\": \"A\",\n"
            "      \"difficulty\": \"medium\",\n"
            "      \"points\": 10\n"
            "    }\n"
            "  ]\n"
            "}\n"
            "```",
            ephemeral=True
        )
    
    @app_commands.command(name="reset", description="Reset quiz leaderboard (Admin only)")
    @app_commands.checks.cooldown(1, 30)
    @feature_enabled("quiz_system")
    @app_commands.default_permissions(administrator=True)
    async def reset_leaderboard(self, interaction: discord.Interaction):
        """Reset the quiz leaderboard (Admin only)"""
        # Check if user has permission
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(
                "❌ You need Administrator permissions to reset the leaderboard.",
                ephemeral=True
            )
            return
            
        # Create confirmation button
        class ConfirmView(discord.ui.View):
            def __init__(self):
                super().__init__(timeout=60)
                self.confirmed = False
                
            @discord.ui.button(label="Confirm Reset", style=discord.ButtonStyle.danger)
            async def confirm(self, confirm_interaction: discord.Interaction, button: discord.ui.Button):
                self.confirmed = True
                self.stop()
                await confirm_interaction.response.send_message(
                    "✅ Leaderboard has been reset!",
                    ephemeral=True
                )
                
            @discord.ui.button(label="Cancel", style=discord.ButtonStyle.secondary)
            async def cancel(self, cancel_interaction: discord.Interaction, button: discord.ui.Button):
                self.stop()
                await cancel_interaction.response.send_message(
                    "❌ Leaderboard reset cancelled.",
                    ephemeral=True
                )
        
        # Send confirmation message
        view = ConfirmView()
        await interaction.response.send_message(
            "⚠️ **WARNING**: This will reset the entire quiz leaderboard for this server.\n"
            "This action cannot be undone. Are you sure?",
            view=view,
            ephemeral=True
        )
        
        # Wait for confirmation
        await view.wait()
        
        if view.confirmed:
            # Reset the leaderboard
            guild_id = str(interaction.guild.id)
            if guild_id in self.leaderboard:
                del self.leaderboard[guild_id]
                self.save_json_file(self.leaderboard_file, self.leaderboard)
                
                # Also reset guild stats in user_stats
                for user_key in list(self.user_stats.keys()):
                    if user_key.startswith(f"{interaction.guild.id}-"):
                        del self.user_stats[user_key]
                
                self.save_json_file(self.user_stats_file, self.user_stats)


async def setup(bot):
    await bot.add_cog(Quiz(bot))
