from textnode import generate_page, source_to_destination, generate_pages_recursive
import os, shutil
def main():
    source_to_destination("./static", "./public")
    generate_pages_recursive("./content", "./template.html", "./public")

main()
