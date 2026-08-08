"""
Downloads public UN / humanitarian documents and chunks them for RAG.
All sources are publicly available — no auth needed.
Run via: python scripts/build_vectorstore.py
"""
import httpx
from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

DOCS_DIR = Path(__file__).parent.parent.parent / "data" / "un_docs"

# Free, publicly accessible UN + humanitarian PDFs
UN_SOURCES = [
    {
        "url": "https://sdgs.un.org/sites/default/files/2021-10/The%20Sustainable%20Development%20Goals%20Report%202021.pdf",
        "name": "sdg_report_2021.pdf",
        "tags": ["SDG", "development", "global goals"],
    },
    {
        "url": "https://www.unhcr.org/globaltrends/globaltrends2022/assets/pdf/GCR_English.pdf",
        "name": "unhcr_global_compact_refugees.pdf",
        "tags": ["refugees", "displacement", "UNHCR"],
    },
    {
        "url": "https://www.unocha.org/sites/unocha/files/Global-Humanitarian-Overview-2024.pdf",
        "name": "ocha_humanitarian_overview_2024.pdf",
        "tags": ["humanitarian", "crisis", "OCHA"],
    },
]

# Fallback: minimal inline text if PDFs fail to download
FALLBACK_TEXTS = [
    """SDG 1 - No Poverty: End poverty in all its forms everywhere.
SDG 2 - Zero Hunger: End hunger, achieve food security and improved nutrition.
SDG 3 - Good Health: Ensure healthy lives and promote well-being for all.
SDG 6 - Clean Water: Ensure access to clean water and sanitation.
SDG 10 - Reduced Inequalities: Reduce inequality within and among countries.
SDG 11 - Sustainable Cities: Make cities inclusive, safe, resilient and sustainable.
SDG 13 - Climate Action: Take urgent action to combat climate change and its impacts.
SDG 16 - Peace and Justice: Promote peaceful and inclusive societies for sustainable development.
SDG 17 - Partnerships: Strengthen global partnerships for sustainable development.""",

    """UNHCR defines a refugee as someone who has been forced to flee their country because of 
persecution, war or violence. Key interventions include: emergency shelter, food assistance, 
healthcare, education, and legal protection. Solutions framework includes voluntary repatriation,
local integration, and resettlement to third countries.""",

    """Humanitarian response principles: humanity, neutrality, impartiality and independence.
OCHA coordinates humanitarian action to ensure crisis-affected people receive assistance.
Cluster system coordinates sectors: Food Security (WFP/FAO), Health (WHO), Shelter (UNHCR),
Water Sanitation (UNICEF), Protection (UNHCR), Nutrition (UNICEF), Education (UNICEF/Save the Children).
Humanitarian Response Plans are developed for countries in crisis.""",

    """Climate change impacts: sea level rise threatens coastal communities, extreme weather events
increase in frequency and severity, droughts cause crop failures and food insecurity, flooding
displaces populations. Paris Agreement targets limiting warming to 1.5°C. Adaptation strategies
include early warning systems, climate-resilient agriculture, and managed retreat from high-risk areas.""",

    """Disease outbreak response: WHO leads international health emergency response under IHR 2005.
Key interventions: surveillance and case detection, contact tracing, vaccination campaigns,
treatment protocols, community engagement. GOARN provides rapid response teams. 
Health system strengthening is critical for epidemic preparedness.""",
]


def download_docs() -> None:
    """Download UN PDFs to data/un_docs/. Skip if already present."""
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    for doc in UN_SOURCES:
        dest = DOCS_DIR / doc["name"]
        if dest.exists():
            print(f"[LOADER] Already exists: {doc['name']}")
            continue
        print(f"[LOADER] Downloading {doc['name']}...")
        try:
            r = httpx.get(doc["url"], follow_redirects=True, timeout=30)
            if r.status_code == 200:
                dest.write_bytes(r.content)
                print(f"[LOADER] ✅ Downloaded {doc['name']} ({len(r.content)//1024}kb)")
            else:
                print(f"[LOADER] ⚠️ HTTP {r.status_code} for {doc['name']} — will use fallback text")
        except Exception as e:
            print(f"[LOADER] ⚠️ Failed {doc['name']}: {e} — will use fallback text")


def load_chunks() -> list:
    """Load and chunk all available docs. Falls back to inline text if no PDFs."""
    from langchain.schema import Document

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=600,
        chunk_overlap=80,
        separators=["\n\n", "\n", ". ", " "],
    )

    chunks = []

    # Try PDF files first
    for doc in UN_SOURCES:
        pdf_path = DOCS_DIR / doc["name"]
        if pdf_path.exists():
            try:
                loader = PyPDFLoader(str(pdf_path))
                pages = loader.load()
                splits = splitter.split_documents(pages)
                # Tag each chunk with metadata
                for s in splits:
                    s.metadata["source"] = doc["name"]
                    s.metadata["tags"] = ", ".join(doc["tags"])
                chunks.extend(splits)
                print(f"[LOADER] ✅ Chunked {doc['name']}: {len(splits)} chunks")
            except Exception as e:
                print(f"[LOADER] ⚠️ Could not parse {doc['name']}: {e}")

    # Always add fallback texts (they're high quality and always available)
    for i, text in enumerate(FALLBACK_TEXTS):
        splits = splitter.create_documents(
            [text],
            metadatas=[{"source": f"un_knowledge_base_{i}", "tags": "UN,SDG,humanitarian"}]
        )
        chunks.extend(splits)

    print(f"[LOADER] 📚 Total chunks ready for embedding: {len(chunks)}")
    return chunks