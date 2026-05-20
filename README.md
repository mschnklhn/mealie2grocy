# mschnklhn's Home Assistant Apps

A Home Assistant App repository containing apps around
[Mealie](https://mealie.io/) and [Grocy](https://grocy.info/).

## Add this repository to Home Assistant

In Home Assistant go to *Settings → Add-ons → Add-on Store →
⋮ (top right) → Repositories* and add:

```
https://github.com/mschnklhn/mealie2grocy
```

## Available add-ons

### [Mealie2Grocy](./mealie2grocy)

Transfers the Mealie shopping list to the Grocy shopping list. As Mealie
is great for recipes and Grocy for inventory management and shopping
lists, this add-on automates the transfer between the two. A web
interface is provided to trigger the transfer and view the logs.

### [Mealie Parser](./mealie-parser)

Standardizes recipes from a Mealie instance using OpenAI:

- Assigns tags and categories from your existing inventory.
- Rewrites preparation steps in a unified, fine-grained way.
- Automatically links ingredients to the matching step.

You get a preview before anything is saved and can adjust suggestions
manually. The container image is pulled from
`ghcr.io/mschnklhn/mealie-parser-{arch}`.
