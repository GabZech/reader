# Reader

## Overview

Reader is a personal reading hub for one person. It brings newsletters, feeds, and saved articles into one place you control, so daily reading stays simple and the material remains yours to organise, highlight, and keep.

The product is built for a solo reader who wants full ownership of their corpus, light-touch curated lists, and an easy path from highlights into an Obsidian vault. It is not a shared or multi-user app.

## How we work

Left alone, an agent will start coding before either side understands the product. This repo uses a SPEC-driven workflow (from [template-spec-workflow](https://github.com/GabZech/template-spec-workflow)): agree what matters, then build only what was accepted. Every step ends with an explicit accept before the next begins.

Discovery and foundation run once. After that, work repeats one feature at a time. For the full playbook, see the [template workflow overview](https://github.com/GabZech/template-spec-workflow#workflow-overview).

## Docs

The `Docs/` folder is split by the kind of question you are asking. The list below is the front door; the [index](docs/README.md) has the rest.

- **[Roadmap](docs/roadmap.md):** Start here to see the current phase, what is already locked, and what this phase still has to settle.
- **[Architecture](docs/architecture.md):** The shape of the running system, covering what we build, what we rent, how mail and feeds get in, and which tradeoffs we accepted so later work does not reopen the whole stack.
- **[Development](docs/development.md):** How to run the app on this machine, including toolchain, start command, tests, and local config names.
- **[Operations](docs/operations.md):** How that same app is meant to stay on a host, including backup of the library file and the monthly cost ceiling.
- **[UI guidelines](docs/ui-guidelines.md):** The overall look copied from the accepted dummy, so later screens follow layout, density, chrome, and quiet type instead of inventing a new visual language.

