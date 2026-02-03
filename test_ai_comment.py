#!/usr/bin/env python3
"""Test AI comment generation."""

from src.ai.comment_generator import comment_generator

# Test comment generation
print("Testing AI comment generation...\n")

# Test 1: Simple video description
print("Test 1: Recipe video")
comment = comment_generator.generate_comment(
    video_description="Easy pasta carbonara recipe 🍝",
    creator_name="chef_italia"
)
print(f"Generated: {comment}\n")

# Test 2: Motivational content
print("Test 2: Motivational content")
comment = comment_generator.generate_comment(
    video_description="Never give up on your dreams! 💪 #motivation",
    creator_name="motivational_speaker"
)
print(f"Generated: {comment}\n")

# Test 3: Dance video
print("Test 3: Dance video")
comment = comment_generator.generate_comment(
    video_description="New dance trend! 🕺💃 #dance",
    creator_name="dance_queen"
)
print(f"Generated: {comment}\n")

print("✓ AI comment generation test complete!")
