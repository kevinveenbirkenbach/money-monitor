#!/bin/bash
# Array mit den Banknamen, hier wird vorausgesetzt, dass der Ordner "Bank Statements" in jedem Verzeichnis liegt.
banks=("Barclays Bank Ireland PLC" "ING-DiBa AG" "Consorsbank" "Paypal")
base_dir="/home/$USER/Documents/institutions/Financial Institutes"

# Für jede Bank wird zuerst ein eigener Export erstellt...
for bank in "${banks[@]}"; do
  input_path="${base_dir}/${bank}/Bank Statements/"
  output_file="${base_dir}/${bank}/transactions"  # Basisname, ohne Suffix
  echo "Verarbeite ${bank} aus ${input_path} ..."
  # Exportiere rekursiv in CSV
  python main.py -r "$input_path" "$output_file" --csv
done

# Anschließend kannst du alle Pfade zusammenfassen und z. B. einen kombinierten JSON-Export erstellen:
input_paths=()
for bank in "${banks[@]}"; do
  input_paths+=("${base_dir}/${bank}/Bank Statements/")
done
python main.py -r "${input_paths[@]}" "${base_dir}/transactions" --csv --html
