#!/bin/bash
# Array mit den Banknamen, hier wird vorausgesetzt, dass der Ordner "Bank Statements" in jedem Verzeichnis liegt.
banks=("Barclays Bank Ireland PLC" "ING-DiBa AG" "Consorsbank")
base_dir="/home/$USER/Documents/institutions/Financial Institutes"

# Erzeuge einen Array mit vollständigen Pfaden zu den "Bank Statements"-Verzeichnissen
input_paths=()
for bank in "${banks[@]}"; do
  input_path="${base_dir}/${bank}/Bank Statements/"
  output_csv="${base_dir}/${bank}/transactions.csv"
  echo "Verarbeite ${bank} aus ${input_path} ..."
  python main.py -r "$input_path" "$output_csv"
  input_paths+=("${input_path}")
done

# Rufe main.py mit allen Eingabe-Pfaden auf (die Output-CSV kann z. B. zentral gespeichert werden)
python main.py -r "${input_paths[@]}" "${base_dir}/transactions.csv"
