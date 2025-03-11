import pdfplumber
import pandas as pd
from code.model.log import Log

class ConsorbankDataFrame:
    def __init__(self, pdf_path:str, log:Log):
        """
        Initializes the ConsorbankDataFrame class with the provided PDF path,
        minimum top threshold for filtering words, and margin for defining column ranges.

        :param pdf_path: Path to the PDF file to be processed.
        """
        self.pdf_path = pdf_path
        self.log = log
        self.top_diference=6
        
        # Column definitions with margins applied
        self.columns = {
            "Text/Verwendungszweck": (46.2 - 40, 153.204 + 40),
            "Datum": (233.1 - 100, 261.101 + 6),
            "PNNr": (272.75 - 6, 295.251 + 10),
            "Wert": (311.55 - 10, 331.547 + 50),
            "Soll": (433.45 - 50, 449.952 + 35),
            "Haben": (521.6 - 35, 549.099 + 100)
        }

    def extract_data(self):
        """
        Extracts data from the PDF and returns it as a pandas DataFrame.
        The words in the PDF are assigned to columns based on their X-coordinates and grouped by `top` position.
        """
        rows = []
        current_row = None
        last_top = None 

        # Open the PDF file
        with pdfplumber.open(self.pdf_path) as pdf:
            for page in pdf.pages:
                words = page.extract_words()

                for word in words:
                    text = word["text"].strip()
                    x_left = word["x0"]
                    x_right = word["x1"]
                    top = word["top"]

                    # If we detect a new row based on the `top` position difference
                    if last_top is None or abs(last_top - top) > self.top_diference:  # Adjust the difference threshold as needed
                        if current_row:
                            rows.append(current_row)
                        current_row = {col: "" for col in self.columns.keys()}

                    # Assign the word to the appropriate column based on its X-coordinate
                    assigned = False
                    for col_name, (col_min, col_max) in self.columns.items():
                        if x_left >= col_min and x_right <= col_max:
                            current_row[col_name] += text + " "
                            assigned = True
                            break

                    # If the word doesn't fit into any column, we ignore it
                    if not assigned:
                        continue

                    # Store the current `top` position for the next row
                    last_top = top

            # After processing all pages, append the last row
            if current_row:
                rows.append(current_row)

        # Convert the rows into a DataFrame
        df = pd.DataFrame(rows)
        self.log.debug(f"Dataframe: {df.to_string()}")
        return df