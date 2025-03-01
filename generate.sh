#!/bin/bash
# Array mit den Banknamen
banks=("Barclays Bank Ireland PLC" "ING-DiBa AG" "Consorsbank")

# Basisverzeichnis
base_dir="/home/$USER/Documents/institutions/Financial Institutes"

# Iteration über die Banknamen
for bank in "${banks[@]}"; do
  input_path="${base_dir}/${bank}/Bank Statements/"
  output_csv="${base_dir}/${bank}/transactions.csv"
  echo "Verarbeite ${bank} aus ${input_path} ..."
  python main.py "$input_path" "$output_csv" --cat
done
