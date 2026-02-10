import glob
import json
import os
import shutil
import stat
from pathlib import Path

from modules.rag_engine import build_vector_store

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data" / "cs"
PERSIST_DIR = ROOT / "vector_db"
DOMAIN = "cs"


def load_docs() -> list[dict]:
    docs = []
    for path in glob.glob(str(DATA_DIR / "qa_*.jsonl")):
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                obj = json.loads(line)
                content = f"{obj.get('question','')}\n{obj.get('answer','')}"
                metadata = {
                    "topic": obj.get("topic", ""),
                    "difficulty": obj.get("difficulty", ""),
                }
                docs.append({"content": content, "metadata": metadata})
    return docs


def _on_rm_error(func, path, exc_info):
    # Handle read-only files on Windows when removing existing vector store
    try:
        os.chmod(path, stat.S_IWRITE)
        func(path)
    except Exception:
        pass


def main():
    docs = load_docs()
    if not docs:
        raise SystemExit("No docs found in data/cs")
    target_dir = PERSIST_DIR / DOMAIN
    if target_dir.exists():
        shutil.rmtree(target_dir, onerror=_on_rm_error)
    db_path = build_vector_store(
        docs=docs,
        domain=DOMAIN,
        persist_dir=str(PERSIST_DIR),
        chunk_size=800,
        chunk_overlap=50,
    )
    print(f"Vector store built at: {db_path}")


if __name__ == "__main__":
    main()
