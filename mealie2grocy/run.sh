#!/usr/bin/with-contenv bashio
echo -e "\e[90m--------------------------------------------\e[0m"
echo -e "\e[1;33m🚀 Mealie ↔ Grocy Sync\e[0m"
echo -e "\e[1;34mSeamlessly syncing your Mealie shopping list with Grocy!\e[0m"
echo -e "\e[90m--------------------------------------------\e[0m"

CONFIG_PATH=/data/options.json
export MEALIE_BASE_URL="$(bashio::config 'MEALIE_BASE_URL')"
export MEALIE_API_KEY="$(bashio::config 'MEALIE_API_KEY')"
export GROCY_BASE_URL="$(bashio::config 'GROCY_BASE_URL')"
export GROCY_API_KEY="$(bashio::config 'GROCY_API_KEY')"
export API_KEYS="$(bashio::config 'API_KEYS')"

cd /app
exec gunicorn -w 4 -b 0.0.0.0:9193 --access-logfile - wsgi:app