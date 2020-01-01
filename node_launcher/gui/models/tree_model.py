from typing import List, Any

from PySide2.QtCore import QAbstractItemModel, QModelIndex, Qt

from node_launcher.gui.models.tree_item import TreeItem


class TreeModel(QAbstractItemModel):
    def __init__(self, columns: int, headers: List[str], data: List[Any],
                 parent=None):
        super().__init__(parent)

        self.treeView = parent
        self.headers = headers
        self.columns = columns
        self.root = TreeItem(headers)
        self.setupModelData(data, self.root)

    def columnCount(self, parent: QModelIndex = None) -> int:
        return self.columns

    def insertRow(self, row, parent):
        return self.insertRows(row, 1, parent)

    def insertRows(self, row, count, parent):
        self.beginInsertRows(parent, row, (row + (count - 1)))
        self.endInsertRows()
        return True

    def removeRow(self, row, parentIndex):
        return self.removeRows(row, 1, parentIndex)

    def removeRows(self, row, count, parentIndex):
        self.beginRemoveRows(parentIndex, row, row)
        node = self.nodeFromIndex(parentIndex)
        node.removeChild(row)
        self.endRemoveRows()
        return True

    def index(self, row: int, column: int, parent: QModelIndex = None):
        node = self.nodeFromIndex(parent)
        return self.createIndex(row, column, node.childAtRow(row))

    def data(self, index: QModelIndex, role: int = None):
        if role == Qt.DecorationRole:
            return str()

        if role == Qt.TextAlignmentRole:
            return Qt.AlignTop | Qt.AlignLeft

        if role != Qt.DisplayRole:
            return str()

        node = self.nodeFromIndex(index)

        if index.column() == 0:
            return str(node.name)

        elif index.column() == 1:
            return str(node.state)

        elif index.column() == 2:
            return str(node.description)
        else:
            return str()

    def rowCount(self, parent: QModelIndex = None) -> int:
        node = self.nodeFromIndex(parent)
        if node is None:
            return 0
        return len(node)

    def parent(self, child):
        if not child.isValid():
            return QModelIndex()

        node = self.nodeFromIndex(child)

        if node is None:
            return QModelIndex()

        parent = node.parent

        if parent is None:
            return QModelIndex()

        grandparent = parent.parent
        if grandparent is None:
            return QModelIndex()
        row = grandparent.rowOfChild(parent)

        assert row != - 1
        return self.createIndex(row, 0, parent)

    def nodeFromIndex(self, index):
        return index.internalPointer() if index.isValid() else self.root
