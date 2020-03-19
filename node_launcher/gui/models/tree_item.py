from typing import List, Any


class TreeItem(object):
    def __init__(self, data: List[Any], parent=None):
        self.data = data
        self.parent = parent
        self.children = []

        self.setParent(parent)

    def setParent(self, parent):
        if parent is not None:
            self.parent = parent
            self.parent.appendChild(self)
        else:
            self.parent = None

    def appendChild(self, child):
        self.children.append(child)

    def childAtRow(self, row: int):
        return self.children[row]

    def rowOfChild(self, child):
        for i, item in enumerate(self.children):
            if item == child:
                return i
        return -1

    def child_count(self):
        return len(self.children)

    def removeChild(self, row):
        value = self.children[row]
        self.children.remove(value)
        return True

    def column_count(self):
        return len(self.data)

    def data(self, column: int):
        return self.data[column]

    def row(self):
        if self.parent is not None:
            return self.parent.children.index(self)
        return 0

    def __len__(self):
        return len(self.children)

