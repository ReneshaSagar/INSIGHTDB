# InsightDB: AI-Powered Relational Data Intelligence
> **A to Z Technical Documentation | Hackfest 2.0 Pitch**

---

## 🚀 The Vision
InsightDB is an autonomous data intelligence platform designed to bridge the gap between **raw departmental data** and **strategic business understanding**. In an era where data is abundant but clarity is scarce, InsightDB provides an immediate, AI-driven audit of relational datasets, calculating "Trust Scores" and generating professional-grade documentation in seconds.

---

## 🛠 The Technical Stack
- **Backend Core**: Python (Flask)
- **Data Engineering**: Pandas & NumPy (High-performance analytical engines)
- **Artificial Intelligence**: Google Vertex AI (`gemini-2.5-flash`)
- **Security & Infrastructure**: Google Cloud Platform (GCP) with **OAuth2 Service Account Authentication**
- **Frontend UI/UX**: HTML5, Vanilla CSS3 (Custom Design System), JavaScript (ES6+)

---

## 🏗 The Architectural Workflow (A to Z)

### 1. Unified Data Ingestion (`DataLoader`)
The journey begins at the **Upload Zone**. Our ingestion engine handles multi-file CSV uploads, preserving relational integrity.
- **Dynamic Loading**: Uses `glob` and `pandas` to load heterogeneous datasets into memory.
- **Session Management**: Supports both "Fresh Starts" and "Appending Data" to existing business contexts.

### 2. Intelligent Schema Reconstruction (`SchemaAnalyzer`)
Once loaded, the system performs a **Context-Aware Audit** of the data structure.
- **Semantic Classification**: Beyond simple data types (int/string), the analyzer identifies **Identifiers, Timestamps, Categorical, and Numeric** metrics using heuristic pattern matching.
- **Relational Inference**: Automatically detects **Potential Primary Keys** (uniqueness constraints) and **Foreign Key Relationships** (heuristic substring matching vs. table names).

### 3. The Trust Engine (`QualityEngine`)
This is the scientific heart of InsightDB. Every table is assigned a **Trust Score** (0-100) based on a weighted multi-dimensional analysis:
- **Completeness (20%)**: Measures null density across the dataset.
- **Identifier Health (25%)**: Evaluates the uniqueness and reliability of join keys.
- **Referential Integrity (25%)**: Calculates "Orphan Rates" by checking FKs against detected parent tables.
- **Numeric Sanity (15%)**: Performs Z-score outlier detection and "Negative Value" audits on unsigned metrics.
- **Freshness (15%)**: Measures data latency against the global dataset timeline.

### 4. Generative Documentation Layer (`AIService`)
We leverage **Vertex AI** to transform raw metadata into business narratives.
- **Project Overview**: Generates a high-level title, description, and "Business Value" assessment.
- **Full Documentation Report**: A comprehensive long-form report explaining the **Architecture & Business Logic** of the entire dataset.
- **Contextual Awareness**: The AI is fed the schema, trust metrics, and table relationships to ensure its insights are grounded in reality, not hallucinations.

### 5. AI Data Assistant (Interactive Chat)
A floating assistant provides a **Natural Language Interface** to the data.
- **Context Injection**: Every question asked is bundled with the **entire project schema and quality metrics**, allowing the AI to answer complex questions like *"Which table covers customer demographics?"* or *"How reliable is our order history data?"*

---

## 🎨 Premium UI/UX Experience
- **Cinematic Entrance**: A full-screen video splash screen sets a premium tone before entering the dashboard.
- **Glassmorphism Design**: Use of backdrop filters, subtle gradients, and a clean Inter-based typography.
- **Interactive Sidebar**: A collapsible navigation system that stays out of the way during deep data dives.
- **Real-time Status**: A system status indicator tracking the health of the AI Core and backend connectivity.

---

## 🔐 Security & Reliability
InsightDB is built for the enterprise:
- **Strict OAuth2**: We enforced **Google Service Account** authentication for Vertex AI, moving away from vulnerable API Keys.
- **GCP Native**: Integrated directly with Google Cloud Project `insightdb-488114` for scalable AI inference via the `us-central1` endpoint.

---

## 🎯 Impact
InsightDB transforms a "folder of CSVs" into a **documented, audited, and queryable business asset**. It empowers data architects to identify risks and business leaders to trust their data before making critical decisions.

---
*Created with ❤️ for Hackfest 2.0*
