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
ROOTDIR = '/var/www/modules'

HTML_FILETYPES = ['html', 'htm']
PDF_FILETYPES = ['pdf']

def clean_html(html: str) -> str:
    # Find every instance of href="http..." and delete entire href
    return re.sub('href *= *"http[^"<>]*"', '', html)

def clean_pdf(pdf: 'pdf') -> tuple['pdf', bool]:
    ''' Takes pdf, creates new pdf and copies pages (but without URLs) '''
    new_pdf = pdfrw.PdfWriter()
    is_changed = False

    for page in pdf.pages:
        # Links are in Annots, but some pages don't have links so Annots returns None
        for annot in page.Annots or []:
            try:
                old_url = annot.A.URI
                new_url = pdfrw.objects.pdfstring.PdfString('()')
                annot.A.URI = new_url
                is_changed = True
            except:
                pass

        new_pdf.addpage(page)
        
    return new_pdf, is_changed

def desc(num_files_screened, num_files_changed): 
    return f'Changed {num_files_changed} out of {num_files_screened} files'
    
def main():
    num_files_screened = 0
    num_files_changed  = 0
    
    progress_bar = tqdm(os.walk(ROOTDIR))
    # Walk through every file recursively from root directory
    for subdir, dirs, files in progress_bar:
        progress_bar.set_description(desc(num_files_screened, num_files_changed))
        for file in files:
            try:
                num_files_screened += 1
                progress_bar.set_description(desc(num_files_screened, num_files_changed))

                path = os.path.join(subdir, file)
                new_path = os.path.join(subdir, file)

                # If file is HTML-like, then clean up the links and overwrite file
                if file.split('.')[-1] in HTML_FILETYPES:
                    with open(path, 'r', encoding='ISO-8859-1') as fpin:
                        html = fpin.read()

                    clean = clean_html(html)
                    if len(html) == len(clean):
                        continue
                    num_html_changed += 1
                    progress_bar.set_description(desc(num_files_screened, num_files_changed))

                    with open(new_path, 'w', encoding='ISO-8859-1') as fpout:
                        fpout.write(clean)

                # If file is PDF, then clean up the links and overwrite file
                elif file.split('.')[-1] in PDF_FILETYPES:
                    pdf = pdfrw.PdfReader(path)

                    clean, is_changed = clean_pdf(pdf)
                    clean.write(new_path)

                    num_files_changed += is_changed
                    progress_bar.set_description(desc(num_files_screened, num_files_changed))
            except:
                pass
                
if __name__ == "__main__":
    main()
