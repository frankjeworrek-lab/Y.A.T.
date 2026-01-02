
from pathlib import Path
from typing import List, Dict, Optional
import re

class DocsManager:
    def __init__(self, docs_path: str = "docs"):
        # Resolve docs path relative to project root
        self.base_dir = Path(__file__).parent.parent
        self.docs_dir = self.base_dir / docs_path
        self.documents: List[Dict] = []
        self._load_docs()

    def _load_docs(self):
        """Load all markdown files from docs directory"""
        self.documents = []
        if not self.docs_dir.exists():
            print(f"Warning: Docs directory '{self.docs_dir}' not found.")
            return

        # Sort files: Quick Start first, then numbered, then others
        files = sorted(list(self.docs_dir.glob("*.md")))
        
        for file_path in files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    
                    # Extract title from first H1
                    title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
                    title = title_match.group(1) if title_match else file_path.stem.replace('-', ' ').title()
                    
                    self.documents.append({
                        "filename": file_path.name,
                        "title": title,
                        "content": content,
                        "path": str(file_path),
                        "lines": content.splitlines()
                    })
            except Exception as e:
                print(f"Error reading {file_path}: {e}")

    def get_all_docs(self) -> List[Dict]:
        """Return list of all loaded documents (metadata only)"""
        return [{"filename": d["filename"], "title": d["title"]} for d in self.documents]

    def get_doc_content(self, filename: str) -> Optional[str]:
        """Get full content of a specific document"""
        for doc in self.documents:
            if doc["filename"] == filename:
                return doc["content"]
        return None

    def search(self, query: str) -> List[Dict]:
        """Search docs for query string"""
        if not query or len(query.strip()) < 2:
            return []

        results = []
        query_lower = query.lower()
        keywords = query_lower.split()

        for doc in self.documents:
            score = 0
            matches = []
            
            # Title match
            if query_lower in doc["title"].lower():
                score += 10
            
            # Content match
            for i, line in enumerate(doc["lines"]):
                line_lower = line.lower()
                found_keywords = [k for k in keywords if k in line_lower]
                
                if found_keywords:
                    # Highlight logic (simple html bold)
                    # We won't modify content here, just return the snippet
                    matches.append({
                        "line": i + 1,
                        "content": line.strip()
                    })
                    score += len(found_keywords)
            
            if score > 0:
                results.append({
                    "filename": doc["filename"],
                    "title": doc["title"],
                    "score": score,
                    "matches": matches[:3], # Top 3 snippets
                    "match_count": len(matches)
                })

        # Sort by score
        results.sort(key=lambda x: x["score"], reverse=True)
        return results
