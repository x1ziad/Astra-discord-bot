import discord
from discord.ext import commands
import random
import asyncio
import json
import os
from datetime import datetime, timedelta


class Quiz(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.leaderboard_file = "data/quiz_leaderboard.json"
        self.user_stats_file = "data/user_quiz_stats.json"

        # Create data directory if it doesn't exist
        os.makedirs("data", exist_ok=True)

        # Load leaderboard and stats
        self.leaderboard = self.load_json_file(self.leaderboard_file, {})
        self.user_stats = self.load_json_file(self.user_stats_file, {})

        self.questions = {
            "space": [
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
            ],
            "stellaris": [
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
            ],
        }

    def load_json_file(self, filename, default):
        """Load JSON file or return default if not found"""
        try:
            with open(filename, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return default

    def save_json_file(self, filename, data):
        """Save data to JSON file"""
        try:
            with open(filename, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving {filename}: {e}")

    def update_user_stats(self, user_id, guild_id, correct, points, category):
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
        if guild_id not in self.leaderboard:
            self.leaderboard[guild_id] = {}

        self.leaderboard[guild_id][str(user_id)] = {
            "points": stats["total_points"],
            "accuracy": (stats["correct_answers"] / stats["total_questions"]) * 100,
            "total_questions": stats["total_questions"],
            "streak": stats["streak"],
            "best_streak": stats["best_streak"],
        }

        # Save data
        self.save_json_file(self.user_stats_file, self.user_stats)
        self.save_json_file(self.leaderboard_file, self.leaderboard)

    @commands.command(name="quiz")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def ask_quiz(self, ctx, category: str = None):
        """Start an interactive quiz - categories: space, stellaris, or random"""

        # Determine category
        if category and category.lower() in self.questions:
            selected_category = category.lower()
            questions_pool = self.questions[selected_category]
        elif category and category.lower() == "random":
            selected_category = "random"
            questions_pool = [
                q
                for category_questions in self.questions.values()
                for q in category_questions
            ]
        else:
            selected_category = "random"
            questions_pool = [
                q
                for category_questions in self.questions.values()
                for q in category_questions
            ]

        q = random.choice(questions_pool)
        options_text = "\n".join(q["options"])

        # Create embed with difficulty and points
        difficulty_emoji = {"easy": "🟢", "medium": "🟡", "hard": "🔴"}

        embed = discord.Embed(
            title=f"🚀 Quiz Time! ({selected_category.title()})",
            description=f"{q['question']}\n\n{options_text}",
            color=0x5865F2,
            timestamp=datetime.utcnow(),
        )

        embed.add_field(
            name="📊 Info",
            value=f"{difficulty_emoji.get(q['difficulty'], '⚪')} {q['difficulty'].title()} • {q['points']} points",
            inline=False,
        )

        embed.set_footer(text="React with A, B, C, or D • 15 seconds to answer")

        message = await ctx.send(embed=embed)

        # Add emoji reactions for A-D
        emoji_list = ["🇦", "🇧", "🇨", "🇩"]
        for emoji in emoji_list:
            await message.add_reaction(emoji)

        def check(reaction, user):
            return (
                user != self.bot.user
                and str(reaction.emoji) in emoji_list
                and reaction.message.id == message.id
            )

        try:
            reaction, user = await self.bot.wait_for(
                "reaction_add", timeout=15.0, check=check
            )
        except asyncio.TimeoutError:
            timeout_embed = discord.Embed(
                title="⏰ Time's Up!",
                description=f"The correct answer was **{q['answer']}**.",
                color=0xFF9900,
            )
            await ctx.send(embed=timeout_embed)
        else:
            index = emoji_list.index(str(reaction.emoji))
            selected_option = chr(ord("A") + index)
            correct = selected_option == q["answer"]

            # Update user stats
            self.update_user_stats(
                user.id,
                ctx.guild.id,
                correct,
                q["points"] if correct else 0,
                selected_category,
            )

            if correct:
                # Get user's current streak
                user_key = f"{ctx.guild.id}-{user.id}"
                current_streak = self.user_stats.get(user_key, {}).get("streak", 0)

                result_embed = discord.Embed(
                    title="✅ Correct!",
                    description=f"Well done, {user.mention}! You earned **{q['points']} points**!",
                    color=0x00FF00,
                )

                if current_streak > 1:
                    result_embed.add_field(
                        name="🔥 Streak",
                        value=f"You're on a {current_streak} question streak!",
                        inline=True,
                    )

            else:
                result_embed = discord.Embed(
                    title="❌ Incorrect",
                    description=f"Sorry {user.mention}, the correct answer was **{q['answer']}**.",
                    color=0xFF0000,
                )

            await ctx.send(embed=result_embed)

    @commands.command(name="leaderboard", aliases=["lb", "top"])
    @commands.cooldown(1, 15, commands.BucketType.guild)
    async def show_leaderboard(self, ctx, sort_by: str = "points"):
        """Show quiz leaderboard - sort by: points, accuracy, questions, streak"""

        guild_id = str(ctx.guild.id)
        if guild_id not in self.leaderboard or not self.leaderboard[guild_id]:
            embed = discord.Embed(
                title="📊 Quiz Leaderboard",
                description="No quiz data yet! Use `!quiz` to get started.",
                color=0xFF9900,
            )
            await ctx.send(embed=embed)
            return

        # Sort users based on criteria
        sort_options = {
            "points": lambda x: x[1]["points"],
            "accuracy": lambda x: (
                x[1]["accuracy"] if x[1]["total_questions"] >= 5 else 0
            ),
            "questions": lambda x: x[1]["total_questions"],
            "streak": lambda x: x[1]["best_streak"],
        }

        if sort_by not in sort_options:
            sort_by = "points"

        sorted_users = sorted(
            self.leaderboard[guild_id].items(), key=sort_options[sort_by], reverse=True
        )[
            :10
        ]  # Top 10

        embed = discord.Embed(
            title=f"🏆 Quiz Leaderboard (by {sort_by.title()})",
            color=0xFFD700,
            timestamp=datetime.utcnow(),
        )

        leaderboard_text = ""
        medals = ["🥇", "🥈", "🥉"]

        for i, (user_id, stats) in enumerate(sorted_users):
            try:
                user = self.bot.get_user(int(user_id)) or await self.bot.fetch_user(
                    int(user_id)
                )
                username = user.display_name if user else "Unknown User"
            except:
                username = "Unknown User"

            medal = medals[i] if i < 3 else f"`{i+1}.`"

            if sort_by == "points":
                value = f"{stats['points']} pts"
            elif sort_by == "accuracy":
                value = (
                    f"{stats['accuracy']:.1f}%"
                    if stats["total_questions"] >= 5
                    else "N/A"
                )
            elif sort_by == "questions":
                value = f"{stats['total_questions']} answered"
            else:  # streak
                value = f"{stats['best_streak']} streak"

            leaderboard_text += f"{medal} **{username}** - {value}\n"

        embed.description = leaderboard_text

        embed.add_field(
            name="📝 Sort Options",
            value="`!lb points` • `!lb accuracy` • `!lb questions` • `!lb streak`",
            inline=False,
        )

        await ctx.send(embed=embed)

    @commands.command(name="mystats", aliases=["quiz-stats", "qs"])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def user_quiz_stats(self, ctx, user: discord.Member = None):
        """Show your quiz statistics or another user's stats"""

        target_user = user or ctx.author
        user_key = f"{ctx.guild.id}-{target_user.id}"

        if user_key not in self.user_stats:
            embed = discord.Embed(
                title="📊 Quiz Statistics",
                description=f"{'You haven' if target_user == ctx.author else f'{target_user.display_name} hasn'}'t answered any quiz questions yet!",
                color=0xFF9900,
            )
            await ctx.send(embed=embed)
            return

        stats = self.user_stats[user_key]
        accuracy = (
            (stats["correct_answers"] / stats["total_questions"]) * 100
            if stats["total_questions"] > 0
            else 0
        )

        embed = discord.Embed(
            title=f"📊 {target_user.display_name}'s Quiz Stats",
            color=0x5865F2,
            timestamp=datetime.utcnow(),
        )

        embed.set_thumbnail(url=target_user.display_avatar.url)

        embed.add_field(
            name="🎯 Overall Performance",
            value=f"**Total Questions:** {stats['total_questions']}\n**Correct Answers:** {stats['correct_answers']}\n**Accuracy:** {accuracy:.1f}%\n**Total Points:** {stats['total_points']}",
            inline=True,
        )

        embed.add_field(
            name="🔥 Streaks",
            value=f"**Current Streak:** {stats['streak']}\n**Best Streak:** {stats['best_streak']}",
            inline=True,
        )

        # Category breakdown
        if stats["categories"]:
            category_text = ""
            for category, cat_stats in stats["categories"].items():
                cat_accuracy = (
                    (cat_stats["correct"] / cat_stats["total"]) * 100
                    if cat_stats["total"] > 0
                    else 0
                )
                category_text += f"**{category.title()}:** {cat_stats['correct']}/{cat_stats['total']} ({cat_accuracy:.1f}%)\n"

            embed.add_field(name="📚 By Category", value=category_text, inline=False)

        # Rank in server
        guild_id = str(ctx.guild.id)
        if (
            guild_id in self.leaderboard
            and str(target_user.id) in self.leaderboard[guild_id]
        ):
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

        await ctx.send(embed=embed)

    @commands.command(name="categories")
    async def quiz_categories(self, ctx):
        """Show available quiz categories"""
        embed = discord.Embed(
            title="📚 Quiz Categories",
            description="Choose a category for your next quiz!",
            color=0x5865F2,
        )

        for category, questions in self.questions.items():
            question_count = len(questions)
            difficulties = {}
            for q in questions:
                diff = q["difficulty"]
                difficulties[diff] = difficulties.get(diff, 0) + 1

            diff_text = " • ".join(
                [f"{count} {diff}" for diff, count in difficulties.items()]
            )

            embed.add_field(
                name=f"🌟 {category.title()}",
                value=f"**{question_count} questions**\n{diff_text}",
                inline=True,
            )

        embed.add_field(
            name="🎲 Usage",
            value="`!quiz space` • `!quiz stellaris` • `!quiz random`",
            inline=False,
        )

        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Quiz(bot))
