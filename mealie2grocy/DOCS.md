# Mealie2Grocy Documentation

## Installation
- Install the Addon in Home Assistant
- Configure the API keys in the Addon configuration
- Start the Addon and visit the web interface

## Usage
The data synchronization is based on the names of the products and units. To ensure a correct synchronization, make sure the names and units are the same in both Mealie and Grocy.

---

## Development

### Translations
The application is translated using flask-babel. To extract the strings for translation, run the following command in the app directory:
```bash
pybabel extract -F babel.cfg -o messages.pot .
```

Edit the `messages.pot` file for English translations and save it as messages.pot.

To update the translations, run the following command in the app directory:
```bash
pybabel update -i messages.pot -d translations
```

To create a new translation, run the following command in the app directory:
```bash
pybabel init -i messages.pot -d translations -l <language>
```

Finally, to compile the translations, run the following command in the app directory:
```bash
pybabel compile -d translations
```