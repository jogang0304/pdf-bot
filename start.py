import logging
import os
import sys

import dotenv

from src.main import main

logging.basicConfig(level=logging.INFO, stream=sys.stdout)

dotenv.load_dotenv()

TOKEN = os.getenv("TOKEN")

if not TOKEN:
    logging.error("No TOKEN environment variable")
    sys.exit(1)


main(TOKEN)
