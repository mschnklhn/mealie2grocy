# Mealie Parser

Standardize recipes from a [Mealie](https://mealie.io/) instance using OpenAI:

- Tags and categories are assigned from your existing inventory.
- Preparation steps are unified and rewritten in a fine-grained way.
- Ingredients are automatically linked to the matching step.

You get a preview before anything is saved and can adjust suggestions manually.

> **Note:**
> This project is fully *vibe coded* – quality and design are the result of
> improvisation and inspiration. Use at your own risk.

## Installation

- Install this add-on in Home Assistant from this repository.
- Start the add-on – no add-on options need to be filled in.
- Open the web UI via Ingress (or the optional direct port `8000/tcp`).
- On first launch you land on the **Settings** page. Enter your Mealie
  URL, Mealie API key and OpenAI API key there and test the connection.
  The values are stored in `/data/config.json` and persist across restarts.

## Privacy

Recipe data is sent to OpenAI. If you do not want that, do not enter an
OpenAI API key and do not start any AI-powered actions.

## Source

The container image is built and published from
[`mschnklhn/mealie-parser`](https://github.com/mschnklhn/mealie-parser)
to `ghcr.io/mschnklhn/mealie-parser-{arch}`.
