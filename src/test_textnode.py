import unittest
from main import extract_title
from textnode import(
    markdown_to_blocks, TextNode, TextType, text_node_to_html_node, split_nodes_delimiter, extract_markdown_images, 
    extract_markdown_links, split_nodes_image, 
    split_nodes_link, text_to_textnodes,
    BlockType, block_to_block_type,
    markdown_to_html_node, text_to_children
)


class TestTextNode(unittest.TestCase):
    def test_eq(self):
        node = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is a text node", TextType.BOLD)
        self.assertEqual(node, node2)
    def test_neq(self):
        node = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is a text node", TextType.ITALIC)
        self.assertNotEqual(node, node2)
    def test_url(self):
        node = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is a text node", TextType.BOLD)
        self.assertIsNone(node.url)
    def test_equrl(self):
        node = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is a text node", TextType.BOLD)
        self.assertEqual(node.url, node2.url)
    def test_nequrl(self):
        node = TextNode("This is a text node", TextType.BOLD, "www.github.com")
        node2 = TextNode("This is a text node", TextType.BOLD)
        self.assertNotEqual(node.url, node2.url)
    def test_text(self):
        node = TextNode("This is a text node", TextType.TEXT)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, None)
        self.assertEqual(html_node.value, "This is a text node")
    def test_delim_no_close(self):
        with self.assertRaises(Exception):
            split_nodes_delimiter([TextNode("this is some text **wow thats neat!", TextType.TEXT)], "**", TextType.BOLD)
        with self.assertRaises(Exception):
            split_nodes_delimiter([TextNode("this is some text _wow thats neat!", TextType.TEXT)], "_", TextType.ITALIC)
        with self.assertRaises(Exception):
            split_nodes_delimiter([TextNode("this is some text `CODE thats neat!", TextType.TEXT)], "`", TextType.CODE)
    def test_delim_works(self):
        node = split_nodes_delimiter([TextNode("This is some text **wow** this is some bold text, how neat is **that**", TextType.TEXT)], "**", TextType.BOLD)
        node2 = [
            TextNode("This is some text ", TextType.TEXT),
            TextNode("wow", TextType.BOLD),
            TextNode(" this is some bold text, how neat is ", TextType.TEXT), 
            TextNode("that", TextType.BOLD)
        ]
        self.assertEqual(node, node2)

    def test_extract_markdown_images(self):
        image_matches = extract_markdown_images(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png)"
        )
        self.assertListEqual([("image", "https://i.imgur.com/zjjcJKZ.png")], image_matches)

    def test_extract_markdown_links(self):
            link_matches = extract_markdown_links(
                "This is text with a link [to boot dev](https://www.boot.dev) and [to youtube](https://www.youtube.com/@bootdotdev)"
            )
            self.assertListEqual([("to boot dev", "https://www.boot.dev"), ("to youtube", "https://www.youtube.com/@bootdotdev")], link_matches) 

    def test_split_images(self):
        node = TextNode(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png) and another ![second image](https://i.imgur.com/3elNhQu.png)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("This is text with an ", TextType.TEXT),
                TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
                TextNode(" and another ", TextType.TEXT),
                TextNode("second image", TextType.IMAGE, "https://i.imgur.com/3elNhQu.png"),
            ],
            new_nodes,
        )

    def test_split_link(self):
        node = TextNode(
            "This is text with a link [to boot dev](https://www.boot.dev) and [to youtube](https://www.youtube.com/@bootdotdev)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_link([node])
        self.assertListEqual(
            [
                TextNode("This is text with a link ", TextType.TEXT),
                TextNode("to boot dev", TextType.LINK, "https://www.boot.dev"),
                TextNode(" and ", TextType.TEXT),
                TextNode("to youtube", TextType.LINK, "https://www.youtube.com/@bootdotdev"),
            ],
            new_nodes
        )

    def test_text_to_textnodes(self):
        node = "This is **text** with an _italic_ word and a `code block` and an ![obi wan image](https://i.imgur.com/fJRm4Vk.jpeg) and a [link](https://boot.dev)" 
        new_nodes = text_to_textnodes(node)
        self.assertListEqual(
            [
                TextNode("This is ", TextType.TEXT),
                TextNode("text", TextType.BOLD),
                TextNode(" with an ", TextType.TEXT),
                TextNode("italic", TextType.ITALIC),
                TextNode(" word and a ", TextType.TEXT),
                TextNode("code block", TextType.CODE),
                TextNode(" and an ", TextType.TEXT),
                TextNode("obi wan image", TextType.IMAGE, "https://i.imgur.com/fJRm4Vk.jpeg"),
                TextNode(" and a ", TextType.TEXT),
                TextNode("link", TextType.LINK, "https://boot.dev"),  
            ],
            new_nodes
        )
    def test_markdown_to_blocks(self):
        md = """
This is **bolded** paragraph

This is another paragraph with _italic_ text and `code` here
This is the same paragraph on a new line

- This is a list
- with items
"""
        blocks = markdown_to_blocks(md)
        self.assertEqual(
            blocks,
            [
                "This is **bolded** paragraph",
                "This is another paragraph with _italic_ text and `code` here\nThis is the same paragraph on a new line",
                "- This is a list\n- with items",
            ],
        )

    def test_block_to_block_type_paragraph(self):
        block = "This is just a normal ass paragraph, nothing to really see here"
        self.assertEqual(
            block_to_block_type(block),
            BlockType.PARAGRAPH
        )
    def test_block_to_block_type_heading(self):
        for i in range(1, 7):
            block = f"{'#' * i} This is heading level {i}"
            self.assertEqual(block_to_block_type(block), BlockType.HEADING)
    def test_block_to_block_type_code(self):
        block = "```\nThis is a code block\n```"
        self.assertEqual(
            block_to_block_type(block),
            BlockType.CODE
        )
    def test_block_to_block_type_quote(self):
        block = "> This is a quote!\n> And so is this!\n> Yeehaw!"
        self.assertEqual(
            block_to_block_type(block),
            BlockType.QUOTE
        )
    def test_block_to_block_type_UL(self):
        block = "- Go to store\n- Get some ramen\n- Go home\n- Eat Ramen."
        self.assertEqual(
            block_to_block_type(block),
            BlockType.UNORDERED_LIST
        )
    def test_block_to_block_type_OL(self):
        block = "1. Now we ordering lists\n2. And they ordered as fuck\n3. Turbo ordered"
        self.assertEqual(
            block_to_block_type(block),
            BlockType.ORDERED_LIST
        )
    def test_block_to_block_type_OL_wrong(self):
            block = "1. Now we ordering lists\n3. And they ordered as fuck\n5. Turbo ordered"
            self.assertNotEqual(
                block_to_block_type(block),
                BlockType.ORDERED_LIST
            )

    def test_paragraphs(self):
        md = """
This is **bolded** paragraph
text in a p
tag here

This is another paragraph with _italic_ text and `code` here

"""

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><p>This is <b>bolded</b> paragraph text in a p tag here</p><p>This is another paragraph with <i>italic</i> text and <code>code</code> here</p></div>",
        )

    def test_codeblock(self):
        md = """
```
This is text that _should_ remain
the **same** even with inline stuff
```
"""

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><pre><code>This is text that _should_ remain\nthe **same** even with inline stuff\n</code></pre></div>",
        )

    def test_heading(self):
        md = "### This is a heading!"

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><h3>This is a heading!</h3></div>",
        )

    def test_quotes(self):
        md = "> This is a quote\n> that spans two lines"

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><blockquote>This is a quote that spans two lines</blockquote></div>"
        )

    def test_UL(self):
        md = "- item one\n- item two"

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><ul><li>item one</li><li>item two</li></ul></div>"
        )

    def test_OL(self):
        md = "1. item one\n2. item two\n3. item three"

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><ol><li>item one</li><li>item two</li><li>item three</li></ol></div>"
        )

    def test_extract_title(self):
        md = "# Hello World!  "
        mmd = "Yellow and red\nAnd Purple\n##and Blue\n# Hello World! "
        title = extract_title(md)
        sneaky_title = extract_title(mmd)
        self.assertEqual(
            title,
            "Hello World!"
        )
        self.assertEqual(
            sneaky_title,
            "Hello World!"
        )

    def test_extract_title_Error(self):
        md = "Yellow and red\nAnd Purple\n##and Blue"
        mmd = ""
        with self.assertRaises(Exception):
            extract_title(md)
        with self.assertRaises(Exception):
            extract_title(mmd)

if __name__ == "__main__":
    unittest.main()