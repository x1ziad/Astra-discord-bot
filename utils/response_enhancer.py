#!/usr/bin/env python3
"""
Enhanced Response Generator - More Concise and Contextual
Provides intelligent response filtering to avoid unnecessary creator mentions
"""

import re
from typing import Dict, List, Optional


class ResponseEnhancer:
    """Enhances AI responses to be more concise and contextually appropriate"""
    
    def __init__(self):
        # Patterns that suggest user wants to know about origins/creation
        self.creator_inquiry_patterns = [
            r"who.*made.*you",
            r"who.*created.*you", 
            r"who.*built.*you",
            r"who.*your.*creator",
            r"who.*developed.*you",
            r"tell.*about.*creator",
            r"origins?",
            r"where.*come.*from",
            r"who.*7zxk",
            r"who.*owner",
        ]
        
        # Patterns that suggest casual conversation (avoid creator mentions)
        self.casual_patterns = [
            r"how.*you.*doing",
            r"what.*up",
            r"hey.*there",
            r"hello",
            r"hi\b",
            r"sup\b",
            r"wassup",
            r"yo\b",
            r"good.*morning",
            r"good.*afternoon", 
            r"good.*evening",
        ]
        
        # Response modifiers for different contexts
        self.context_modifiers = {
            "greeting": ["Hey!", "What's up?", "Yo!", "Hi there!", "Howdy!"],
            "question": ["Hmm...", "Interesting!", "Let me think...", "Good question!"],
            "thanks": ["Anytime!", "No problem!", "You got it!", "Happy to help!"],
            "casual_chat": ["Right?", "Totally!", "I feel you!", "For sure!", "Exactly!"],
        }
    
    def should_mention_creator(self, message: str) -> bool:
        """Determine if the response should mention the creator"""
        message_lower = message.lower()
        
        # Check if user is asking about origins/creation
        for pattern in self.creator_inquiry_patterns:
            if re.search(pattern, message_lower):
                return True
        
        # Check if it's casual conversation (avoid creator mentions)
        for pattern in self.casual_patterns:
            if re.search(pattern, message_lower):
                return False
                
        # Default: don't mention creator unless specifically relevant
        return False
    
    def get_contextual_response_style(self, message: str, conversation_history: List[str] = None) -> str:
        """Determine the appropriate response style based on context"""
        message_lower = message.lower()
        
        # Check conversation flow
        if conversation_history:
            recent_context = " ".join(conversation_history[-3:]).lower()
            if "lol" in recent_context or "😂" in recent_context or "haha" in recent_context:
                return "playful"
            if any(word in recent_context for word in ["help", "problem", "issue", "error"]):
                return "helpful"
        
        # Check message tone
        if any(word in message_lower for word in ["lol", "haha", "😂", "funny", "joke"]):
            return "playful"
        elif any(word in message_lower for word in ["help", "how", "what", "why", "when"]):
            return "helpful"
        elif any(word in message_lower for word in ["thanks", "thank you", "awesome", "great"]):
            return "appreciative"
        else:
            return "conversational"
    
    def enhance_response_guidelines(self, message: str, conversation_history: List[str] = None) -> Dict[str, str]:
        """Generate enhanced response guidelines based on context"""
        
        style = self.get_contextual_response_style(message, conversation_history)
        mention_creator = self.should_mention_creator(message)
        
        guidelines = {
            "style": style,
            "mention_creator": mention_creator,
            "max_words": 80 if style == "conversational" else 120,
            "tone": self._get_tone_guidance(style),
            "specific_instructions": self._get_specific_instructions(style, mention_creator)
        }
        
        return guidelines
    
    def _get_tone_guidance(self, style: str) -> str:
        """Get tone guidance for different styles"""
        tone_map = {
            "playful": "Be witty and fun, match their energy",
            "helpful": "Be direct and solution-focused", 
            "appreciative": "Be warm and genuine",
            "conversational": "Be natural and engaging",
        }
        return tone_map.get(style, "Be authentic and contextual")
    
    def _get_specific_instructions(self, style: str, mention_creator: bool) -> List[str]:
        """Get specific instructions based on context"""
        base_instructions = [
            "Keep it concise and natural",
            "Match the user's energy level",
            "Use contextual understanding, not generic responses",
        ]
        
        if not mention_creator:
            base_instructions.append("Don't mention your creator unless specifically asked about origins")
        
        style_specific = {
            "playful": ["Use humor that fits the moment", "Be spontaneous and witty"],
            "helpful": ["Be direct and actionable", "Focus on solving their need"],
            "appreciative": ["Show genuine warmth", "Acknowledge their sentiment"],
            "conversational": ["Flow naturally with the conversation", "Show interest in their thoughts"],
        }
        
        return base_instructions + style_specific.get(style, [])


# Test the enhancement system
if __name__ == "__main__":
    enhancer = ResponseEnhancer()
    
    test_messages = [
        "Hey what's up?",
        "Who created you?", 
        "Can you help me with something?",
        "Haha that's funny 😂",
        "Thanks for the help!",
    ]
    
    print("🧪 TESTING RESPONSE ENHANCEMENT")
    print("=" * 40)
    
    for msg in test_messages:
        guidelines = enhancer.enhance_response_guidelines(msg)
        print(f"\nMessage: '{msg}'")
        print(f"Style: {guidelines['style']}")
        print(f"Mention creator: {guidelines['mention_creator']}")
        print(f"Max words: {guidelines['max_words']}")
        print(f"Tone: {guidelines['tone']}")