import funcs
from tqdm import tqdm


df, dict_with_links = funcs.link_extractor()

# print(dict_with_links)
# print(funcs.clean_extracted_text(funcs.get_plaintext_from_url(url)))

# generated database used to store the extracted text with the tags
programs = {}

# extract the text from the links 
for program in tqdm(dict_with_links.keys(), desc="Programs"):  # access the list containing the links for each of the programs
    for link in tqdm(dict_with_links[program], desc=f"Processing {program}", leave=False):  # access each of the links in the list 
        text = funcs.get_plaintext_from_url(link)
        clean_text = funcs.clean_extracted_text(text)
        funcs.add_program(programs, program, link, clean_text)
        
        
# funcs.save_programs_csv(programs)





        
# print("Web scraping is finished")

