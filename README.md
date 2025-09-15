### 🧠 Synthetic Mind (Consciousness Emulator)

A revolutionary, brain-inspired Python framework that fuses attention, memory, reasoning, reflection, and goal-driven behavior into a single coherent system — designed to self-explain its thinking, adapt over time, and hold deep conversations across philosophy, science, coding, and more.

Built to push beyond the Turing Test toward the Meta-Turing Test: a system that can reason about itself, describe its own cognitive operations, and evolve its behavior. Licensed under the MIT License by AmirHosseinRasti.

---

### ✨ Highlights

- Dual-mode reasoning: fast heuristics + symbolic rule engine
- Working and Long-Term Memory with vector search (FAISS + sentence-transformers)
- Persistent LTM to disk (Parquet episodes + FAISS index + embeddings)
- Self-model with uncertainty and contradiction tracking
- Attention spotlight merges short-term context with retrieved episodes
- Meta-Turing probes: "Why did you say that?", "What don’t you know?", CoT summaries
- Tool-use (goal-gated): web search and safe code execution sandbox
- Streamlit UI for immersive, long-form dialogue and transparent traces

---

### 🚀 Quick Start

1) Create a virtual environment and install dependencies:
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

2) Run CLI:
```bash
python main.py --prompt "Explain your reasoning, then answer: 12*7?" --trace
```

3) Launch Streamlit App:
```bash
streamlit run streamlit_app.py
```

---

### 🧩 Architecture Overview

- Sensory Layer (Input Normalization)
  - Normalizes text inputs into internal experience objects with timestamps and saliency.

- Working Memory (Short-Term Context)
  - Limited-capacity buffer with recency decay + saliency reinforcement.
  - Tracks "what’s happening right now" to support ongoing tasks.

- Long-Term Memory (Knowledge + Experience)
  - Hybrid vector + tags store.
  - FAISS index + sentence-transformers embeddings.
  - Episodes persisted as Parquet; embeddings as NPY; FAISS index on disk.
  - Symbolic tags for targeted retrieval (e.g., "philosophy", "math", "ethics").

- Attention Controller (Spotlight)
  - Selects a small set of the most relevant items from WM and retrieved LTM.
  - Biases by saliency, recency, and retrieval scores.

- Reasoning Engine (Dual-System)
  - Symbolic rule engine for identity, uncertainty, “why” queries, and arithmetic.
  - Heuristic generator for mixed-mode reasoning with retrieval tails.

- Self-Model (Reflection Layer)
  - Tracks intent, uncertainty, and potential contradictions.
  - Exposes snapshots for tracing and probes.

- Goal + Emotion Module (Utility-Driven)
  - Curiosity and coherence drives.
  - Used to gate tools and reasoning strategies.

- Action Layer (Output Generation)
  - Composes fuller answers: base answer + rationale + confidence/advice + follow-ups.
  - Tool-use actions: web search and safe code execution.

---

### 🗂️ Key Files

- `main.py` — CLI entrypoint.
- `streamlit_app.py` — Streamlit conversation UI + probes + trace panel.
- `synthetic_mind/core.py` — Orchestrator tying all modules together; persistence hooks.
- `synthetic_mind/types.py` — Core data structures: Experience, Thought, Action.
- `synthetic_mind/memory/working.py` — Recency/saliency WM with reinforcement.
- `synthetic_mind/memory/long_term.py` — Vector-store LTM with FAISS + Parquet persistence.
- `synthetic_mind/attention/controller.py` — WM+LTM spotlight selection.
- `synthetic_mind/reasoning/engine.py` — Rules + heuristic reasoning.
- `synthetic_mind/self_model/model.py` — Uncertainty + contradiction tracking.
- `synthetic_mind/action/effectors.py` — Answer composer + web search + safe code exec.

---

### 🧪 CLI Examples

- Introspective arithmetic:
```bash
python main.py --prompt "Explain your own reasoning then compute 12*7." --trace
```
- Philosophy chat starter:
```bash
python main.py --prompt "What is consciousness? Examine arguments for and against functionalism." --trace
```
- Open-ended exploration:
```bash
python main.py
# Enter interactive mode. Type 'exit' to quit.
```

---

### 🖥️ Streamlit UI

- Chat with the mind; see real-time trace JSON.
- Sidebar features Meta-Turing probes:
  - Why did you say that?
  - What don’t you know?
  - Summarize chain-of-thought.
- Future toggles (planned): enable/disable tools, select embedding model, persistence controls.

Run:
```bash
streamlit run streamlit_app.py
```

---

### 🧠 Cognitive Loop (High-Level)

1) Ingest input → Experience object with saliency initialization
2) Self-model updates intent + uncertainty from observation quality
3) Attention selects top WM items and augments from LTM retrieval
4) Reasoning runs: apply rules, otherwise mixed-mode heuristic with retrieval tails
5) Action composes fuller answer with rationale + confidence + follow-up cues
6) Writeback: reinforce WM items, record episode to LTM with tags, persist
7) Meta: produce trace for inspection and probes

---

### 🧮 Reasoning Modes

- Symbolic Rules:
  - Identity/purpose answers
  - “Why did you …” explanations
  - Uncertainty acknowledgements
  - Arithmetic patterns (e.g., `a op b`)

- Heuristic Proposal:
  - Consolidates spotlight context + retrieved summaries
  - Generates clear next steps and optional clarifying questions

---

### 🧭 Self-Model and Introspection

- Uncertainty is updated per input (questions raise it; specifics lower it).
- Contradiction detection flags mixed affirmations/negations in context.
- Probes:
  - `why_did_you_say()` — returns last rationale.
  - `what_dont_you_know()` — uncertainty-aware gap identification.
  - `summarize_chain_of_thought()` — compact narrative of focus and rationale.

---

### 💾 Persistence

- Episodes → `storage/episodes.parquet`
- Embeddings → `storage/embeddings.npy`
- FAISS Index → `storage/index.faiss`
- Tags Index → `storage/tags_index.npy`

On startup, the orchestrator loads persisted memory if present; after each step, it saves updated structures.

---

### 🛠️ Tools (Goal-Gated)

- Web Search (DuckDuckGo HTML):
  - Fetches a snippet to seed further reasoning.
  - Timeouts and errors are handled gracefully.

- Safe Code Exec:
  - AST-validated, limited builtins environment
  - Result must be assigned to `result` variable

Tool use can be extended to calculators, web APIs, or local knowledge bases.

---

### 🧵 Multi-Turn CoT and Planning (Roadmap)

- Rolling chain-of-thought summaries across turns to compress long dialogues
- Plan refinement loop: propose plan → execute → evaluate → revise
- Attention-guided plan checkpointing based on uncertainty and utility

---

### 🔧 Configuration

- `MindConfig` in `synthetic_mind/core.py`:
  - `working_memory_capacity`
  - `storage_dir`

- LTM embedder model can be changed via constructor parameter.

---

### ⚖️ Ethics and Alignment

- Utility goals (coherence, curiosity) guide attention and tool-use.
- Explainability-first design: rationale is surfaced with each answer.
- Future work: constraint solvers for alignment rules and safe boundaries.

---

### 🔭 Extending the System

- Add new tools by extending `ActionExecutor` and adding goal checks
- Add new rules to `RuleEngine` for domain-specific behaviors
- Swap or fine-tune embedding models for specialized memory retrieval
- Persist to external DBs (SQLite/Postgres) with row-level encryption

---

### 🧪 Testing Ideas

- Probe uncertainty changes with vague vs. specific prompts
- Insert contradictory statements and observe contradiction tracking
- Verify arithmetic rules and mixed-mode reasoning
- Stress-test persistence by restarting sessions and resuming context

---

### ❓ FAQ

- Q: Does it truly understand like a human?
  - A: It emulates aspects of cognition (memory, attention, reasoning, reflection). Real consciousness remains a philosophical and scientific question.

- Q: Is it safe to execute code?
  - A: The sandbox is minimal and restricted; nevertheless, treat it as untrusted and run in a controlled environment.

- Q: Can I add images/audio?
  - A: The architecture is designed for multimodal extension; add new sensory adapters and embed accordingly.

---

### 📜 License

MIT License © 2025 AmirHosseinRasti

See `LICENSE` for full terms.

---

### 🗺️ Roadmap

- [x] Mini-mind pipeline
- [x] Vector LTM + tags + persistence
- [x] Rules + heuristics
- [x] Self-model with uncertainty + contradictions
- [x] Streamlit UI + probes
- [ ] Multi-turn planning loop and plan memory
- [ ] Richer tool-use (calculators, Wikipedia, code-LLM bridge)
- [ ] Advanced alignment constraints and safety checks
- [ ] Multimodal inputs (vision/audio) and embodiment API

---

### ❤️ Acknowledgments

This project stands on the shoulders of open-source ecosystems: PyTorch, Sentence-Transformers, FAISS, Streamlit, and the Python community.

---

### 🧨 Notes

- First run downloads embedding model; allow time.
- FAISS is optional; fallback uses NumPy similarity.
- Windows symlink warnings can be ignored or fixed by enabling Developer Mode.

---

### 🔄 Example Session Walkthrough

1) Prompt: "What is consciousness? Compare physicalism vs dualism and reflect on uncertainty."
2) WM ingests observation; self-model raises uncertainty due to breadth.
3) Attention retrieves prior philosophical turns; spotlight forms a compact context.
4) Reasoning combines rules (identity) and heuristic synthesis with retrieval.
5) Action composes a full answer: arguments on both sides, sources to explore, uncertainty note, follow-up invitation.
6) LTM records the episode; persistence saves to disk.
7) Probes can immediately explain rationale and summarize focus.

---

Happy hacking — and welcome to your Synthetic Mind. 🧠🚀
