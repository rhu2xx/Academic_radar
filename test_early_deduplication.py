"""
Test to demonstrate cost savings from early duplicate removal.
"""
from src.core.models import PaperMetadata
from src.tools.paper_tracker import PaperTracker
from datetime import datetime


def test_early_deduplication():
    """Demonstrate cost savings from removing duplicates before LLM analysis."""
    print("💰 Testing Early Duplicate Removal - Cost Optimization")
    print("=" * 80)
    
    tracker = PaperTracker()
    
    # Simulate papers with duplicates (same title, different IDs/URLs)
    papers = [
        PaperMetadata(
            title="Attention Is All You Need",
            authors=["Vaswani et al."],
            abstract="Transformer architecture...",
            publication_date=datetime(2017, 6, 12),
            openalex_id="https://openalex.org/W2964118967",
            url="https://arxiv.org/abs/1706.03762",
            primary_field="Computer Science",
            cited_by_count=50000
        ),
        PaperMetadata(
            title="BERT: Pre-training Transformers",
            authors=["Devlin et al."],
            abstract="BERT model...",
            publication_date=datetime(2018, 10, 11),
            openalex_id="https://openalex.org/W2950234567",
            url="https://arxiv.org/abs/1810.04805",
            primary_field="Computer Science",
            cited_by_count=40000
        ),
        PaperMetadata(
            title="Attention Is All You Need!",  # Duplicate with punctuation
            authors=["Vaswani et al."],
            abstract="Transformer architecture...",
            publication_date=datetime(2017, 6, 12),
            openalex_id="https://openalex.org/DIFFERENT_ID",  # Different ID!
            url="https://doi.org/10.5555/3295222.3295349",  # Different URL!
            primary_field="Computer Science",
            cited_by_count=50000
        ),
        PaperMetadata(
            title="GPT-3: Language Models",
            authors=["Brown et al."],
            abstract="GPT-3 model...",
            publication_date=datetime(2020, 5, 28),
            openalex_id="https://openalex.org/W3032934567",
            url="https://arxiv.org/abs/2005.14165",
            primary_field="Computer Science",
            cited_by_count=30000
        ),
        PaperMetadata(
            title="BERT: Pre-training Transformers",  # Exact duplicate
            authors=["Devlin et al."],
            abstract="BERT model...",
            publication_date=datetime(2018, 10, 11),
            openalex_id="https://openalex.org/ANOTHER_ID",  # Different ID!
            url="https://doi.org/10.18653/v1/N19-1423",  # Different URL!
            primary_field="Computer Science",
            cited_by_count=40000
        ),
    ]
    
    print(f"\n📊 Input: {len(papers)} papers to analyze")
    print("\nPapers:")
    for i, paper in enumerate(papers, 1):
        print(f"  {i}. {paper.title}")
        print(f"     ID: {paper.openalex_id}")
        print(f"     URL: {paper.url}")
    
    # Deduplicate by title
    print("\n🔍 Deduplicating by normalized title...")
    seen_titles = set()
    unique_papers = []
    duplicates = []
    
    for paper in papers:
        normalized = tracker.normalize_title(paper.title)
        if normalized in seen_titles:
            duplicates.append(paper)
        else:
            seen_titles.add(normalized)
            unique_papers.append(paper)
    
    print(f"\n✅ Result: {len(unique_papers)} unique papers")
    print(f"🚫 Removed: {len(duplicates)} duplicates")
    
    print("\nUnique papers:")
    for i, paper in enumerate(unique_papers, 1):
        print(f"  {i}. {paper.title}")
    
    print("\nDuplicates removed:")
    for i, paper in enumerate(duplicates, 1):
        print(f"  {i}. {paper.title}")
        print(f"     (Different ID/URL but same normalized title)")
    
    # Calculate cost savings
    print("\n" + "=" * 80)
    print("💰 COST ANALYSIS")
    print("=" * 80)
    
    llm_cost_per_paper = 0.01  # Approximate cost per paper analysis
    
    print(f"\n❌ BEFORE (Publisher-stage deduplication):")
    print(f"   • Papers analyzed by LLM: {len(papers)}")
    print(f"   • Cost: ${len(papers) * llm_cost_per_paper:.2f}")
    print(f"   • Duplicates removed AFTER analysis: {len(duplicates)}")
    print(f"   • Wasted cost: ${len(duplicates) * llm_cost_per_paper:.2f} 💸")
    
    print(f"\n✅ AFTER (Analyst-stage deduplication):")
    print(f"   • Papers analyzed by LLM: {len(unique_papers)}")
    print(f"   • Cost: ${len(unique_papers) * llm_cost_per_paper:.2f}")
    print(f"   • Duplicates removed BEFORE analysis: {len(duplicates)}")
    print(f"   • Saved cost: ${len(duplicates) * llm_cost_per_paper:.2f} 💰")
    
    savings_pct = (len(duplicates) / len(papers)) * 100
    print(f"\n📈 Improvement: {savings_pct:.1f}% cost reduction on this batch")
    
    print("\n" + "=" * 80)
    print("🎉 Early deduplication prevents wasted LLM tokens!")
    print("=" * 80)
    
    # Show the normalized titles that caught duplicates
    print("\n🔬 Title Normalization Examples:")
    test_titles = [
        "Attention Is All You Need",
        "Attention Is All You Need!",
        "BERT: Pre-training Transformers",
    ]
    
    for title in test_titles:
        normalized = tracker.normalize_title(title)
        print(f"  '{title}'")
        print(f"  → '{normalized}'")
        print()


if __name__ == "__main__":
    test_early_deduplication()
