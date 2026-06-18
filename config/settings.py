import os
import sys
from dotenv import load_dotenv

# Load Environment Variables
load_dotenv()

USING_NEW_SDK = False
genai_client = None
genai_legacy = None

try:
    # Menggunakan Google GenAI SDK Baru (pip install google-genai)
    from google import genai
    USING_NEW_SDK = True
except ImportError:
    try:
        # Fallback ke legacy SDK (pip install google-generativeai)
        import google.generativeai as genai_legacy
        USING_NEW_SDK = False
    except ImportError:
        genai_legacy = None
        USING_NEW_SDK = False