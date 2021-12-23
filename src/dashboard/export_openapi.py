from dotenv import load_dotenv
from pathlib import Path
import json

for envfile in ['token.env', 'site.env']:
    load_dotenv(Path(__file__).parent / '../..' / envfile)

from main import app
print(json.dumps(app.openapi()))