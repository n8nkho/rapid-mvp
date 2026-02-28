"""
Set environment variables before any module imports so that database.py
can initialise its supabase client with non-None values during tests.
"""
import os

os.environ.setdefault("SUPABASE_URL", "https://fake.supabase.co")
os.environ.setdefault("SUPABASE_KEY", "fake-supabase-key")
os.environ.setdefault("ANTHROPIC_API_KEY", "sk-ant-fake")
