import argparse
import os
import sys
from pathlib import Path

# Allow importing project modules
ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT))

from config import DASHSCOPE_API_KEY
from modules.rag_engine import get_retrieved_context


def run_query(query: str, difficulty: str | None, topic: str | None, k: int, domain: str, persist_dir: str) -> None:
    if DASHSCOPE_API_KEY:
        os.environ["DASHSCOPE_API_KEY"] = DASHSCOPE_API_KEY

    filt = {}
    if difficulty:
        filt["difficulty"] = difficulty
    if topic:
        filt["topic"] = topic

    ctx = get_retrieved_context(
        query=query,
        domain=domain,
        k=k,
        persist_dir=persist_dir,
        search_filter=filt or None,
    )

    print("=== Query ===")
    print(query)
    print("=== Filter ===")
    print(filt or "None")
    print("=== Result ===")
    print(ctx)
    print(f"\nlen: {len(ctx)}")


def main():
    parser = argparse.ArgumentParser(description="Quick RAG retrieval tester")
    parser.add_argument("query", nargs="?", help="your query text")
    parser.add_argument("--difficulty", help="metadata difficulty filter")
    parser.add_argument("--topic", help="metadata topic filter")
    parser.add_argument("--k", type=int, default=5, help="top-k to retrieve")
    parser.add_argument("--domain", default="cs", help="domain name (vector dir)")
    parser.add_argument("--persist-dir", default=str(ROOT / "vector_db"), help="vector db root dir")
    args = parser.parse_args()

    # If query not provided, enter interactive mode for terminal input
    if not args.query:
        print("Interactive mode: leave blank to skip optional fields.")
        query = input("Query: ").strip()
        difficulty = input("Difficulty (optional): ").strip() or None
        topic = input("Topic (optional): ").strip() or None
        try:
            k = int(input(f"k (default {args.k}): ").strip() or args.k)
        except ValueError:
            k = args.k
        domain = input(f"Domain (default {args.domain}): ").strip() or args.domain
        persist_dir = input(f"Persist dir (default {args.persist_dir}): ").strip() or args.persist_dir
    else:
        query = args.query
        difficulty = args.difficulty
        topic = args.topic
        k = args.k
        domain = args.domain
        persist_dir = args.persist_dir

    run_query(query, difficulty, topic, k, domain, persist_dir)


if __name__ == "__main__":
    main()
