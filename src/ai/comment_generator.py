"""AI-powered comment generation using OpenAI.

This module will be implemented in Week 3.
"""

from typing import Optional, List
from openai import OpenAI

from src.config import config
from src.logger import log


class CommentGenerator:
    """Generate contextual comments using AI."""

    def __init__(self):
        """Initialize AI client (OpenRouter or OpenAI)."""
        if config.OPENAI_API_KEY:
            self.client = OpenAI(
                api_key=config.OPENAI_API_KEY,
                base_url=config.OPENAI_BASE_URL
            )
            log.info(f"AI client initialized with base_url: {config.OPENAI_BASE_URL}")
            log.info(f"Using model: {config.OPENAI_MODEL}")
        else:
            self.client = None
            log.warning("AI API key not set. Comment generation will not work.")

    def generate_comment(
        self,
        video_description: str,
        creator_name: Optional[str] = None,
        video_context: Optional[str] = None
    ) -> str:
        """Generate a natural comment for a TikTok video.

        Args:
            video_description: The video's description/caption
            creator_name: Username of the video creator
            video_context: Additional context about the video

        Returns:
            Generated comment text
        """
        if not self.client:
            log.error("OpenAI client not initialized. Cannot generate comment.")
            return self._get_fallback_comment()

        try:
            # Build context for AI
            context_parts = []
            if video_description:
                context_parts.append(f"Video caption: {video_description}")
            if creator_name:
                context_parts.append(f"Creator: @{creator_name}")
            if video_context:
                context_parts.append(f"Context: {video_context}")

            context = "\n".join(context_parts) if context_parts else "A TikTok video"

            # Generate comment using AI
            prompt = self._build_prompt(context)

            log.info(f"Generating comment with model: {config.OPENAI_MODEL}")

            response = self.client.chat.completions.create(
                model=config.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.9,  # High creativity
                max_tokens=100,
            )

            comment = response.choices[0].message.content.strip()

            # Clean up the comment
            comment = self._clean_comment(comment)

            # Validate
            if not self.validate_comment(comment):
                log.warning(f"Generated comment failed validation: {comment}")
                return self._get_fallback_comment()

            log.success(f"Generated comment: {comment}")
            return comment

        except Exception as e:
            log.error(f"Error generating comment: {e}")
            return self._get_fallback_comment()

    def _get_fallback_comment(self) -> str:
        """Get a random fallback comment template.

        Returns:
            A generic comment

        TODO: Implement proper template system in Week 3
        """
        templates = [
            "Love this! 😍",
            "This is amazing! 🔥",
            "Great content! 👏",
            "So creative! ✨",
            "This made my day! 😊"
        ]

        import random
        return random.choice(templates)

    def _get_system_prompt(self) -> str:
        """Get the system prompt for AI comment generation."""
        return """You are a friendly TikTok user who leaves genuine, engaging comments on videos.

Your comments should be:
- Natural and conversational (like a real person)
- Positive and supportive
- Between 5-50 words
- Include 1-2 relevant emojis (not excessive)
- Specific to the video content when possible
- NOT generic spam (avoid "nice video", "great content" alone)
- Authentic and human-like

Examples of good comments:
- "This recipe looks delicious! I'm definitely trying this tonight 😍🍝"
- "Your editing skills are insane! How long did this take? 🔥"
- "I needed this motivation today, thank you 💪"
- "The way you explained this actually makes sense finally! 👏"

Respond with ONLY the comment text, no quotes or extra formatting."""

    def _build_prompt(self, context: str) -> str:
        """Build the user prompt for comment generation."""
        return f"""Generate a natural TikTok comment for this video:

{context}

Write a genuine, engaging comment that a real person would leave. Be specific to the content when possible."""

    def _clean_comment(self, comment: str) -> str:
        """Clean up generated comment text.

        Args:
            comment: Raw comment from AI

        Returns:
            Cleaned comment text
        """
        # Remove surrounding quotes if present
        comment = comment.strip('"\'')

        # Remove "Comment:" prefix if AI added it
        if comment.lower().startswith("comment:"):
            comment = comment[8:].strip()

        # Ensure it ends properly (not mid-sentence)
        if comment and not comment[-1] in ".!?🔥😍💪👏✨🎉":
            # Add period if it's a statement
            if not any(emoji in comment for emoji in "😀😃😄😁😆😅🤣😂🙂🙃😉😊😇🥰😍🤩😘😗☺😚😙🥲😋😛😜🤪😝🤑🤗🤭🤫🤔🤐🤨😐😑😶😏😒🙄😬🤥😌😔😪🤤😴"):
                if len(comment) > 20:  # Only add period for longer statements
                    comment += "."

        return comment

    def validate_comment(self, comment: str) -> bool:
        """Validate that comment is appropriate and not spam.

        Args:
            comment: The comment to validate

        Returns:
            True if comment is valid
        """
        # Length check
        if len(comment) < 5 or len(comment) > 150:
            return False

        # Check for spam patterns
        spam_keywords = [
            "check out my",
            "follow me",
            "click here",
            "link in bio",
            "dm me",
            "check my profile",
            "subscribe",
            "buy now",
            "http://",
            "https://",
            "www.",
        ]

        comment_lower = comment.lower()
        if any(spam in comment_lower for spam in spam_keywords):
            return False

        # Check for excessive emojis (more than 30% of content)
        emoji_count = sum(1 for c in comment if ord(c) > 127)
        if len(comment) > 0 and emoji_count / len(comment) > 0.3:
            return False

        # Check for repeated characters (spam pattern)
        import re
        if re.search(r'(.)\1{4,}', comment):  # 5+ repeated chars
            return False

        return True


# Singleton instance
comment_generator = CommentGenerator()
