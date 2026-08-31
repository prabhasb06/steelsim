import os, glob

for filepath in glob.glob("src/**/*.tsx", recursive=True):
    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()
    
    text = text.replace("\\`", "`")
    text = text.replace("\\${", "${")
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(text)
