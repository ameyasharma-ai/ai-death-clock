"""Curated quotes on time, mortality, and intentional living (Memento Mori).

Provides rotating reflections to remind the user to make every breath count.
"""

from __future__ import annotations

import random

QUOTES: list[dict[str, str]] = [
    {
        "quote": "It is not that we have a short time to live, but that we waste a lot of it.",
        "author": "Seneca",
    },
    {
        "quote": "You could leave life right now. Let that determine what you do and say and think.",
        "author": "Marcus Aurelius",
    },
    {
        "quote": "Remembering that you are going to die is the best way I know to avoid the trap of thinking you have something to lose.",
        "author": "Steve Jobs",
    },
    {
        "quote": "Do not act as if you were going to live ten thousand years. Death hangs over you. While you live, while it is in your power, be good.",
        "author": "Marcus Aurelius",
    },
    {
        "quote": "Life is long if you know how to use it.",
        "author": "Seneca",
    },
    {
        "quote": "The trouble is, you think you have time.",
        "author": "Jack Kornfield",
    },
    {
        "quote": "How long are you going to wait before you demand the best for yourself?",
        "author": "Epictetus",
    },
    {
        "quote": "Waste no more time arguing what a good person should be. Be one.",
        "author": "Marcus Aurelius",
    },
    {
        "quote": "Every man has two lives, and the second starts when he realizes he has just one.",
        "author": "Confucius",
    },
    {
        "quote": "Let each thing you do, say, or intend be like that of a dying person.",
        "author": "Marcus Aurelius",
    },
]


def get_random_quote() -> dict[str, str]:
    """Retrieve a random Memento Mori quote.

    Returns:
        dict[str, str]: Dictionary containing 'quote' and 'author'.
    """
    return random.choice(QUOTES)
