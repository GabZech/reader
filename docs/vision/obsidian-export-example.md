---
author: Josh Rosen 

published_date: 2026-08-13 

source: https://x.com/JoshARosen/status/2087944178558791874/?rw_tt_thread=True 


last_highlighted_date: 2026-08-15
---
# Subagents on Subagents: How Many Layers Deep Is Too Many?

## Summary

>Agents can delegate tasks to subagents, creating a complex graph of work instead of a simple chain. Mistakes early in this graph can affect many later results, while errors near the end have smaller impact. The key is managing how errors spread by controlling dependencies, not limiting how deep the delegation goes.

## Highlights
### Subagents

- Agents are starting to spawn agents. Give an agent a sufficiently large job and one increasingly common strategy is delegation. The parent agent decides that part of the work should be handled somewhere else, spins up a subagent with its own context and instructions, waits for the result, and continues. That subagent may eventually do the same thing.

- There are good reasons to work this way. A subagent can have a narrower job, a cleaner context window, different tools, or instructions specialized for the task it has been given. It can also do a large amount of exploratory work without dumping all of that context back into the parent. Once agents can delegate recursively, though, an obvious question appears: **how many layers deep should we let them go?**
### Graph engineering

- You can think about a parent spawning subagents as a tree. The parent delegates to several workers, some workers delegate again, and results eventually flow back toward the top. But real systems quickly become more complicated than trees.
   One agent’s research becomes another agent’s input. Several branches get joined together. A reviewer evaluates the output of a worker. A planner produces a plan that several executors follow. Some branches run in parallel while others cannot begin until their dependencies finish. At that point, you have a graph.

- That is roughly what people have started calling **graph engineering**: making the nodes, dependencies, routing, and state transitions between pieces of agentic work explicit. This framing changes the way we think about subagents because instead of asking only, “How many agents are running?” or “How deeply are they nested?”, we can ask what each node produces, which other nodes consume it, and what portion of the eventual result depends on it.

- That is a much more useful way to reason about reliability because not every node carries the same amount of risk. Some nodes sit at the edge of the graph and produce a small, isolated contribution. Others sit high in the graph and establish the premises that many later nodes will use.
### Errors have a blast radius

- Imagine an agent producing a competitive analysis. The first agent decides which competitors matter. Three subagents research those companies. Their outputs feed another agent that compares the products. That comparison goes to another agent that identifies strategic threats, and a final agent writes recommendations.

- If the final writing agent phrases one recommendation poorly, you have a fairly localized problem. Most of the underlying work is still intact. If the first agent picks the wrong competitors, everything downstream can be perfectly executed and the final answer can still be wrong.
   The important distinction is **where the error entered the graph and how much work depends on it**.

- The number of layers matters, but **the downstream influence of each layer matters more**. A deeply nested agent working on an isolated task may have very little impact on the final result, while a shallow agent making an early routing or planning decision may determine everything that follows.
### Context isolation is a problem

- There is another problem with deeply nested subagents: information gets transformed at every boundary. A subagent might inspect twenty documents and return a five-paragraph summary. Its parent uses that summary to create a plan. Another agent receives part of the plan and turns it into an analysis, while a final agent synthesizes several analyses into a recommendation.

- Context isolation is part of the benefit of subagents, but it also creates distance between the final decision and the evidence that originally supported it.
### Dependency engineering

- This is why I think one of the most important parts of graph engineering will be deciding **what is allowed to depend on what**. If an agent produces something with enormous downstream influence, that node deserves more scrutiny than a node producing an isolated piece of the final response.

- Maybe it should have a verifier. Maybe its output needs to be structured. Maybe the original evidence should travel alongside its conclusion. Maybe several agents should independently produce the result before the graph moves forward.
### The metric is “blast radius”

- The metric I care about is closer to **blast radius**. For any agent-generated artifact, ask what else becomes wrong if that artifact is wrong. If the answer is one small part of the final output, you can probably tolerate a fairly agentic node. If the answer is every remaining step in the workflow, that node deserves a very different engineering standard.
