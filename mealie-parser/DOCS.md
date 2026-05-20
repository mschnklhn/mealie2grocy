# Mealie Parser Documentation

## Installation

1. Add this repository to Home Assistant
   (*Settings → Add-ons → Add-on Store → ⋮ → Repositories*).
2. Install the **Mealie Parser** add-on.
3. Start the add-on – there is nothing to configure on the
   *Configuration* tab.
4. Open the web UI via Ingress (*Open Web UI* button on the add-on page).
5. On first launch you land on the **Settings** page. Enter your
   Mealie URL, Mealie API key and OpenAI API key there, then test the
   connection.

## Configuration

All configuration happens **inside the web UI** of the add-on, not in
the *Configuration* tab in Home Assistant. The Settings page in the web
UI asks for:

- **Mealie URL** – base URL of your Mealie instance, e.g.
  `http://homeassistant.local:9925`. If Mealie runs as a Home Assistant
  add-on you can also use the internal hostname, e.g.
  `http://db21ed7f-mealie:9000`.
- **Mealie API key** – long-lived token created in Mealie under
  *User → API Tokens*.
- **OpenAI API key** – required for the AI features.
- **OpenAI model** – defaults to `gpt-4o-mini`.
- **Review mode** – when enabled, every AI suggestion is shown as a
  preview and must be confirmed before it is written back to Mealie.

The values are stored in `/data/config.json` inside the add-on and
persist across restarts.

## Ingress and direct access

Ingress makes the UI reachable without opening any ports. If you also
want to reach the UI directly (e.g. from outside Home Assistant), set
`8000/tcp: 8000` in the *Network* section of the add-on – the UI is
then additionally reachable via `homeassistant.local:8000`.

## Privacy

Recipe data is sent to OpenAI to generate suggestions. If you do not
want that, do not enter an OpenAI API key and do not start any
AI-powered actions in the web UI.
