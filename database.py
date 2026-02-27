import os
from datetime import datetime, timezone
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def save_gap_analysis(engagement_id: str, process_description: str, matches: list) -> dict:
    record = {
        "engagement_id": engagement_id,
        "process_description": process_description,
        "matches": matches,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    response = supabase.table("gap_results").insert(record).execute()
    return response.data[0] if response.data else {}
