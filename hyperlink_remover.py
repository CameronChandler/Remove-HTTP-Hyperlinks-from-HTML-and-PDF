############################################################################
# Written by Cameron Chandler 26/06/2022 for Teacher in a Box              #
# Python3 script to remove http hyperlinks from html and pdf documents     #
# requires installation (via internet) of pdfrw (tqdm is for loading bars) #
############################################################################

import os
from tqdm import tqdm
import re
import pdfrw

# Change ROOTDIR to be the path to the `modules` folder
ROOTDIR = r'C:\Computer\var\www\modules'

HTML_FILETYPES = ['html', 'htm']
PDF_FILETYPES = ['pdf']

count = sum(1 for _, _, files in os.walk(ROOTDIR))

def clean_html(html: str) -> str:
    # Find every instance of href="http..." and delete entire href
    return re.sub('href *= *"http[^"<>]*"', '', html)

def clean_pdf(pdf: 'pdf') -> 'pdf':
    ''' Takes pdf, creates new pdf and copies pages (but without URLs) '''
    new_pdf = pdfrw.PdfWriter()

    for page in pdf.pages:
        # Links are in Annots, but some pages don't have links so Annots returns None
        for annot in page.Annots or []:

            old_url = annot.A.URI
            new_url = pdfrw.objects.pdfstring.PdfString('()')
            annot.A.URI = new_url

        new_pdf.addpage(page)
        
    return new_pdf

def main():
    # Walk through every file recursively from root directory
    for subdir, dirs, files in tqdm(os.walk(ROOTDIR), total=count):
        for file in files:
            path = os.path.join(subdir, file)
            new_path = os.path.join(subdir, file)
            
            # If file is HTML-like, then clean up the links and overwrite file
            if file.split('.')[-1] in HTML_FILETYPES:
                with open(path, 'r', encoding='ISO-8859-1') as fpin:
                    html = fpin.read()

                clean = clean_html(html)
                if len(html) == len(clean):
                    continue

                with open(new_path, 'w') as fpout:
                    fpout.write(clean)
                    
            # If file is PDF, then clean up the links and overwrite file
            elif file.split('.')[-1] in PDF_FILETYPES:
                pdf = pdfrw.PdfReader(path)

                clean = clean_pdf(pdf)
                clean.write(new_path)
                
if __name__ == "__main__":
    main()