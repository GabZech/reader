# Operations

## Purpose

How this one-person system is hosted, deployed, and kept on, within the $10 USD/month ceiling.

## Where it runs

A small always-on Fly.io container serving the web app. The SQLite file lives on a volume attached to that container. The phone and computer reach it over the internet. A later move to a machine you own is the same Docker image plus that file.

Local run is for development. The intended production path is hosted.

## Deploy

Build the Docker image from the repo root and deploy it to the container host from GitHub (or the Fly CLI). The volume must stay attached so the library survives a new version.

Until Docker and a Fly (or equivalent) account are available on the operator's machine, the hosted smoke test cannot be run from this repo. Local run plus tests prove the app; they do not prove the host.

## Config and secrets

Injected as environment variables on the host. Secrets stay out of Git.

- `DATABASE_PATH`: path to the SQLite file on the volume
- `SKELETON_FEED_URL`: public RSS URL for the skeleton sync
- Later: isolated-mailbox IMAP host, user, and app password. Never personal-mailbox credentials.

## Backup and data control

The library is the SQLite file. Copy it off the volume (or off `data/reader.db` locally) to back up. That file is what you move to another host. Highlights will later be markdown you already keep in the vault.

## Cost

A small always-on Fly.io machine plus volume is expected to sit near a few USD per month, under the $10 ceiling and in reach of the $5 preference. No App Store fee. The consumer mailbox is already paid for. Stay off sleeping free tiers: wake time would eat the morning sync bound.

## Smoke test

After deploy: open the hosted URL on a phone or computer, wait for Home to finish sync, confirm News shows feed items, then turn on airplane mode and open an item already seen. It should still read.
