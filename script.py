import funcs

# reading the 
df, dict_with_links = funcs.link_extractor()

print(dict_with_links)
# url = dict_with_links['e@UBCV'][0]
# print(funcs.clean_extracted_text(funcs.get_plaintext_from_url(url)))

# generated database 
programs = {}

for program in dict_with_links.keys():      # access the list containing the links for each of the programs
    for link in dict_with_links[program]:   # access each of the links in the list 
        text = funcs.get_plaintext_from_url(link)
        clean_text = funcs.clean_extracted_text(text)
        funcs.add_program(programs, program, link, clean_text)
        
        
# for key in programs:
    # print(programs[key][0])