"""
app/core/rag/result_fusion.py
----------------------------
Reusable ResultFusion service to merge adjacent document chunks, remove duplicates,
normalize similarity scores, and sort candidates.
"""

import math
from typing import List, Dict, Any, Optional
from app.core.config import settings


class ResultFusion:
    """
    Handles chunk de-duplication, text-overlap merging, and similarity score normalization.
    """

    def fuse_results(
        self,
        results: List[Dict[str, Any]],
        score_normalization: Optional[str] = None,
        overlap_threshold: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Main orchestration entrypoint to de-duplicate, merge, normalize, and sort retrieval results.
        """
        if not results:
            return []

        # 1. Content De-duplication (exact matching text)
        deduplicated: List[Dict[str, Any]] = []
        seen_texts = set()
        for res in results:
            text = res.get("content", "").strip()
            if not text:
                continue
            if text in seen_texts:
                continue
            seen_texts.add(text)
            deduplicated.append(res.copy())

        # 2. Adjacent Chunk Merging
        fused: List[Dict[str, Any]] = []
        for cand in deduplicated:
            # Try to merge with an existing chunk in our fused list
            if not self._merge_adjacent(fused, cand, overlap_threshold):
                fused.append(cand)

        # 3. Score Normalization
        norm_method = score_normalization or settings.RAG_SCORE_NORMALIZATION
        normalized = self.normalize_scores(fused, norm_method)

        # 4. Final sort descending by score
        return sorted(normalized, key=lambda x: x.get("score", 0.0), reverse=True)

    def _merge_adjacent(
        self,
        fused_list: List[Dict[str, Any]],
        candidate: Dict[str, Any],
        overlap_threshold: int,
    ) -> bool:
        """
        Searches fused list for sequential adjacent chunk of same document/dataset and merges.
        """
        cand_meta = candidate.get("metadata", {})
        cand_doc = (
            cand_meta.get("document_id")
            or cand_meta.get("source_file")
            or cand_meta.get("record_id")
        )
        cand_ds = cand_meta.get("dataset_id")
        cand_idx = cand_meta.get("chunk_index")

        if cand_doc is None or cand_idx is None:
            return False

        for existing in fused_list:
            exist_meta = existing.get("metadata", {})
            exist_doc = (
                exist_meta.get("document_id")
                or exist_meta.get("source_file")
                or exist_meta.get("record_id")
            )
            exist_ds = exist_meta.get("dataset_id")
            exist_idx = exist_meta.get("chunk_index")

            if exist_doc == cand_doc and exist_ds == cand_ds and exist_idx is not None:
                # Check sequential adjacency
                if abs(exist_idx - cand_idx) == 1:
                    # Merge contents
                    if exist_idx < cand_idx:
                        existing["content"] = self._merge_text_overlap(
                            existing["content"], candidate["content"], overlap_threshold
                        )
                        existing["metadata"]["chunk_index"] = cand_idx
                    else:
                        existing["content"] = self._merge_text_overlap(
                            candidate["content"], existing["content"], overlap_threshold
                        )
                        existing["metadata"]["chunk_index"] = exist_idx

                    # Consolidate scoring
                    existing["score"] = max(
                        existing.get("score", 0.0), candidate.get("score", 0.0)
                    )
                    return True
        return False

    def _merge_text_overlap(self, text1: str, text2: str, threshold: int) -> str:
        """
        Finds overlapping suffix/prefix strings and returns combined content.
        """
        max_overlap = min(len(text1), len(text2))
        for i in range(max_overlap, threshold - 1, -1):
            if text1.endswith(text2[:i]):
                return text1 + text2[i:]
        return text1 + "\n" + text2

    def normalize_scores(
        self, results: List[Dict[str, Any]], method: str
    ) -> List[Dict[str, Any]]:
        """
        Normalizes scores using Min-Max, Z-Score, or Logistic functions.
        """
        if not results or method == "none" or method is None:
            return results

        scores = [r.get("score", 0.0) for r in results]

        if method == "min-max":
            min_s = min(scores)
            max_s = max(scores)
            denom = max_s - min_s
            for r in results:
                r["score"] = (r["score"] - min_s) / denom if denom > 0.0 else 1.0

        elif method == "z-score":
            n = len(scores)
            if n > 1:
                mean = sum(scores) / n
                variance = sum((x - mean) ** 2 for x in scores) / (n - 1)
                std = math.sqrt(variance)
                for r in results:
                    r["score"] = (r["score"] - mean) / std if std > 0.0 else 0.0
            else:
                for r in results:
                    r["score"] = 1.0

        elif method == "logistic":
            # Sigmoid activation: 1 / (1 + exp(-x))
            for r in results:
                # Shift and scale if score is usually [0, 1] cosine similarity
                r["score"] = 1.0 / (1.0 + math.exp(-r["score"]))

        return results
