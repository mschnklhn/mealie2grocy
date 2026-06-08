# Baby Buddy Planner Documentation

## Installation

1. Add the add-on repository to Home Assistant
   (*Settings → Add-ons → Add-on Store → ⋮ → Repositories*).
2. Install the **Baby Buddy Planner** add-on.
3. Start the add-on – there is nothing to configure on the
   *Configuration* tab.
4. Open the web UI via Ingress (*Open Web UI* button on the add-on page).
5. On first launch you land on the **Settings** page. Enter your
   Baby Buddy URL, API token and sleep intervals there, then test the
   connection.

## Configuration

All configuration happens **inside the web UI** of the add-on, not in
the *Configuration* tab in Home Assistant. The Settings page asks for:

- **Baby Buddy URL** – base URL of your Baby Buddy instance, e.g.
  `http://a0d7b954-babybuddy:8000` when Baby Buddy runs as a Home
  Assistant add-on.
- **API token** – token from Baby Buddy under *User Settings*.
- **Child ID** – numeric ID of the child in Baby Buddy.
- **Timezone** – e.g. `Europe/Berlin` for the calendar day view.
- **Day intervals** – wake and sleep duration in hours during the day
  (e.g. 1.5 h awake, 2.25 h sleeping).
- **Night window** – start/end time (24h format) and separate wake/sleep
  intervals for the night period (e.g. 20:00–07:00).

Values are stored in `/data/config.json` inside the add-on and persist
across restarts.

## Day view

The **Tagesansicht** shows the current calendar day (00:00–24:00):

- **Solid blue blocks** – actual sleep entries from Baby Buddy
- **Dashed blocks** – projected wake/sleep phases until midnight
- **Shaded background** – configured night window
- **Red line** – current time

Projections start from the last sleep (or active sleep timer) using
your configured intervals.

## Ingress and direct access

Ingress makes the UI reachable without opening any ports. To reach the
UI directly, set `8000/tcp: 8000` in the *Network* section of the
add-on.

## Publishing a new version

1. Tag the app repo: `git tag v0.1.0 && git push --tags`
2. Wait for CI to build and push images to GHCR
3. Make the GHCR package public (first time only)
4. Bump `version` in `ha-addon/babybuddy-planner/config.yaml`
5. Users update via the add-on store
