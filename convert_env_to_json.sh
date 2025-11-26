#!/bin/bash

ENV_FILE=".env"
OUTPUT_FILE="secrets.json"

echo "{" > $OUTPUT_FILE
first=true

while IFS= read -r line || [ -n "$line" ]; do
  # skip empty lines and comments
  [[ -z "$line" || "$line" =~ ^# ]] && continue
  key="${line%%=*}"
  value="${line#*=}"
  # add comma if not the first entry
  if [ "$first" = true ]; then
    first=false
  else
    echo "," >> $OUTPUT_FILE
  fi
  echo "  \"$key\": \"$value\"" >> $OUTPUT_FILE
done < "$ENV_FILE"

echo -e "\n}" >> $OUTPUT_FILE

echo "Converted $ENV_FILE → $OUTPUT_FILE"
