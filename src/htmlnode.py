class HTMLNode:
    def __init__(self, tag=None, value=None, children=None, props=None):
        self.tag = tag
        self.value = value
        self.children = children
        self.props = props

    def to_html(self):
        raise NotImplementedError
    def props_to_html(self):
        if self.props != None:
            html_props = []
            for key, value in self.props.items():
                prop = f' {key}="{value}"'
                html_props.append(prop)
            return "".join(html_props)
        else:
            return ""
        
    def __repr__(self):
        return f"HTMLNode({self.tag}, {self.value}, {self.children}, {self.props})"
    

class LeafNode(HTMLNode):
    def __init__(self, tag, value, props=None):
        super().__init__(tag, value, None, props)
    def to_html(self):
        if self.value is None:
            raise ValueError
        if self.tag is None:
            return self.value
        else:
            attributes = self.props_to_html()
            return f'<{self.tag}{attributes}>{self.value}</{self.tag}>'
    def __repr__(self):
        return f"LeafNode({self.tag}, {self.value}, {self.props})"
    
class ParentNode(HTMLNode):
    def __init__(self, tag, children, props=None):
        super().__init__(tag, None, children, props)
    def to_html(self):
        if self.tag is None:
            raise ValueError("Node has no tag.")
        if self.children is None:
            raise ValueError("Node has no children.")
        string = ""
        attributes = self.props_to_html()
        for child in self.children:
            string += child.to_html()
        return f'<{self.tag}{attributes}>{string}</{self.tag}>'


