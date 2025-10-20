"""
SENTIMENT & TONE ANALYZER TOOL
Advanced sentiment analysis and tone detection
"""

import logging
import json
from typing import Dict, Any, List
from datetime import datetime
from collections import defaultdict

logger = logging.getLogger(__name__)


class SentimentToneAnalyzerTool:
    """Advanced sentiment and tone analysis"""

    def __init__(self):
        self.name = "sentiment_tone_analyzer"
        self.description = "Analyze sentiment, tone, and emotional content"

        # Expanded word lists
        self.positive_words = {
            "love": 2.0, "amazing": 2.0, "excellent": 2.0, "fantastic": 2.0,
            "beautiful": 1.5, "wonderful": 1.5, "great": 1.5, "awesome": 1.5,
            "brilliant": 1.5, "perfect": 1.5, "good": 1.0, "nice": 1.0,
            "happy": 1.5, "delighted": 2.0, "thrilled": 2.0, "proud": 1.5,
            "grateful": 1.5, "blessed": 1.5, "fantastic": 2.0, "incredible": 2.0,
            "outstanding": 2.0, "phenomenal": 2.0, "superb": 1.5, "superior": 1.0
        }

        self.negative_words = {
            "hate": -2.0, "terrible": -2.0, "awful": -2.0, "horrible": -2.0,
            "disgusting": -2.0, "bad": -1.0, "poor": -1.0, "wrong": -1.0,
            "angry": -1.5, "frustrated": -1.5, "disappointed": -1.5, "sad": -1.5,
            "depressed": -2.0, "miserable": -2.0, "pathetic": -2.0, "useless": -2.0,
            "worthless": -2.0, "ridiculous": -1.5, "stupid": -1.5, "dumb": -1.5,
            "fail": -1.5, "failed": -1.5, "broken": -1.0, "problem": -0.5
        }

        self.venting_indicators = {
            "ugh": 1.0, "seriously": 0.8, "rant": 1.5, "frustrated": 1.0,
            "over it": 1.5, "can't believe": 1.0, "unbelievable": 1.0,
            "ridiculous": 1.0, "excuse me": 0.8, "wow": 0.5, "why": 0.3
        }

        self.promotional_indicators = {
            "buy": 2.0, "sale": 2.0, "limited time": 2.0, "offer": 2.0,
            "discount": 2.0, "free": 1.5, "shop": 1.5, "purchase": 1.5,
            "exclusive": 1.5, "now": 0.5, "order": 1.5, "get": 0.5
        }

        self.question_indicators = {
            "what": 1.0, "how": 1.0, "why": 1.0, "when": 1.0, "where": 1.0,
            "can": 0.8, "could": 0.8, "would": 0.8, "should": 0.8,
            "do you": 1.0, "have you": 1.0, "?": 0.5
        }

    async def _execute(
        self,
        content: str,
        detailed: bool = False,
        **kwargs
    ) -> Dict[str, Any]:
        """Analyze sentiment and tone"""

        logger.info("Analyzing sentiment and tone")

        try:
            sentiment = self._analyze_sentiment(content)
            tone = self._analyze_tone(content)
            emotion = self._analyze_emotions(content)
            intensity = self._analyze_intensity(content)

            if detailed:
                word_analysis = self._detailed_word_analysis(content)
            else:
                word_analysis = {}

            return {
                "success": True,
                "sentiment": sentiment,
                "tone": tone,
                "emotion": emotion,
                "intensity": intensity,
                "word_analysis": word_analysis,
                "overall_assessment": self._generate_assessment(sentiment, tone, emotion, intensity),
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Sentiment analysis failed: {str(e)}")
            return {"success": False, "error": str(e)}

    def _analyze_sentiment(self, content: str) -> Dict[str, Any]:
        """Detailed sentiment analysis"""
        content_lower = content.lower()

        positive_score = 0.0
        negative_score = 0.0

        for word, weight in self.positive_words.items():
            positive_score += content_lower.count(word) * weight

        for word, weight in self.negative_words.items():
            negative_score += abs(content_lower.count(word) * weight)

        total_score = positive_score - negative_score
        total_possible = positive_score + negative_score if positive_score + negative_score > 0 else 1

        sentiment_value = total_score / total_possible if total_possible > 0 else 0
        sentiment_value = max(-1.0, min(1.0, sentiment_value))

        if sentiment_value > 0.3:
            sentiment_type = "positive"
        elif sentiment_value < -0.3:
            sentiment_type = "negative"
        else:
            sentiment_type = "neutral"

        return {
            "type": sentiment_type,
            "score": round(sentiment_value, 2),
            "positive_score": round(positive_score, 2),
            "negative_score": round(negative_score, 2),
            "confidence": round(abs(sentiment_value), 2)
        }

    def _analyze_tone(self, content: str) -> Dict[str, Any]:
        """Analyze message tone"""
        content_lower = content.lower()

        # Calculate tone scores
        venting_score = sum(content_lower.count(word) * weight
                           for word, weight in self.venting_indicators.items())
        promotional_score = sum(content_lower.count(word) * weight
                               for word, weight in self.promotional_indicators.items())
        question_score = sum(content_lower.count(word) * weight
                            for word, weight in self.question_indicators.items())
        informative_score = len(content_lower.split()) * 0.1  # Longer content = informative

        scores = {
            "venting": venting_score,
            "promotional": promotional_score,
            "question": question_score,
            "informative": informative_score
        }

        # Determine primary tone
        primary_tone = max(scores.items(), key=lambda x: x[1])[0] if scores else "neutral"

        # Check for formality
        is_formal = any(phrase in content for phrase in [
            "Dear", "Sincerely", "Regards", "Furthermore", "However",
            "Therefore", "Moreover", "Additionally"
        ])
        is_casual = any(word in content_lower for word in [
            "lol", "haha", "omg", "btw", "tbh", "imho", "etc"
        ])
        is_urgent = any(word in content_lower for word in [
            "urgent", "asap", "immediately", "right now", "emergency"
        ])

        formality = "formal" if is_formal else "casual" if is_casual else "semi-formal"

        return {
            "primary_tone": primary_tone,
            "tone_scores": {k: round(v, 1) for k, v in scores.items()},
            "formality": formality,
            "urgency": "high" if is_urgent else "low",
            "tone_blend": self._describe_tone_blend(scores)
        }

    def _analyze_emotions(self, content: str) -> Dict[str, Any]:
        """Detect specific emotions"""
        content_lower = content.lower()

        emotion_indicators = {
            "joy": ["happy", "excited", "thrilled", "delighted", "ecstatic", "joyful"],
            "sadness": ["sad", "depressed", "miserable", "unhappy", "down", "lonely"],
            "anger": ["angry", "furious", "rage", "mad", "livid", "hateful"],
            "fear": ["scared", "afraid", "terrified", "anxious", "worried", "nervous"],
            "disgust": ["disgusting", "gross", "revolting", "vile", "repulsive"],
            "surprise": ["shocked", "surprised", "amazed", "astonished", "stunned"],
            "anticipation": ["excited", "anticipating", "looking forward", "can't wait"],
            "trust": ["confident", "trust", "sure", "certain", "reliable"]
        }

        emotion_scores = {}
        for emotion, keywords in emotion_indicators.items():
            score = sum(1 for keyword in keywords if keyword in content_lower)
            emotion_scores[emotion] = score

        primary_emotion = max(emotion_scores.items(), key=lambda x: x[1])[0] if emotion_scores else "neutral"

        return {
            "primary_emotion": primary_emotion,
            "emotion_breakdown": emotion_scores,
            "emotional_intensity": self._calculate_emotional_intensity(emotion_scores),
            "emotional_range": self._calculate_emotional_range(emotion_scores)
        }

    def _analyze_intensity(self, content: str) -> Dict[str, Any]:
        """Analyze content intensity"""

        # All caps ratio
        all_caps_ratio = sum(1 for c in content if c.isupper()) / len(content) if content else 0

        # Exclamation mark ratio
        exclamation_count = content.count("!")
        exclamation_ratio = exclamation_count / len(content.split()) if content else 0

        # Question ratio
        question_count = content.count("?")
        question_ratio = question_count / len(content.split()) if content else 0

        # Repetition (repeated punctuation)
        repeated_punct = any(punct * 2 in content for punct in "!?")

        # Length indicators
        word_count = len(content.split())
        is_short = word_count < 50
        is_long = word_count > 300

        # Calculate overall intensity
        intensity_score = (
            all_caps_ratio * 0.3 +
            exclamation_ratio * 0.3 +
            question_ratio * 0.2 +
            (0.2 if repeated_punct else 0)
        )
        intensity_score = min(1.0, intensity_score * 2)  # Normalize to 0-1

        return {
            "overall_intensity": round(intensity_score, 2),
            "all_caps_ratio": round(all_caps_ratio, 2),
            "exclamation_count": exclamation_count,
            "exclamation_ratio": round(exclamation_ratio, 2),
            "question_count": question_count,
            "question_ratio": round(question_ratio, 2),
            "repeated_punctuation": repeated_punct,
            "length_category": "short" if is_short else "long" if is_long else "medium",
            "intensity_level": "high" if intensity_score > 0.6 else "medium" if intensity_score > 0.3 else "low"
        }

    def _detailed_word_analysis(self, content: str) -> Dict[str, Any]:
        """Detailed word-by-word analysis"""
        content_lower = content.lower()
        words = content.split()

        positive_words_found = [w for w in words if w.lower() in self.positive_words]
        negative_words_found = [w for w in words if w.lower() in self.negative_words]
        venting_words_found = [w for w in words if w.lower() in self.venting_indicators]
        promotional_words_found = [w for w in words if w.lower() in self.promotional_indicators]

        return {
            "positive_words": list(set(positive_words_found)),
            "negative_words": list(set(negative_words_found)),
            "venting_words": list(set(venting_words_found)),
            "promotional_words": list(set(promotional_words_found)),
            "total_sentiment_words": len(positive_words_found) + len(negative_words_found)
        }

    def _generate_assessment(self, sentiment: Dict, tone: Dict, emotion: Dict, intensity: Dict) -> str:
        """Generate human-readable assessment"""
        assessment = f"This content is {sentiment['type']} in sentiment "
        assessment += f"with a {tone['primary_tone']} tone and {tone['formality']} formality. "

        if emotion['primary_emotion'] != "neutral":
            assessment += f"Primary emotion: {emotion['primary_emotion']}. "

        assessment += f"Intensity level: {intensity['intensity_level']}. "

        return assessment

    def _describe_tone_blend(self, scores: Dict) -> str:
        """Describe the blend of tones"""
        sorted_tones = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        if sorted_tones[0][1] == 0:
            return "neutral"

        top_tones = [tone for tone, score in sorted_tones[:2] if score > 0]
        if len(top_tones) == 1:
            return top_tones[0]
        elif len(top_tones) == 2:
            return f"{top_tones[0]} with {top_tones[1]} elements"
        else:
            return "mixed"

    def _calculate_emotional_intensity(self, emotions: Dict) -> str:
        """Calculate overall emotional intensity"""
        total = sum(emotions.values())
        if total == 0:
            return "neutral"
        elif total > 5:
            return "high"
        elif total > 2:
            return "moderate"
        else:
            return "low"

    def _calculate_emotional_range(self, emotions: Dict) -> int:
        """Calculate how many emotions are present"""
        return sum(1 for count in emotions.values() if count > 0)


class ToneAdjustmentTool:
    """Adjust tone of content for different contexts"""

    def __init__(self):
        self.name = "tone_adjustment"
        self.description = "Adjust content tone for different contexts"

    async def _execute(
        self,
        content: str,
        target_tone: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Adjust tone of content"""

        logger.info(f"Adjusting tone to: {target_tone}")

        try:
            adjusted = self._adjust_tone(content, target_tone)

            return {
                "success": True,
                "original_content": content,
                "adjusted_content": adjusted["content"],
                "target_tone": target_tone,
                "adjustments_made": adjusted["changes"],
                "tone_shift": adjusted["shift_description"],
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Tone adjustment failed: {str(e)}")
            return {"success": False, "error": str(e)}

    def _adjust_tone(self, content: str, target_tone: str) -> Dict[str, Any]:
        """Adjust tone based on target"""

        if target_tone.lower() == "professional":
            return self._to_professional(content)
        elif target_tone.lower() == "casual":
            return self._to_casual(content)
        elif target_tone.lower() == "friendly":
            return self._to_friendly(content)
        elif target_tone.lower() == "authoritative":
            return self._to_authoritative(content)
        elif target_tone.lower() == "humorous":
            return self._to_humorous(content)
        elif target_tone.lower() == "sympathetic":
            return self._to_sympathetic(content)
        else:
            return {"content": content, "changes": [], "shift_description": "No tone shift applied"}

    def _to_professional(self, content: str) -> Dict[str, Any]:
        """Convert to professional tone"""
        adjusted = content
        changes = []

        # Replace casual language
        casual_replacements = {
            "lol": "respectfully",
            "omg": "notably",
            "btw": "additionally",
            "gonna": "will",
            "wanna": "would like to",
            "kinda": "somewhat",
            "sorta": "rather",
            "'ll": " will"
        }

        for casual, professional in casual_replacements.items():
            if casual in adjusted.lower():
                adjusted = adjusted.replace(casual, professional)
                adjusted = adjusted.replace(casual.upper(), professional.upper())
                changes.append(f"Replaced '{casual}' with '{professional}'")

        # Add formal greeting if missing
        if not any(greeting in adjusted for greeting in ["Dear", "Hello", "Greetings"]):
            adjusted = "Dear colleague,\n\n" + adjusted
            changes.append("Added formal greeting")

        return {
            "content": adjusted,
            "changes": changes,
            "shift_description": "Shifted to professional, formal tone"
        }

    def _to_casual(self, content: str) -> Dict[str, Any]:
        """Convert to casual tone"""
        adjusted = content
        changes = []

        # Remove formal language
        formal_replacements = {
            "Furthermore": "Plus,",
            "Moreover": "And",
            "However": "But",
            "Therefore": "So",
            "Sincerely": "Cheers"
        }

        for formal, casual in formal_replacements.items():
            if formal in adjusted:
                adjusted = adjusted.replace(formal, casual)
                changes.append(f"Replaced '{formal}' with '{casual}'")

        # Add casual markers
        if "!" not in adjusted:
            adjusted = adjusted + "!"
            changes.append("Added enthusiasm marker")

        return {
            "content": adjusted,
            "changes": changes,
            "shift_description": "Shifted to casual, conversational tone"
        }

    def _to_friendly(self, content: str) -> Dict[str, Any]:
        """Convert to friendly tone"""
        adjusted = content
        changes = []

        # Add warm language
        adjusted = adjusted.replace("You should", "You might want to")
        adjusted = adjusted.replace("Must", "Should")
        adjusted = adjusted.replace("Required", "Helpful")

        # Add emojis if missing
        if "😊" not in adjusted and "🙂" not in adjusted:
            adjusted += " 😊"
            changes.append("Added friendly emoji")

        # Add conversational phrases
        if "I appreciate" not in adjusted:
            adjusted = adjusted + "\n\nThanks for your time!"
            changes.append("Added appreciation phrase")

        changes.append("Adjusted for warmer, more approachable tone")

        return {
            "content": adjusted,
            "changes": changes,
            "shift_description": "Shifted to friendly, approachable tone"
        }

    def _to_authoritative(self, content: str) -> Dict[str, Any]:
        """Convert to authoritative tone"""
        adjusted = content
        changes = []

        # Add authoritative language
        adjusted = adjusted.replace("I think", "Research shows")
        adjusted = adjusted.replace("might", "will")
        adjusted = adjusted.replace("could", "will")
        adjusted = adjusted.replace("maybe", "certainly")

        # Add statements of confidence
        if "important" not in adjusted.lower():
            adjusted = "It's important to understand that " + adjusted
            changes.append("Added authoritative opener")

        changes.append("Strengthened claims and assertions")

        return {
            "content": adjusted,
            "changes": changes,
            "shift_description": "Shifted to authoritative, confident tone"
        }

    def _to_humorous(self, content: str) -> Dict[str, Any]:
        """Convert to humorous tone"""
        adjusted = content
        changes = []

        # Add light-hearted language
        adjusted = adjusted.replace("problem", "plot twist")
        adjusted = adjusted.replace("difficult", "spicy")
        adjusted = adjusted.replace("boring", "snooze-fest")

        # Add humor markers
        if "😄" not in adjusted:
            adjusted += " 😄"
            changes.append("Added humorous emoji")

        changes.append("Injected humor and light-hearted language")

        return {
            "content": adjusted,
            "changes": changes,
            "shift_description": "Shifted to humorous, witty tone"
        }

    def _to_sympathetic(self, content: str) -> Dict[str, Any]:
        """Convert to sympathetic tone"""
        adjusted = content
        changes = []

        # Add empathetic language
        adjusted = adjusted.replace("You should", "I understand you might need to")
        adjusted = adjusted.replace("wrong", "challenging")
        adjusted = adjusted.replace("stupid", "confusing")

        # Add validation phrases
        adjusted = "I completely understand. " + adjusted
        changes.append("Added empathetic validation")

        return {
            "content": adjusted,
            "changes": changes,
            "shift_description": "Shifted to sympathetic, empathetic tone"
        }


# Singleton instances
sentiment_tone_analyzer = SentimentToneAnalyzerTool()
tone_adjustment = ToneAdjustmentTool()
