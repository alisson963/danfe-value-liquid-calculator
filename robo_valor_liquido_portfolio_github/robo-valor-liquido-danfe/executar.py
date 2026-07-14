from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR / "src"))

from main import processar_documentos


if __name__ == "__main__":
    processar_documentos()
