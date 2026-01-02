import os
import sys
import glob
import re
from pathlib import Path
from typing import List, Dict, Tuple

# ANSI Colors for nicer terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def load_docs(docs_path: str = "docs") -> List[Dict]:
    """Load all markdown files from docs directory"""
    docs = []
    
    # Get absolute path relative to this script
    base_dir = Path(__file__).parent.parent
    target_dir = base_dir / docs_path
    
    if not target_dir.exists():
        print(f"{Colors.RED}Error: Docs directory '{target_dir}' not found.{Colors.ENDC}")
        return []

    for file_path in target_dir.glob("*.md"):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                docs.append({
                    "path": str(file_path.relative_to(base_dir)),
                    "filename": file_path.name,
                    "content": content,
                    "lines": content.splitlines()
                })
        except Exception as e:
            print(f"{Colors.YELLOW}Warning: Could not read {file_path}: {e}{Colors.ENDC}")
            
    return docs

def search_docs(docs: List[Dict], query: str) -> List[Dict]:
    """Search for query in docs"""
    results = []
    
    # Simple case-insensitive search
    query_lower = query.lower()
    keywords = query_lower.split()
    
    for doc in docs:
        matches = []
        
        # Check title/filename relevance
        relevance = 0
        if query_lower in doc["filename"].lower():
            relevance += 10
            
        for i, line in enumerate(doc["lines"]):
            line_lower = line.lower()
            
            # Simple scoring: count how many keywords are in the line
            found_keywords = [k for k in keywords if k in line_lower]
            
            if found_keywords:
                # Highlight logic
                display_line = line
                for k in keywords:
                    # Regex replacement for case-insensitive highlighting
                    display_line = re.sub(
                        f"({re.escape(k)})", 
                        f"{Colors.YELLOW}\\1{Colors.ENDC}", 
                        display_line, 
                        flags=re.IGNORECASE
                    )
                
                matches.append({
                    "line_num": i + 1,
                    "content": display_line,
                    "score": len(found_keywords)
                })
                relevance += len(found_keywords)
        
        if matches:
            # Sort matches by relevance (score)
            matches.sort(key=lambda x: x["score"], reverse=True)
            results.append({
                "doc": doc,
                "matches": matches[:3], # Top 3 matches per file
                "total_matches": len(matches),
                "relevance": relevance
            })
            
    # Sort files by relevance
    results.sort(key=lambda x: x["relevance"], reverse=True)
    return results

def main():
    print(f"{Colors.HEADER}{Colors.BOLD}🔍 KI Chat Pattern - Documentation Search{Colors.ENDC}")
    print(f"{Colors.BLUE}Loading documentation...{Colors.ENDC}")
    
    docs = load_docs()
    print(f"{Colors.GREEN}Loaded {len(docs)} documents.{Colors.ENDC}")
    print(f"Type 'exit' or 'quit' to stop.\n")
    
    while True:
        try:
            query = input(f"{Colors.BOLD}Search Query > {Colors.ENDC}").strip()
            
            if query.lower() in ['exit', 'quit', 'q']:
                print("Goodbye! 👋")
                break
                
            if not query:
                continue
                
            results = search_docs(docs, query)
            
            if not results:
                print(f"{Colors.RED}No results found for '{query}'.{Colors.ENDC}\n")
                continue
                
            print(f"\n{Colors.CYAN}Found matches in {len(results)} files:{Colors.ENDC}\n")
            
            for res in results:
                filename = res["doc"]["filename"]
                print(f"{Colors.BOLD}📄 {filename}{Colors.ENDC} ({res['total_matches']} matches)")
                
                for match in res["matches"]:
                    print(f"  {Colors.BLUE}L{match['line_num']}:{Colors.ENDC} {match['content'].strip()}")
                
                if res['total_matches'] > 3:
                    print(f"  {Colors.BLUE}... and {res['total_matches'] - 3} more{Colors.ENDC}")
                print("") # Empty line
                
        except KeyboardInterrupt:
            print("\nGoodbye! 👋")
            break

if __name__ == "__main__":
    main()
