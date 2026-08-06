# SPEC-driven Workflow Template

This is a template to ensure AI agents follow best practices in product management and specification-driven development when developing software. The core difference to other workflows is that it applies SPEC philosophy not only to individual feature development, but to the **entire product lifecycle**.

Left alone, an AI agent will happily start writing application right after your first prompt. At that point, neither the agent (i.e. the delivery team) or you (i.e. the client) usually have a good understanding of the full requirements for the final solution should be. This leads to frustating errors and misguided actions.

So the point of the template is that it **imposes a structured workflow** in front of that impulse: it forces AI agents to guide you through understanding the problem, iterating through the requirements, fleshing out the details, designing the overall foundation, and only then building the features one at a time.


## Workflow Overview

The work runs in two stages: 
1. **Product discovery and foundation**: happens once, at the beginning, to figure out what the product is and lay its technical foundation. 
2. **Feature development** repeats for every feature you decide to build, for as long as the product lives.

### 1. Product Discovery and Foundation

This stage runs once, at the start of a new product. It moves from a rough idea in your head to a system that is designed and scaffolded, ready to receive features. Nothing here is application code except the final scaffold.

#### 1.1 Kickoff

- 🎯 Goal: Capture the product idea from the client's initial prompt, ask clarifying questions and turn the result into a clear problem statement, product vision, non-goals, and success measures.

- 📄 Artifacts:

  - `docs/roadmap.md`: initialised with where we are
  - `docs/product-definition/vision.md`: problem, vision, and non-goals
  - `docs/product-definition/metrics.md`: how success will be measured


#### 1.2 Understand

- 🎯 Goal: Interrogate the vision: who uses the product, what they are trying to do, and the detail, edge cases, and constraints that make those journeys real.

- 📄 Artifacts:

  - `docs/product-definition/personas.md`: who uses the product
  - `docs/product-definition/journeys.md`: what they are trying to do
  - `docs/product-definition/constraints.md`: cross-cutting rules and limits that shape the product

#### 1.3 Scope

- 🎯 Goal: Turn journeys into epics, then decide what belongs in the prototype, the MVP, and later.

- 📄 Artifacts:

  - `docs/product-definition/epics.md`: chunks of work and the prototype / MVP / later cut

#### 1.4 Prototype

- 🎯 Goal: Make the priority journeys clickable in Figma before a line of product code exists and iterate according to feedback.

- 📄 Artifacts:

  - `docs/history/discovery/04-prototype/`: prototype link and walkthrough

#### 1.5 Foundation

- 🎯 Goal: Design the system once, and build its skeleton: architecture, stack, application shell, and operational basics.

- 📄 Artifacts:

  - `docs/architecture.md`: living description of the system
  - `docs/development.md`: local setup and how features are built (where relevant)
  - `docs/operations.md`: deploy, backup, verify, restore (where relevant)
  - Repository scaffold: application shell and operational basics
  - `docs/history/decisions/`: significant technical choices as decision records

---

### 2. Feature Development

From here on, every feature follows the same eight steps, repeated once per feature. The approach follows a SPEC-driven development practice: before any code is written, the feature is pinned down in three documents (requirements, design, and tasks) that you review and accept. Those documents are the contract: the build phase then implements exactly what was agreed.

Each feature gets its own folder, `docs/specs/<feature-slug>/`, created when the work starts. Once Foundation is accepted, the agent proposes the first feature.

#### 2.1 Requirements

- 🎯 Goal: State what the feature must do, as user stories with testable acceptance criteria.

- 📄 Artifacts:

  - `docs/specs/<feature-slug>/requirements.md`: user stories and acceptance criteria

#### 2.2 Design

- 🎯 Goal: Explain how this feature fits into the architecture that already exists.

- 📄 Artifacts:

  - `docs/specs/<feature-slug>/design.md`: how the feature fits the existing architecture

#### 2.3 Tasks

- 🎯 Goal: Break the design into an ordered list of implementation steps small enough to execute and check off.

- 📄 Artifacts:

  - `docs/specs/<feature-slug>/tasks.md`: ordered implementation steps

#### 2.4 Build

- 🎯 Goal: Implement the approved tasks, and only those, on a feature branch.

- 📄 Artifacts:

  - Working software on the feature branch: the approved tasks, implemented

#### 2.5 Review

- 🎯 Goal: Walk the built software back against the acceptance criteria agreed in step 2.1, make adaptations where needed, and get final acceptance.

- 📄 Artifacts:

  - `docs/specs/<feature-slug>/review/`: append-only notes of what was checked and when

#### 2.6 Document

- 🎯 Goal: Bring the permanent documentation back in line with reality, on the same branch as the code.

- 📄 Artifacts:

  - `docs/architecture.md`, `docs/roadmap.md`, `docs/development.md`, `docs/operations.md`: updated as needed
  - `docs/history/decisions/`: new decision records where choices were made
  - `docs/history/plans/`: archived implementation plans
  - `docs/specs/<feature-slug>/`: frozen after acceptance

#### 2.7 Deploy

- 🎯 Goal: Ship the finished slice to its live environment.

- 📄 Artifacts:

  - `docs/specs/<feature-slug>/deploy/`: append-only deploy notes

#### 2.8 Monitor

- 🎯 Goal: Look at the feature running in the real environment and gather short evidence that it behaves as intended.

- 📄 Artifacts:

  - `docs/specs/<feature-slug>/monitor/`: append-only evidence notes


#### 🏁 Milestone: MVP

When every epic in the MVP cut has been through this eight-step cycle, the roadmap records **Milestone: MVP**. Nothing about the process changes afterwards: further features keep following the same loop for as long as the product is being developed.

---

### How It Plays Out: A Short Example

A client arrives with one sentence: "build an app for X."

The agent starts at **Kickoff**, capturing the idea, explaining how the engagement will run, asking clarifying questions, and turning that into a problem statement, vision, non-goals, and success measures. **Understand** turns that into personas, journeys, and the constraints that shape them. **Scope** packages journeys into epics and decides prototype / MVP / later. **Prototype** makes the main journey clickable in Figma, and once accepted the roadmap records **Milestone: Prototype**. **Foundation** then settles the stack and scaffolds the repository. Each of those phases ended with a review the client had to accept.

Only now does code for a feature begin. The first feature is pinned down in requirements, design and tasks, accepted, built on a branch, tried by the client against the criteria with occasional adaptations, then finally accepted, documented, deployed and observed. The next feature repeats the loop. When the last MVP epic is through, the roadmap records **Milestone: MVP**, and the same loop continues for whatever comes next.

---

## Repository Structure

The template ships no product code. What it ships is a place for decisions to land, so the reasoning behind the product survives the chat that produced it.

```text
├── README.md                 # This manual
├── .gitignore                # Paths excluded from version control
├── .cursor/rules/            # Agent rules that steer the engagement
│   └── engagement.mdc        # Engagement workflow rules for agents
└── docs/                     # Project documentation
    ├── README.md             # Map of the docs tree
    ├── conventions.md        # Standards for writing and deciding in docs
    ├── roadmap.md            # Where we are + what we are building
    ├── product-definition/   # Vision, personas, journeys, constraints, epics, metrics
    ├── architecture.md       # How the system is designed and fits together
    ├── development.md        # How to run and build the product locally
    ├── operations.md         # How the live system is run and recovered
    ├── ui-guidelines.md      # Visual and interaction rules for the UI
    ├── specs/                # Requirements, design, and delivery notes per feature
    └── history/              # Record of what was agreed over time
        ├── discovery/        # Accepted outcomes from discovery phases
        ├── decisions/        # Why major technical choices were made
        └── plans/            # Implementation plans kept after the work
```


⚠️ Important Information
- Placeholder files under `docs/` start as titles only. Real content is written when work reaches the phase that needs it.
- Everything under `docs/history/` records what was agreed and decided during the engagement and development; the other files describe how the product works today and stay updated.


---

## How to Start

1. On GitHub, choose **Use this template** and create a new repository.
2. Clone that repository and open it as your Cursor workspace.
3. In your first prompt, say what you want to build, for example "we will build an app for X".
4. The agent begins at **Kickoff**, then **Understand**, and so on. Coding will only start at the end of the product discovery phase.
