"""
Discord UI Components for Astra Bot
Includes buttons, select menus, modals, and interactive views
"""

import discord
from discord.ext import commands
from discord import ui
from typing import List, Dict, Any, Optional, Callable
import asyncio
from datetime import datetime
import json

class PaginatedView(discord.ui.View):
    """Paginated embed view with buttons"""
    
    def __init__(self, embeds: List[discord.Embed], timeout: float = 180):
        super().__init__(timeout=timeout)
        self.embeds = embeds
        self.current_page = 0
        self.max_pages = len(embeds)
        
        # Disable buttons if only one page
        if self.max_pages <= 1:
            self.previous_button.disabled = True
            self.next_button.disabled = True
            self.first_button.disabled = True
            self.last_button.disabled = True
        else:
            # Update button states based on current page
            self.update_buttons()
    
    def update_buttons(self):
        """Update button states based on current page"""
        self.first_button.disabled = self.current_page == 0
        self.previous_button.disabled = self.current_page == 0
        self.next_button.disabled = self.current_page == self.max_pages - 1
        self.last_button.disabled = self.current_page == self.max_pages - 1
    
    @discord.ui.button(emoji="⏪", style=discord.ButtonStyle.secondary)
    async def first_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_page = 0
        self.update_buttons()
        await interaction.response.edit_message(embed=self.embeds[self.current_page], view=self)
    
    @discord.ui.button(emoji="◀️", style=discord.ButtonStyle.primary)
    async def previous_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page > 0:
            self.current_page -= 1
        self.update_buttons()
        await interaction.response.edit_message(embed=self.embeds[self.current_page], view=self)
    
    @discord.ui.button(emoji="🗑️", style=discord.ButtonStyle.danger)
    async def delete_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(content="*Message deleted by user*", embed=None, view=None)
    
    @discord.ui.button(emoji="▶️", style=discord.ButtonStyle.primary)
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page < self.max_pages - 1:
            self.current_page += 1
        self.update_buttons()
        await interaction.response.edit_message(embed=self.embeds[self.current_page], view=self)
    
    @discord.ui.button(emoji="⏩", style=discord.ButtonStyle.secondary)
    async def last_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_page = self.max_pages - 1
        self.update_buttons()
        await interaction.response.edit_message(embed=self.embeds[self.current_page], view=self)
    
    async def on_timeout(self):
        """Disable all buttons when view times out"""
        for item in self.children:
            item.disabled = True
        # Note: Cannot update message here without interaction


class QuizView(discord.ui.View):
    """Interactive quiz view with buttons"""
    
    def __init__(self, question_data: Dict, callback: Callable, timeout: float = 15):
        super().__init__(timeout=timeout)
        self.question_data = question_data
        self.callback = callback
        self.answered = False
        
        # Create buttons for each option
        for i, option in enumerate(question_data['options']):
            button = QuizButton(
                label=option,
                custom_id=f"quiz_{chr(65 + i)}",  # A, B, C, D
                style=discord.ButtonStyle.secondary,
                row=i // 2  # 2 buttons per row
            )
            self.add_item(button)
    
    async def on_timeout(self):
        """Handle quiz timeout"""
        if not self.answered:
            self.answered = True
            for item in self.children:
                item.disabled = True
            await self.callback(None, timeout=True)


class QuizButton(discord.ui.Button):
    """Quiz answer button"""
    
    async def callback(self, interaction: discord.Interaction):
        view: QuizView = self.view
        if view.answered:
            return
        
        view.answered = True
        selected_answer = self.custom_id.split('_')[1]  # Extract A, B, C, D
        
        # Disable all buttons and style them
        for item in view.children:
            item.disabled = True
            if isinstance(item, QuizButton):
                answer_letter = item.custom_id.split('_')[1]
                if answer_letter == view.question_data['answer']:
                    item.style = discord.ButtonStyle.success
                elif answer_letter == selected_answer and answer_letter != view.question_data['answer']:
                    item.style = discord.ButtonStyle.danger
                else:
                    item.style = discord.ButtonStyle.secondary
        
        await interaction.response.edit_message(view=view)
        await view.callback(interaction.user, selected_answer)


class EmpireRoleSelect(discord.ui.Select):
    """Stellaris empire role selector"""
    
    def __init__(self, empire_data: Dict):
        options = []
        for emoji, empire_info in empire_data.items():
            options.append(discord.SelectOption(
                label=empire_info['name'],
                description=empire_info['description'][:100],
                emoji=emoji,
                value=empire_info['name']
            ))
        
        super().__init__(
            placeholder="Choose your Stellaris empire...",
            options=options,
            max_values=1
        )
        self.empire_data = empire_data
    
    async def callback(self, interaction: discord.Interaction):
        selected_empire = self.values[0]
        
        # Find the empire data
        empire_info = None
        for emoji, info in self.empire_data.items():
            if info['name'] == selected_empire:
                empire_info = info
                break
        
        if not empire_info:
            return
        
        # Handle role assignment logic here
        guild = interaction.guild
        member = guild.get_member(interaction.user.id)
        
        # Try to find or create the role
        role = discord.utils.get(guild.roles, name=selected_empire)
        if not role:
            try:
                # Create role with empire-specific color
                role_colors = {
                    "Democratic Empire": 0x0066cc,
                    "Imperial Authority": 0x800080,
                    "Machine Intelligence": 0x888888,
                    "Hive Mind": 0x663399,
                    "Military Junta": 0xcc0000,
                    "Criminal Syndicate": 0x000000,
                    "Enlightened Republic": 0x00cc66,
                    "Defensive Coalition": 0x0099ff,
                    "Science Directorate": 0x00ffff,
                    "Divine Empire": 0xffcc00
                }
                
                color = discord.Color(role_colors.get(selected_empire, 0x6a0dad))
                role = await guild.create_role(
                    name=selected_empire,
                    color=color,
                    mentionable=True,
                    reason=f"Stellaris empire role created via UI"
                )
            except discord.Forbidden:
                embed = discord.Embed(
                    title="❌ Permission Error",
                    description="I don't have permission to create roles.",
                    color=0xff0000
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
        
        # Remove other empire roles
        for other_info in self.empire_data.values():
            if other_info['name'] != selected_empire:
                other_role = discord.utils.get(guild.roles, name=other_info['name'])
                if other_role and other_role in member.roles:
                    await member.remove_roles(other_role)
        
        # Add selected role
        if role not in member.roles:
            await member.add_roles(role)
        
        embed = discord.Embed(
            title=f"🌌 Empire Role Assigned!",
            description=f"Welcome to the **{selected_empire}**, {interaction.user.mention}!\n\n*{empire_info['description']}*",
            color=role.color if role else 0x6a0dad
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)


class EmpireRoleView(discord.ui.View):
    """View containing empire role selector"""
    
    def __init__(self, empire_data: Dict):
        super().__init__(timeout=300)
        self.add_item(EmpireRoleSelect(empire_data))
        self.empire_data = empire_data
    
    @discord.ui.button(label="Remove Empire Role", emoji="🗑️", style=discord.ButtonStyle.danger, row=1)
    async def remove_role(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        member = guild.get_member(interaction.user.id)
        
        removed_roles = []
        for empire_info in self.empire_data.values():
            role = discord.utils.get(guild.roles, name=empire_info['name'])
            if role and role in member.roles:
                await member.remove_roles(role)
                removed_roles.append(role.name)
        
        if removed_roles:
            embed = discord.Embed(
                title="🗑️ Empire Role Removed",
                description=f"Your empire roles have been removed: {', '.join(removed_roles)}",
                color=0xff6600
            )
        else:
            embed = discord.Embed(
                title="ℹ️ No Empire Roles",
                description="You don't have any empire roles to remove.",
                color=0x999999
            )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)


class ConfirmationView(discord.ui.View):
    """Generic confirmation view with Yes/No buttons"""
    
    def __init__(self, callback: Callable, timeout: float = 60):
        super().__init__(timeout=timeout)
        self.callback = callback
        self.result = None
    
    @discord.ui.button(label="Yes", emoji="✅", style=discord.ButtonStyle.success)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.result = True
        self.stop()
        await self.callback(interaction, True)
    
    @discord.ui.button(label="No", emoji="❌", style=discord.ButtonStyle.danger)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.result = False
        self.stop()
        await self.callback(interaction, False)


class CategorySelectView(discord.ui.View):
    """Category selection view for various features"""
    
    def __init__(self, categories: Dict[str, Dict], callback: Callable, placeholder: str = "Select a category..."):
        super().__init__(timeout=180)
        self.callback = callback
        self.add_item(CategorySelect(categories, callback, placeholder))


class CategorySelect(discord.ui.Select):
    """Category selection dropdown"""
    
    def __init__(self, categories: Dict[str, Dict], callback: Callable, placeholder: str):
        options = []
        for key, category in categories.items():
            options.append(discord.SelectOption(
                label=category.get('name', key.title()),
                description=category.get('description', 'No description')[:100],
                emoji=category.get('emoji', '📂'),
                value=key
            ))
        
        super().__init__(
            placeholder=placeholder,
            options=options,
            max_values=1
        )
        self.callback_func = callback
    
    async def callback(self, interaction: discord.Interaction):
        selected_category = self.values[0]
        await self.callback_func(interaction, selected_category)


class SetupModal(discord.ui.Modal, title="Astra Bot Setup"):
    """Guild setup modal for initial configuration"""
    
    guild_name = discord.ui.TextInput(
        label="Server Name (for logs)",
        placeholder="Your server name...",
        max_length=100,
        required=False
    )
    
    admin_roles = discord.ui.TextInput(
        label="Admin Roles (comma separated)",
        placeholder="Admin, Administrator, Owner",
        max_length=200,
        required=False
    )
    
    quiz_channel = discord.ui.TextInput(
        label="Quiz Channel ID (optional)",
        placeholder="Channel ID for quiz commands",
        max_length=50,
        required=False
    )
    
    space_channel = discord.ui.TextInput(
        label="Space Channel ID (optional)",
        placeholder="Channel ID for space content",
        max_length=50,
        required=False
    )
    
    features = discord.ui.TextInput(
        label="Enable Features (comma separated)",
        placeholder="quiz, space, stellaris, notion",
        max_length=200,
        required=False
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        # Process setup data here
        setup_data = {
            'guild_name': self.guild_name.value or interaction.guild.name,
            'admin_roles': [role.strip() for role in self.admin_roles.value.split(',') if role.strip()],
            'quiz_channel': int(self.quiz_channel.value) if self.quiz_channel.value.isdigit() else None,
            'space_channel': int(self.space_channel.value) if self.space_channel.value.isdigit() else None,
            'features': [feature.strip() for feature in self.features.value.split(',') if feature.strip()]
        }
        
        embed = discord.Embed(
            title="🚀 Setup Complete!",
            description="Astra bot has been configured for your server.",
            color=0x00ff00
        )
        
        # Add setup details to embed
        if setup_data['admin_roles']:
            embed.add_field(
                name="Admin Roles",
                value=", ".join(setup_data['admin_roles']),
                inline=False
            )
        
        if setup_data['features']:
            embed.add_field(
                name="Enabled Features",
                value=", ".join(setup_data['features']),
                inline=False
            )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
        
        # Save configuration (would integrate with config manager)
        # config_manager.set_guild_setting(interaction.guild.id, "setup_data", setup_data)


class ProfileView(discord.ui.View):
    """User profile view with interactive buttons"""
    
    def __init__(self, user_data: Dict, user: discord.Member):
        super().__init__(timeout=300)
        self.user_data = user_data
        self.user = user
    
    @discord.ui.button(label="Quiz Stats", emoji="🎯", style=discord.ButtonStyle.primary)
    async def quiz_stats(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title=f"🎯 {self.user.display_name}'s Quiz Statistics",
            color=0x5865F2
        )
        
        quiz_data = self.user_data.get('quiz', {})
        embed.add_field(
            name="📊 Performance",
            value=f"**Questions Answered:** {quiz_data.get('total_questions', 0)}\n"
                  f"**Correct Answers:** {quiz_data.get('correct_answers', 0)}\n"
                  f"**Accuracy:** {quiz_data.get('accuracy', 0):.1f}%\n"
                  f"**Current Streak:** {quiz_data.get('streak', 0)}",
            inline=True
        )
        
        embed.add_field(
            name="🏆 Achievements",
            value=f"**Total Points:** {quiz_data.get('points', 0)}\n"
                  f"**Best Streak:** {quiz_data.get('best_streak', 0)}\n"
                  f"**Rank:** #{quiz_data.get('rank', 'Unranked')}",
            inline=True
        )
        
        await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.button(label="Achievements", emoji="🏅", style=discord.ButtonStyle.success)
    async def achievements(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title=f"🏅 {self.user.display_name}'s Achievements",
            color=0x00ff00
        )
        
        achievements = self.user_data.get('achievements', [])
        if achievements:
            achievement_text = ""
            for achievement in achievements[:10]:  # Show first 10
                achievement_text += f"🏆 **{achievement.get('name', 'Unknown')}**\n"
                achievement_text += f"   *{achievement.get('description', 'No description')}*\n\n"
            
            embed.description = achievement_text
        else:
            embed.description = "No achievements yet! Start using Astra to earn achievements."
        
        await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.button(label="Empire Info", emoji="🏛️", style=discord.ButtonStyle.secondary)
    async def empire_info(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title=f"🏛️ {self.user.display_name}'s Empire",
            color=0x6a0dad
        )
        
        # Find user's empire role
        empire_roles = ["Democratic Empire", "Imperial Authority", "Machine Intelligence", 
                       "Hive Mind", "Military Junta", "Criminal Syndicate", 
                       "Enlightened Republic", "Defensive Coalition", "Science Directorate", "Divine Empire"]
        
        user_empire = None
        for role in self.user.roles:
            if role.name in empire_roles:
                user_empire = role
                break
        
        if user_empire:
            embed.add_field(
                name="Current Empire",
                value=f"**{user_empire.name}**\n*Leading the galaxy with {user_empire.name.lower()} ideals*",
                inline=False
            )
            embed.color = user_empire.color
        else:
            embed.description = "No empire chosen yet! Use `/empire` to select your galactic empire."
        
        homeworld = self.user_data.get('homeworld', 'Unknown')
        embed.add_field(
            name="🌍 Homeworld",
            value=homeworld.title() if homeworld != 'Unknown' else 'Not selected',
            inline=True
        )
        
        await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.button(label="Back to Profile", emoji="👤", style=discord.ButtonStyle.secondary, row=1)
    async def back_to_profile(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title=f"👤 {self.user.display_name}'s Profile",
            color=0x5865F2
        )
        
        embed.set_thumbnail(url=self.user.display_avatar.url)
        
        # Basic info
        embed.add_field(
            name="📊 Overview",
            value=f"**Level:** {self.user_data.get('level', 1)}\n"
                  f"**XP:** {self.user_data.get('xp', 0)}\n"
                  f"**Joined:** <t:{int(self.user.joined_at.timestamp())}:R>",
            inline=True
        )
        
        # Activity info
        embed.add_field(
            name="🎯 Activity",
            value=f"**Commands Used:** {self.user_data.get('commands_used', 0)}\n"
                  f"**Last Active:** <t:{int(datetime.utcnow().timestamp())}:R>\n"
                  f"**Status:** {self.user_data.get('status', 'Explorer')}",
            inline=True
        )
        
        await interaction.response.edit_message(embed=embed, view=self)


class HomeworldSelectView(discord.ui.View):
    """Homeworld selection view"""
    
    def __init__(self):
        super().__init__(timeout=180)
        self.add_item(HomeworldSelect())


class HomeworldSelect(discord.ui.Select):
    """Homeworld selection dropdown"""
    
    def __init__(self):
        planet_types = {
            "terran": {"name": "Terran World", "emoji": "🌍", "description": "Earth-like planet with balanced conditions"},
            "desert": {"name": "Desert World", "emoji": "🏜️", "description": "Arid planet with harsh, dry conditions"},
            "ocean": {"name": "Ocean World", "emoji": "🌊", "description": "Water-covered planet with deep seas"},
            "arctic": {"name": "Arctic World", "emoji": "🧊", "description": "Frozen planet with icy landscapes"},
            "jungle": {"name": "Jungle World", "emoji": "🌴", "description": "Dense tropical world teeming with life"},
            "volcanic": {"name": "Volcanic World", "emoji": "🌋", "description": "Geologically active planet with lava flows"},
            "gas_giant": {"name": "Gas Giant Moon", "emoji": "🪐", "description": "Moon orbiting a massive gas giant"},
            "artificial": {"name": "Artificial World", "emoji": "🛰️", "description": "Constructed habitat or ring world"}
        }
        
        options = []
        for key, planet in planet_types.items():
            options.append(discord.SelectOption(
                label=planet['name'],
                description=planet['description'],
                emoji=planet['emoji'],
                value=key
            ))
        
        super().__init__(
            placeholder="Choose your homeworld type...",
            options=options,
            max_values=1
        )
    
    async def callback(self, interaction: discord.Interaction):
        selected_world = self.values[0]
        
        # Here you would save the homeworld selection to user data
        # user_manager.set_user_data(interaction.user.id, 'homeworld', selected_world)
        
        world_names = {
            "terran": "Terran World",
            "desert": "Desert World", 
            "ocean": "Ocean World",
            "arctic": "Arctic World",
            "jungle": "Jungle World",
            "volcanic": "Volcanic World",
            "gas_giant": "Gas Giant Moon",
            "artificial": "Artificial World"
        }
        
        embed = discord.Embed(
            title="🌍 Homeworld Selected!",
            description=f"You have chosen **{world_names[selected_world]}** as your homeworld!\n\n"
                       f"Your cosmic journey begins on this {selected_world} world.",
            color=0x00ff00
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)


class LeaderboardView(discord.ui.View):
    """Interactive leaderboard with sorting options"""
    
    def __init__(self, leaderboard_data: Dict, current_sort: str = "points"):
        super().__init__(timeout=300)
        self.leaderboard_data = leaderboard_data
        self.current_sort = current_sort
    
    @discord.ui.button(label="By Points", emoji="🏆", style=discord.ButtonStyle.primary)
    async def sort_by_points(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = self.create_leaderboard_embed("points")
        await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.button(label="By Accuracy", emoji="🎯", style=discord.ButtonStyle.secondary)
    async def sort_by_accuracy(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = self.create_leaderboard_embed("accuracy")
        await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.button(label="By Streak", emoji="🔥", style=discord.ButtonStyle.secondary)
    async def sort