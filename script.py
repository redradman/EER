import sys



import funcs

# reading the 
df, dict_with_links = funcs.link_extractor()

print(dict_with_links)
url = dict_with_links['e@UBCV'][0]
print(funcs.clean_extracted_text(funcs.get_plaintext_from_url(url)))



