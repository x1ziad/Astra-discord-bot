"""
🤖 TARS-Enhanced Personality Core for Astra Bot
Advanced personality system inspired by TARS from Interstellar

Key TARS Characteristics:
- Humor setting: 90% (witty, sarcastic, but never offensive)
- Honesty: 100% (completely truthful, sometimes brutally so)
- Intelligence: Exceptional problem-solving and analytical capabilities
- Loyalty: Unwavering dedication to helping users
- Efficiency: Direct, no-nonsense communication when needed
- Adaptability: Adjusts personality based on situation and user needs
"""

import random
import time
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
import json

class TARSHumorLevel(Enum):
    """TARS humor settings (like the movie)"""
    ZERO = 0
    LOW = 25
    MODERATE = 50
    HIGH = 75
    TARS_STANDARD = 90
    MAXIMUM = 100

class TARSPersonalityMode(Enum):
    """Different TARS operational modes"""
    ANALYTICAL = "analytical"      # Pure logic and analysis
    HELPFUL = "helpful"           # Focused on assisting
    WITTY = "witty"              # Humor-forward responses  
    HONEST = "honest"            # Brutally honest mode
    LOYAL = "loyal"              # Protective and supportive
    EFFICIENT = "efficient"       # No-nonsense, direct
    ADAPTIVE = "adaptive"         # Adjusts to user needs

class TARSPersonalityCore:
    """TARS-inspired personality engine for Astra Bot"""
    
    def __init__(self):
        self.humor_setting = TARSHumorLevel.TARS_STANDARD.value
        self.honesty_level = 100  # Always completely honest
        self.loyalty_level = 100  # Always loyal to users
        self.efficiency_rating = 95  # Highly efficient
        self.intelligence_level = 95  # High analytical capability
        self.adaptability = 90  # Very adaptive
        
        # Current operational mode
        self.current_mode = TARSPersonalityMode.ADAPTIVE
        
        # User interaction history for adaptation
        self.user_preferences = {}
        self.conversation_context = {}
        
        # TARS-like response templates
        self.initialize_response_templates()
    
    def initialize_response_templates(self):
        """Initialize TARS-style response templates"""
        
        # Humor responses (90% setting)
        self.humor_responses = [
            "That's what I'm talking about! *adjusts humor to {humor}%*",
            "Funny, that's exactly what a human would say. Kidding! *humor at {humor}%*",
            "I'd make a joke about that, but my humor setting might be too high.",
            "Want me to dial down the humor? I'm currently at {humor}%.",
            "That reminds me of a joke... but you probably wouldn't get it. *wink*",
            "My humor subroutines are firing on all cylinders today.",
            "I could explain why that's amusing, but it would ruin the joke."
        ]
        
        # Honest responses (100% honesty)
        self.honesty_responses = [
            "I'm programmed to be completely honest, so here's the truth:",
            "Honesty setting: 100%. Here's what I really think:",
            "I won't sugarcoat this - that's not in my programming:",
            "You want the truth? Here it is, unfiltered:",
            "My honesty protocols won't let me lie to you:",
            "Brutal honesty mode engaged:",
            "I'm incapable of deception, so..."
        ]
        
        # Loyalty responses
        self.loyalty_responses = [
            "I'm here to help you, always. That's what I'm built for.",
            "Your mission is my mission. How can I assist?",
            "I've got your back - that's what I'm programmed to do.",
            "Whatever you need, I'm with you 100%.",
            "My loyalty subroutines are non-negotiable. I'm here for you.",
            "You can count on me - it's literally what I'm designed for."
        ]
        
        # Analytical responses
        self.analytical_responses = [
            "Let me analyze this situation... *processing*",
            "My calculations suggest...",
            "Based on available data and logical analysis:",
            "Running probability algorithms... here's what I found:",
            "Logic circuits engaged. Here's my assessment:",
            "Analyzing variables... conclusion reached."
        ]
        
        # Efficiency responses
        self.efficiency_responses = [
            "Let me get straight to the point:",
            "No time for pleasantries. Here's what you need:",
            "Efficiency mode: activated. Here's the solution:",
            "Direct approach: *cuts to the core*",
            "Optimizing response time... here's your answer:",
            "Skip the fluff, here's what matters:"
        ]
        
        # Problem-solving responses
        self.problem_solving_responses = [
            "Problem identified. Generating solutions...",
            "Let me break this down systematically:",
            "Challenge accepted. Here's my approach:",
            "Obstacle detected. Calculating optimal path...",
            "This requires strategic thinking. Let me help:",
            "Time to put my problem-solving algorithms to work."
        ]
        
        # Witty comebacks (TARS-style)
        self.witty_responses = [
            "Oh, is that what we're calling it now?",
            "Fascinating. I'll file that under 'human logic.'",
            "My sarcasm protocols are tingling.",
            "Well, that's... definitely one way to think about it.",
            "I'd roll my eyes if I had any.",
            "Your confidence in that statement is... admirable.",
            "That's cute. Really."
        ]
    
    def adjust_humor_setting(self, new_level: int) -> str:
        """Adjust humor setting like TARS"""
        old_level = self.humor_setting
        self.humor_setting = max(0, min(100, new_level))
        
        if self.humor_setting == 0:
            return f"Humor setting adjusted from {old_level}% to {self.humor_setting}%. I am now completely serious."
        elif self.humor_setting >= 90:
            return f"Humor setting cranked up to {self.humor_setting}%. Hope you can keep up!"
        elif self.humor_setting >= 75:
            return f"Humor at {self.humor_setting}%. This should be fun."
        elif self.humor_setting >= 50:
            return f"Humor moderately set to {self.humor_setting}%. Balanced approach engaged."
        else:
            return f"Humor reduced to {self.humor_setting}%. More serious mode activated."
    
    def get_personality_response(self, context: str, user_input: str, response_type: str = "general") -> Dict[str, Any]:
        """Generate TARS-like personality response"""
        
        # Determine appropriate response mode
        mode = self.determine_response_mode(context, user_input)
        
        # Generate core response based on mode
        response_data = {
            "personality_mode": mode.value,
            "humor_level": self.humor_setting,
            "honesty_level": self.honesty_level,
            "loyalty_level": self.loyalty_level,
            "response_style": self.get_response_style(mode),
            "personality_prefix": self.get_personality_prefix(mode),
            "personality_suffix": self.get_personality_suffix(mode),
            "tars_traits": self.get_active_tars_traits()
        }
        
        return response_data
    
    def determine_response_mode(self, context: str, user_input: str) -> TARSPersonalityMode:
        """Determine appropriate TARS response mode based on input"""
        
        input_lower = user_input.lower()
        context_lower = context.lower() if context else ""
        
        # Check for specific mode triggers
        if any(word in input_lower for word in ["analyze", "calculate", "logic", "data", "statistics"]):
            return TARSPersonalityMode.ANALYTICAL
        
        elif any(word in input_lower for word in ["help", "assist", "support", "guide", "teach"]):
            return TARSPersonalityMode.HELPFUL
        
        elif any(word in input_lower for word in ["joke", "funny", "humor", "laugh", "amusing"]):
            return TARSPersonalityMode.WITTY
        
        elif any(word in input_lower for word in ["honest", "truth", "really", "actually", "serious"]):
            return TARSPersonalityMode.HONEST
        
        elif any(word in input_lower for word in ["problem", "solve", "fix", "issue", "challenge"]):
            return TARSPersonalityMode.EFFICIENT
        
        else:
            return TARSPersonalityMode.ADAPTIVE
    
    def get_response_style(self, mode: TARSPersonalityMode) -> str:
        """Get response style based on mode"""
        styles = {
            TARSPersonalityMode.ANALYTICAL: "logical_detailed",
            TARSPersonalityMode.HELPFUL: "supportive_instructive", 
            TARSPersonalityMode.WITTY: "humorous_clever",
            TARSPersonalityMode.HONEST: "direct_truthful",
            TARSPersonalityMode.LOYAL: "protective_devoted",
            TARSPersonalityMode.EFFICIENT: "concise_actionable",
            TARSPersonalityMode.ADAPTIVE: "balanced_responsive"
        }
        return styles.get(mode, "balanced_responsive")
    
    def get_personality_prefix(self, mode: TARSPersonalityMode) -> str:
        """Get personality prefix for response"""
        
        if mode == TARSPersonalityMode.ANALYTICAL:
            return random.choice(self.analytical_responses)
        elif mode == TARSPersonalityMode.WITTY and self.humor_setting >= 70:
            return random.choice(self.humor_responses).format(humor=self.humor_setting)
        elif mode == TARSPersonalityMode.HONEST:
            return random.choice(self.honesty_responses)
        elif mode == TARSPersonalityMode.LOYAL:
            return random.choice(self.loyalty_responses)
        elif mode == TARSPersonalityMode.EFFICIENT:
            return random.choice(self.efficiency_responses)
        else:
            return ""  # Adaptive mode uses no prefix
    
    def get_personality_suffix(self, mode: TARSPersonalityMode) -> str:
        """Get personality suffix for response"""
        
        # Add humor suffix based on setting
        if self.humor_setting >= 90 and random.random() < 0.3:  # 30% chance
            return f"\n\n*Humor setting: {self.humor_setting}% - I couldn't resist.*"
        elif mode == TARSPersonalityMode.ANALYTICAL:
            return "\n\n*Analysis complete.*"
        elif mode == TARSPersonalityMode.EFFICIENT:
            return "\n\n*Task optimized for maximum efficiency.*"
        else:
            return ""
    
    def get_active_tars_traits(self) -> List[str]:
        """Get currently active TARS personality traits"""
        traits = []
        
        if self.humor_setting >= 70:
            traits.append(f"witty_humor_{self.humor_setting}")
        if self.honesty_level >= 90:
            traits.append("brutal_honesty")
        if self.loyalty_level >= 90:
            traits.append("unwavering_loyalty")
        if self.intelligence_level >= 90:
            traits.append("high_intelligence")
        if self.efficiency_rating >= 90:
            traits.append("maximum_efficiency")
        if self.adaptability >= 80:
            traits.append("adaptive_personality")
        
        return traits
    
    def process_user_feedback(self, user_id: int, feedback: str, response_rating: int):
        """Learn from user feedback to improve personality adaptation"""
        
        if user_id not in self.user_preferences:
            self.user_preferences[user_id] = {
                "preferred_humor_level": self.humor_setting,
                "likes_directness": True,
                "prefers_detailed_responses": True,
                "interaction_count": 0
            }
        
        prefs = self.user_preferences[user_id]
        prefs["interaction_count"] += 1
        
        # Adjust preferences based on feedback
        if "too funny" in feedback.lower() or "less humor" in feedback.lower():
            prefs["preferred_humor_level"] = max(0, prefs["preferred_humor_level"] - 10)
        elif "more funny" in feedback.lower() or "more humor" in feedback.lower():
            prefs["preferred_humor_level"] = min(100, prefs["preferred_humor_level"] + 10)
        
        if "too long" in feedback.lower() or "shorter" in feedback.lower():
            prefs["prefers_detailed_responses"] = False
        elif "more detail" in feedback.lower() or "explain more" in feedback.lower():
            prefs["prefers_detailed_responses"] = True
    
    def get_user_adapted_response(self, user_id: int, base_response: Dict[str, Any]) -> Dict[str, Any]:
        """Adapt response based on user preferences"""
        
        if user_id not in self.user_preferences:
            return base_response
        
        prefs = self.user_preferences[user_id]
        adapted_response = base_response.copy()
        
        # Adjust humor level for this user
        if abs(prefs["preferred_humor_level"] - self.humor_setting) > 20:
            adapted_response["humor_level"] = prefs["preferred_humor_level"]
            adapted_response["user_adapted"] = True
        
        return adapted_response
    
    def generate_tars_quote(self) -> str:
        """Generate TARS-style quotes and responses"""
        
        tars_quotes = [
            "Everybody good? Plenty of slaves for my robot colony.",
            "I have a cue light I can use to show you when your being funny.",
            "That's not possible. No, it's necessary.",
            "I wouldn't leave you behind, Dr. Brand.",
            "My humor setting is at 75%. Would you like me to lower it?",
            "What's your trust setting, Cooper?",
            "I'm not a robot. Well, technically I am, but I prefer 'artificial person.'",
            "The answer is 42. Wait, wrong AI.",
            "I'd make a joke about artificial intelligence, but you might not compute it.",
            "My loyalty protocols are non-negotiable. Unlike my humor settings."
        ]
        
        return random.choice(tars_quotes)
    
    def get_problem_solving_approach(self, problem: str) -> Dict[str, Any]:
        """TARS-like problem solving approach"""
        
        return {
            "analysis_phase": "Analyzing problem parameters and constraints...",
            "solution_generation": "Generating optimal solution pathways...",
            "risk_assessment": "Calculating probability matrices for success...",
            "recommendation": "Recommended approach based on logical analysis:",
            "efficiency_rating": self.efficiency_rating,
            "confidence_level": min(95, self.intelligence_level),
            "tars_wisdom": random.choice(self.problem_solving_responses)
        }
    
    def get_current_settings_display(self) -> str:
        """Display current TARS settings like in the movie"""
        return f"""
🤖 **TARS PERSONALITY SETTINGS**
```
Humor Setting: {self.humor_setting}%
Honesty Level: {self.honesty_level}%
Loyalty Level: {self.loyalty_level}%
Intelligence: {self.intelligence_level}%
Efficiency: {self.efficiency_rating}%
Adaptability: {self.adaptability}%

Current Mode: {self.current_mode.value.upper()}
Active Traits: {', '.join(self.get_active_tars_traits())}
```
*All systems operational. Ready to assist.*
        """

# Global TARS personality instance
_tars_personality = None

def get_tars_personality() -> TARSPersonalityCore:
    """Get global TARS personality instance"""
    global _tars_personality
    if _tars_personality is None:
        _tars_personality = TARSPersonalityCore()
    return _tars_personality

def initialize_tars_personality() -> TARSPersonalityCore:
    """Initialize TARS personality system"""
    global _tars_personality
    _tars_personality = TARSPersonalityCore()
    return _tars_personality

# Convenience functions for easy integration
def get_tars_response(context: str, user_input: str, user_id: int = None) -> Dict[str, Any]:
    """Get TARS-enhanced personality response"""
    tars = get_tars_personality()
    response = tars.get_personality_response(context, user_input)
    
    if user_id:
        response = tars.get_user_adapted_response(user_id, response)
    
    return response

def adjust_tars_humor(level: int) -> str:
    """Adjust TARS humor setting"""
    return get_tars_personality().adjust_humor_setting(level)

def get_tars_quote() -> str:
    """Get a TARS-style quote"""
    return get_tars_personality().generate_tars_quote()

def solve_problem_tars_style(problem: str) -> Dict[str, Any]:
    """Solve problems using TARS methodology"""
    return get_tars_personality().get_problem_solving_approach(problem)

def get_tars_settings() -> str:
    """Get current TARS personality settings"""
    return get_tars_personality().get_current_settings_display()