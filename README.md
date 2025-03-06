# Mealie2Grocy

## About

This application transfers the Mealie shoppinglist to the Grocy shoppinglist.
As I prefer the use of Mealie for my recipes and Grocy for my inventory management and shoppinglist, this application automates the transfer between the two.

A web interface is provided to trigger the transfer and to view the logs.

## Installation
- Install the Addon in Home Assistant
- Configure the API keys in the Addon configuration
- Start the Addon and visit the web interface

## Usage
The data synchronization is based on the names of the products and units. To ensure a correct synchronization, make sure the names and units are the same in both Mealie and Grocy.

## Future plans
- [ ] Home Assistant integration
- [ ] Generic settings for units that should be treated as "present-only", e.g., "one teaspoon of salt"
- [ ] Automated transfer of the shoppinglist items
- [ ] Weekly meal plan generation based on Grocy inventory, preferences, and advanced rules
