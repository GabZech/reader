# Reader

## Overview

Reader is a personal reading hub for one person. It brings newsletters, feeds, and saved articles into one place you control, so daily reading stays simple and the material remains yours to organise, highlight, and keep.

The product is built for a solo reader who wants full ownership of their corpus, light-touch curated lists, and an easy path from highlights into an Obsidian vault. It is not a shared or multi-user app.

## How we work

Left alone, an agent will start coding before either side understands the product. Discovery and foundation run once: agree what matters, design the system, and hang a walking skeleton. After that, each epic is Build then Deploy. Build is a short try-and-sign-off loop like Mockup, on a local instance of the real software, with the usual checks (continuous integration) before each slice is shown. Deploy is the continuous-delivery release: put signed-off work on the production host when the epic is done or when you ask to ship, smoke the live path, and let living docs catch up. That is not continuous deployment of every local change. Every phase ends with an explicit accept before the next begins.

For discovery and foundation, see the [template workflow overview](https://github.com/GabZech/template-spec-workflow#workflow-overview). Feature work in this repo is Build then Deploy, not that template’s SPEC stairs.

## Docs

The `Docs/` folder is split by the kind of question you are asking. The list below is the front door; the [index](docs/README.md) has the rest.

- **[Roadmap](docs/roadmap.md):** Start here to see the current phase, what is already locked, and what this phase still has to settle.
- **[Architecture](docs/architecture.md):** The shape of the running system, covering what we build, what we rent, how mail and feeds get in, and which tradeoffs we accepted so later work does not reopen the whole stack.
- **[Development](docs/development.md):** How to run the app on this machine, including toolchain, start command, tests, and local config names.
- **[Operations](docs/operations.md):** How that same app is meant to stay on a host, including backup of the library file and the monthly cost ceiling.
- **[UI guidelines](docs/ui-guidelines.md):** The overall look copied from the accepted dummy, so later screens follow layout, density, chrome, and quiet type instead of inventing a new visual language.

