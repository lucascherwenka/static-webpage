from enum import Enum
from htmlnode import *
from pathlib import Path
import re, os, shutil

class TextType(Enum):
    TEXT = "text"
    BOLD = "bold"
    ITALIC = "italic"
    CODE = "code"
    LINK = "link"
    IMAGE = "image"

class BlockType(Enum):
    PARAGRAPH = "paragraph"
    HEADING = "heading"
    CODE = "code"
    QUOTE = "quote"
    UNORDERED_LIST = "unordered_list"
    ORDERED_LIST = "ordered_list"

class TextNode:
    def __init__(self, text, text_type, url=None):
        self.text = text
        self.text_type = text_type
        self.url = url
    
    def __eq__(self, other):
        return (
            self.text == other.text and
            self.text_type == other.text_type and
            self.url == other.url

        )
    
    def __repr__(self):
        return f"TextNode({self.text}, {self.text_type.value}, {self.url})"

def text_node_to_html_node(text_node: TextNode) -> LeafNode:
    if text_node.text_type == TextType.TEXT:
        return LeafNode(None, text_node.text)
    elif text_node.text_type == TextType.BOLD:
        return LeafNode("b", text_node.text)
    elif text_node.text_type ==TextType.ITALIC:
        return LeafNode("i", text_node.text)
    elif text_node.text_type == TextType.CODE:
        return LeafNode("code", text_node.text)
    elif text_node.text_type == TextType.LINK:
        return LeafNode("a", text_node.text, {"href": text_node.url})
    elif text_node.text_type == TextType.IMAGE:
        return LeafNode("img", "", {"src": text_node.url, "alt": text_node.text})
    raise ValueError

def split_nodes_delimiter(old_nodes: list[TextNode], delimiter: str, text_type: TextType) -> list[TextNode]:
    new_list = []
    for node in old_nodes:
        if node.text_type is not TextType.TEXT:
            new_list.append(node)
        else:
            parts = node.text.split(delimiter)
            if len(parts) % 2 == 0:
                raise Exception("No closing delimiter found.")
            else:
                for num, part in enumerate(parts):
                    if part == "":
                        continue
                    if num % 2 == 0:
                        new_list.append(TextNode(part, TextType.TEXT))
                    else:
                        new_list.append(TextNode(part, text_type))
    return new_list

def extract_markdown_images(text):
    image_matches = re.findall(r"!\[([^\[\]]*)\]\(([^\(\)]*)\)", text)
    return image_matches

def extract_markdown_links(text):
    link_matches = re.findall(r"(?<!!)\[([^\[\]]*)\]\(([^\(\)]*)\)", text)
    return link_matches

def split_nodes_image(old_nodes: list[TextNode]) -> list[TextNode]:
    new_list = []
    for node in old_nodes:
        if node.text is None:
            continue
        if node.text_type is not TextType.TEXT:
            new_list.append(node)
        else:
            image_matches = extract_markdown_images(node.text)
            if len(image_matches) == 0:
                new_list.append(node)
            else:
                remaining_text = node.text
                for alt_text, url in image_matches:
                    sections = remaining_text.split(f"![{alt_text}]({url})", 1)
                    if sections[0] != "":
                        new_list.append(TextNode(sections[0], TextType.TEXT))
                    new_list.append(TextNode(alt_text, TextType.IMAGE, url))
                    remaining_text = sections[1]
                if len(remaining_text) != 0:
                    new_list.append(TextNode(remaining_text, TextType.TEXT))
    return new_list


def split_nodes_link(old_nodes: list[TextNode]) -> list[TextNode]:
    new_list = []
    for node in old_nodes:
        if node.text is None:
            continue
        if node.text_type is not TextType.TEXT:
            new_list.append(node)
        else:
            link_matches = extract_markdown_links(node.text)
            if len(link_matches) == 0:
                new_list.append(node)
            else:
                remaining_text = node.text
                for anchor, url in link_matches:
                    sections = remaining_text.split(f"[{anchor}]({url})", 1)
                    if sections[0] != "":
                        new_list.append(TextNode(sections[0], TextType.TEXT))
                    new_list.append(TextNode(anchor, TextType.LINK, url))
                    remaining_text = sections[1]
                if len(remaining_text) != 0:
                    new_list.append(TextNode(remaining_text, TextType.TEXT))
    return new_list

def text_to_textnodes(text):
    nodes = [TextNode(text, TextType.TEXT)]
    nodes = split_nodes_delimiter(nodes, "**", TextType.BOLD)
    nodes = split_nodes_delimiter(nodes, "_", TextType.ITALIC)
    nodes = split_nodes_delimiter(nodes, "`", TextType.CODE)
    nodes = split_nodes_image(nodes)
    nodes = split_nodes_link(nodes)
    return nodes

def markdown_to_blocks(markdown):
    finished_blocks = []
    blocks = markdown.split("\n\n")
    for block in blocks:
        stripped_blocks = block.strip()
        if stripped_blocks != "":
            finished_blocks.append(stripped_blocks)
        else:
            continue
    return finished_blocks

def block_to_block_type(block):
    lines = block.splitlines()
    if block.startswith(("# ", "## ", "### ", "#### ", "##### ", "###### ")):
        return BlockType.HEADING
    elif block.startswith("```\n") and block.endswith("```"):
        return BlockType.CODE
    elif block.startswith(">"):
        for line in lines:
            if not line.startswith(">"):
                return BlockType.PARAGRAPH
        return BlockType.QUOTE
    elif block.startswith("- "):
        for line in lines:
            if not line.startswith("- "):
                return BlockType.PARAGRAPH
        return BlockType.UNORDERED_LIST
    elif block.startswith("1. "):
        i = 1
        for line in lines:
            if not line.startswith(f"{i}. "):
                return BlockType.PARAGRAPH
            i += 1
        return BlockType.ORDERED_LIST
    else:
        return BlockType.PARAGRAPH

def text_to_children(text):
    list = text_to_textnodes(text)
    nodes = []
    for node in list:
        nodes.append(text_node_to_html_node(node))
    return nodes

def markdown_to_html_node(markdown):
    blocks = markdown_to_blocks(markdown)
    nodes = []
    for block in blocks:
        block_type = block_to_block_type(block)
        if block_type is BlockType.PARAGRAPH:
            children = text_to_children(block.replace("\n", " "))
            nodes.append(ParentNode("p", children))
        elif block_type is BlockType.CODE:
            children = text_node_to_html_node(TextNode(block[4:-3], TextType.TEXT))
            inner = ParentNode("code", [children])
            nodes.append(ParentNode("pre", [inner]))
        elif block_type is BlockType.HEADING:
            level = 0
            for hashtag in block:
                if hashtag == "#":
                    level += 1
                else:
                    break
            children = text_to_children(block[level+1:].replace("\n", " "))
            nodes.append(ParentNode(f"h{level}", children))
        elif block_type is BlockType.QUOTE:
            lines = block.split("\n")
            new_lines = []
            for line in lines:
                stripped_line = line.lstrip("> ")
                new_lines.append(stripped_line)
            children = text_to_children(" ".join(new_lines))
            nodes.append(ParentNode("blockquote", children))
        elif block_type is BlockType.UNORDERED_LIST:
            lines = block.split("\n")
            html_items = []
            for line in lines:
                children = text_to_children(line.lstrip("- "))
                html_items.append(ParentNode("li", children))
            nodes.append(ParentNode("ul", html_items))
        elif block_type is BlockType.ORDERED_LIST:
            lines = block.split("\n")
            html_items = []
            for line in lines:
                children = text_to_children(line.split(". ", 1)[1])
                html_items.append(ParentNode("li", children))
            nodes.append(ParentNode("ol", html_items))
            
    return ParentNode("div", nodes)

def generate_page(
    from_path: str, template_path: str, dest_path: str | Path, basepath: str
) -> None:
    print(f'Generating page from {from_path} to {dest_path} using {template_path}.')
    with open(from_path) as f:
        from_contents = f.read()
    with open(template_path) as f:
        template_contents = f.read()
    path_node = markdown_to_html_node(from_contents)
    html = path_node.to_html()
    title = extract_title(from_contents)
    title_replace = template_contents.replace("{{ Title }}", title)
    content_replace = title_replace.replace("{{ Content }}", html)
    replace_href = content_replace.replace('href="/', 'href="' + basepath)
    replace_src = replace_href.replace('src="/', 'src="' + basepath)
    directory = os.path.dirname(dest_path)
    os.makedirs(directory, exist_ok=True)
    with open(dest_path, mode='w') as f:
        f.write(replace_src)

def source_to_destination(source, destination):
    if os.path.exists(destination):
        shutil.rmtree(destination)
    os.mkdir(destination)
    for name in os.listdir(source):
        source_entry = os.path.join(source, name)
        destination_entry = os.path.join(destination, name)
        if not os.path.isfile(source_entry):
            source_to_destination(source_entry, destination_entry)
        else:
            shutil.copy(source_entry, destination_entry)
def extract_title(markdown):
    lines = markdown.splitlines()
    for line in lines:
        if line.startswith("# "):
            new_line = line.replace("# ", "")
            return new_line.strip()
    else:
        raise Exception("No Title")

def generate_pages_recursive(dir_path_content, template_path, dest_dir_path, basepath):
    content = os.listdir(dir_path_content)
    for file in content:
        current = os.path.join(dir_path_content, file)
        current_destination = os.path.join(dest_dir_path, file)
        if os.path.isfile(current):
            file_path = Path(current_destination)
            new_path = file_path.with_suffix(".html")
            generate_page(current, template_path, new_path, basepath)
        else:
            generate_pages_recursive(current, template_path, current_destination, basepath)
