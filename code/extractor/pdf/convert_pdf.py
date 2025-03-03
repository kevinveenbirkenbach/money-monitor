import os
import PyPDF2

from code.logger import Logger

class ConvertPDF:
    def __init__(self, output_base: str, logger: Logger):
        self.output_base = output_base
        self.logger = logger  # Use the logger instance
        self.txt_output_dir = os.path.join(output_base, "txt")

        # If debugging is enabled, create the txt directory if it doesn't exist
        if self.logger.debug_enabled and not os.path.exists(self.txt_output_dir):
            os.makedirs(self.txt_output_dir)

    def convert(self, pdf_path: str, return_text=False):
        """Convert PDF to text and either return the text or save it as a .txt file."""
        try:
            with open(pdf_path, 'rb') as pdf_file:
                # Initialize PDF reader
                pdf_reader = PyPDF2.PdfReader(pdf_file)
                text = ""
                
                # Loop through all pages and extract text
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + '\n'  # Add text with a newline to separate pages
                
                if return_text:
                    return text  # Return the extracted text
                else:
                    # Save the text to a file
                    pdf_name = os.path.splitext(os.path.basename(pdf_path))[0] + ".txt"
                    txt_path = os.path.join(self.txt_output_dir, pdf_name)
                    with open(txt_path, 'w', encoding='utf-8') as txt_file:
                        txt_file.write(text)
                    
                    if self.logger.debug_enabled:
                        self.logger.debug(f"PDF successfully exported to {txt_path}")
                    return txt_path  # Return the path of the saved file

        except Exception as e:
            self.logger.error(f"Error processing {pdf_path}: {e}")
            raise Exception(f"Error processing {pdf_path}: {e}")
