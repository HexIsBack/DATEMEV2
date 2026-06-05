#!/usr/bin/env python
import os, sys
from pathlib import Path

def load_dotenv():
    """Load variables from a .env file into os.environ (no extra packages needed)."""
    env_path = Path(__file__).resolve().parent / '.env'
    if not env_path.exists():
        return
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            # Skip blank lines and comments
            if not line or line.startswith('#'):
                continue
            if '=' not in line:
                continue
            key, _, value = line.partition('=')
            key   = key.strip()
            value = value.strip().strip('"').strip("'")
            # Don't overwrite variables already set in the environment
            os.environ.setdefault(key, value)

def main():
    load_dotenv()
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dateme.settings')
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()
