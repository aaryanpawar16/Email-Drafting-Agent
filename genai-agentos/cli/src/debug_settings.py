import sys
import os

# Dynamically add the root of the project to sys.path
current_file = os.path.abspath(__file__)
project_root = os.path.abspath(os.path.join(current_file, "../../../../"))  # 4 levels up
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    from src.settings import get_settings
except ModuleNotFoundError as e:
    print("❌ Failed to import 'src.settings'. Make sure you're running this from the right directory.")
    print("Current sys.path:", sys.path)
    raise e

def main():
    settings = get_settings()
    print("✅ CLI_BACKEND_ORIGIN_URL:", settings.CLI_BACKEND_ORIGIN_URL)

if __name__ == "__main__":
    main()
