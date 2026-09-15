from textnode import generate_page, source_to_destination, generate_pages_recursive
import os, shutil, sys

default_basepath = "/"

def main():
    basepath = default_basepath
    if len(sys.argv) > 1:
        basepath = sys.argv[1]
    source_to_destination("./static", "./docs")
    generate_pages_recursive("./content", "./template.html", "./docs", basepath)
    
main()
