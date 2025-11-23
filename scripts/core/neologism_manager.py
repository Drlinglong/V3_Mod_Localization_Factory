import json
import os
import uuid
import logging
from typing import List, Dict, Optional, Literal
from pydantic import BaseModel
from scripts.app_settings import PROJECT_ROOT
from scripts.core.api_handler import get_handler
from scripts.core.neologism_miner import NeologismMiner
from scripts.core.glossary_manager import glossary_manager

CACHE_FILE = os.path.join(PROJECT_ROOT, "data", "cache", "neologism_candidates.json")

class Candidate(BaseModel):
    id: str
    original: str
    context_snippets: List[str]
    suggestion: str
    reasoning: str
    status: Literal["pending", "approved", "ignored"] = "pending"
    source_file: Optional[str] = None

class NeologismManager:
    def __init__(self):
        self.candidates: List[Candidate] = []
        self.load_candidates()
        self.logger = logging.getLogger(__name__)

    def load_candidates(self):
        if os.path.exists(CACHE_FILE):
            try:
                with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.candidates = [Candidate(**item) for item in data]
            except Exception as e:
                self.logger.error(f"Failed to load neologism candidates: {e}")
                self.candidates = []
        else:
            self.candidates = []

    def save_candidates(self):
        os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
        try:
            with open(CACHE_FILE, 'w', encoding='utf-8') as f:
                json.dump([c.dict() for c in self.candidates], f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save neologism candidates: {e}")

    def get_pending_candidates(self) -> List[Dict]:
        return [c.dict() for c in self.candidates if c.status == "pending"]

    def approve_candidate(self, candidate_id: str, final_translation: str, glossary_id: int) -> bool:
        candidate = next((c for c in self.candidates if c.id == candidate_id), None)
        if not candidate:
            return False
        
        # Add to glossary
        entry = {
            "source": candidate.original,
            "translations": {"zh-CN": final_translation}, # Assuming zh-CN for now, should be configurable
            "notes": f"Auto-mined. Reasoning: {candidate.reasoning}",
            "metadata": {"source_file": candidate.source_file}
        }
        
        # We need to construct the payload for glossary_manager.add_entry
        # glossary_manager.add_entry expects storage format
        new_entry_id = str(uuid.uuid4())
        storage_entry = {
            "id": new_entry_id,
            "translations": {"en": candidate.original, "zh-CN": final_translation}, # Assuming source is EN
            "raw_metadata": {"remarks": entry["notes"], "source_file": candidate.source_file},
            "variants": {},
            "abbreviations": {}
        }
        
        if glossary_manager.add_entry(glossary_id, storage_entry):
            candidate.status = "approved"
            self.save_candidates()
            return True
        return False

    def reject_candidate(self, candidate_id: str) -> bool:
        candidate = next((c for c in self.candidates if c.id == candidate_id), None)
        if candidate:
            candidate.status = "ignored"
            self.save_candidates()
            return True
        return False
    
    def update_candidate_suggestion(self, candidate_id: str, suggestion: str) -> bool:
        candidate = next((c for c in self.candidates if c.id == candidate_id), None)
        if candidate:
            candidate.suggestion = suggestion
            self.save_candidates()
            return True
        return False

    def run_mining_workflow(self, file_paths: List[str], api_provider: str, source_lang: str = "en", target_lang: str = "zh"):
        """
        Main workflow:
        1. Initialize Miner with API provider.
        2. Iterate files, extract terms (Stage A).
        3. Deduplicate terms.
        4. For each term, find context (Stage B preparation).
        5. Call LLM for analysis (Stage B).
        6. Save candidates.
        """
        handler = get_handler(api_provider)
        miner = NeologismMiner(handler)
        
        all_terms = set()
        term_sources = {} # term -> source_file

        # Stage A: Mining
        for file_path in file_paths:
            try:
                with open(file_path, 'r', encoding='utf-8-sig') as f:
                    content = f.read()
                
                # Simple chunking if content is too large
                # For now, let's assume files are manageable or we chunk by lines
                # Better to chunk by paragraphs or max chars
                chunk_size = 4000
                chunks = [content[i:i+chunk_size] for i in range(0, len(content), chunk_size)]
                
                for chunk in chunks:
                    terms = miner.extract_terms(chunk)
                    for term in terms:
                        if term not in all_terms:
                            all_terms.add(term)
                            term_sources[term] = file_path
            except Exception as e:
                self.logger.error(f"Error reading file {file_path}: {e}")

        # Filter out terms already in glossary or ignored/approved
        existing_terms = set()
        # Check glossary (this is expensive if glossary is huge, but necessary)
        # For now, let's just check against our own candidates status
        for c in self.candidates:
            if c.status in ["approved", "ignored"]:
                existing_terms.add(c.original)
        
        new_terms = [t for t in all_terms if t not in existing_terms and not any(c.original == t for c in self.candidates)]

        # Stage B: Analysis
        for term in new_terms:
            source_file = term_sources[term]
            context_snippets = self._find_context_snippets(term, source_file)
            
            analysis = self._analyze_term(term, context_snippets, handler, source_lang, target_lang)
            
            candidate = Candidate(
                id=str(uuid.uuid4()),
                original=term,
                context_snippets=context_snippets,
                suggestion=analysis.get("suggestion", ""),
                reasoning=analysis.get("reasoning", ""),
                status="pending",
                source_file=source_file
            )
            self.candidates.append(candidate)
        
        self.save_candidates()
        return len(new_terms)

    def _find_context_snippets(self, term: str, file_path: str, max_snippets: int = 3) -> List[str]:
        snippets = []
        try:
            with open(file_path, 'r', encoding='utf-8-sig') as f:
                lines = f.readlines()
            
            for line in lines:
                if term in line:
                    snippets.append(line.strip())
                    if len(snippets) >= max_snippets:
                        break
        except Exception:
            pass
        return snippets

    def _analyze_term(self, term: str, snippets: List[str], handler, source_lang: str, target_lang: str) -> Dict:
        """
        Ask LLM for suggestion and reasoning.
        """
        context_text = "\n".join([f"- {s}" for s in snippets])
        prompt = f"""
        Term: "{term}"
        
        Context Snippets:
        {context_text}
        
        Task:
        1. Analyze the meaning of the term "{term}" based on the provided context.
        2. Suggest a translation for this term from {source_lang} to {target_lang}.
        3. Provide a brief reasoning for your suggestion.
        
        Output JSON:
        {{
            "suggestion": "...",
            "reasoning": "..."
        }}
        """
        
        try:
            # Use _call_api or generate_content
            # We need to handle the response parsing
            response_text = ""
            if hasattr(handler, "generate_content"):
                 response_text = handler.generate_content(prompt)
            else:
                 response_text = handler._call_api(handler.client, prompt)
            
            # Clean and parse JSON
            cleaned = response_text.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            
            return json.loads(cleaned)
        except Exception as e:
            self.logger.error(f"Analysis failed for term {term}: {e}")
            return {"suggestion": "", "reasoning": "Analysis failed"}

neologism_manager = NeologismManager()
