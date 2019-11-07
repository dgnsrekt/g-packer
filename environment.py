from pathlib import Path

ROOT_DIR = Path(__file__).parent
TEST_DATA_DIR = ROOT_DIR / "test_data"
PRE_PROCESS_DATA = TEST_DATA_DIR / "Pre" # Data pre processing.
POST_PROCESS_DATA = TEST_DATA_DIR / "Post" # Data post processing.

TEST_DATA_DIR.mkdir(exist_ok=True)
PRE_PROCESS_DATA.mkdir(exist_ok=True)
POST_PROCESS_DATA.mkdir(exist_ok=True)


