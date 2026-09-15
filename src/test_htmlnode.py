import unittest
from htmlnode import HTMLNode, LeafNode, ParentNode


class TestHTMLNode(unittest.TestCase):
    def test_props_to_html(self):
        node = HTMLNode(
            "a",
            "Click here!",
            None,
            {"href": "https://www.google.com"},
        )
        self.assertEqual(
            node.props_to_html(),
            ' href="https://www.google.com"',
        )
    def test_props_None(self):
        node = HTMLNode(
            "a",
            "Click here!",
            None,
            None,
        )
        self.assertEqual(
            node.props_to_html(),
            ''
        )
    def test_multi_props(self):
        node = HTMLNode(
            "a",
            "Click here!",
            None,
            {"href": "https://www.google.com", "target": "_blank"},
        )
        self.assertEqual(
            node.props_to_html(),
            ' href="https://www.google.com" target="_blank"'
        )
    
    def test_empty_node(self):
        node = HTMLNode(
            None,
            None,
            None,
            None,
        )
        self.assertIsNone(node.tag)
        self.assertIsNone(node.value)
        self.assertIsNone(node.children)
        self.assertIsNone(node.props)
    
    def test_leaf_to_html_p(self):
        node = LeafNode("p", "Hello, world!")
        self.assertEqual(node.to_html(), "<p>Hello, world!</p>")
    
    def test_to_html_with_children(self):
        child_node = LeafNode("span", "child")
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(parent_node.to_html(), "<div><span>child</span></div>")


    def test_to_html_with_grandchildren(self):
        grandchild_node = LeafNode("b", "grandchild")
        child_node = ParentNode("span", [grandchild_node])
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(
            parent_node.to_html(),
            "<div><span><b>grandchild</b></span></div>",
        )
    

if __name__ == "__main__":
    unittest.main()