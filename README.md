# xtudio

**AI-powered software project builder.** A Django monolith that guides software teams from
business requirements to production-ready, tested, and documented code through a structured
multi-agent pipeline.

---

## Platform Phases

| Branch | Phase | Status | Description |
|---|---|---|---|
| `phase-1` | Foundation | ✅ Complete | Users, projects, document upload |
| `phase-2` | Requirements Intelligence | 🔄 Planned | AI requirements extraction |
| `phase-3` | Architecture & Design | 📋 Planned | Architecture agent + approval gate |
| `phase-4` | Sprint Planning | 📋 Planned | Sprint breakdown + approval |
| `phase-5` | Code Generation | 📋 Planned | 4-stage coding pipeline |
| `phase-6` | Studio | 📋 Planned | Web IDE |
| `phase-7` | Memory Management | 📋 Planned | Memory viewer + controls |
| `phase-8` | Pipeline Library | 📋 Planned | Reusable pipeline definitions |
| `phase-9` | Project Health | 📋 Planned | Traceability + metrics |
| `phase-10` | Extract Libraries | 📋 Planned | Open-source 5 internal apps |

---

## Claude Code Instruction Files

All Claude Code instructions live in `.claude/`:

| File | Purpose |
|---|---|
| `PLATFORM.md` | Full platform vision, all phases, business context |
| `ARCHITECTURE.md` | System architecture, models, services, URL contracts |
| `CODING.md` | Django Way: DRY, fat models, skinny views, import rules |
| `AGENTS.md` | Agent patterns, AgentFactory usage, mock rules |
| `UI.md` | Dark theme, CSS classes, template hierarchy |
| `WORKSPACE.md` | Filesystem rules, path safety |
| `TESTING.md` | pytest rules, coverage requirements, mock strategy |
| `REVIEW.md` | Pre-merge checklist, code review standards |
| `SKILLS.md` | Reusable patterns library |
| `CODE_REVIEW.md` | Claude Code: automated code review execution |
| `TEST_GENERATION.md` | Claude Code: test script generation |
| `TEST_EXECUTION.md` | Claude Code: test execution and analysis |

---

## Tech Stack

- **Python** 3.11+ / **Django** 5.1
- **PostgreSQL** 15+
- **Anthropic API** — claude-sonnet-4-6, claude-haiku-4-5-20251001, claude-opus-4-6
- **Auth** — django-allauth (email + Google OAuth)
- **CSS** — Custom dark design system (DM Sans + DM Mono, no Bootstrap)
- **Testing** — pytest + factory-boy + pytest-mock

---

## Each Phase Branch is Independently Runnable

Switch to any phase branch and follow its `README-phase-N.md` to run it locally.
No phase depends on state from a previous branch — each is self-contained.
