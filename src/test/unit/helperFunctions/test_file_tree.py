import unittest
import pytest
from helperFunctions.file_tree import FileTreeNode, get_partial_virtual_path, get_correct_icon_for_mime


@pytest.mark.parametrize('mime_type, icon', [
    ('application/zip', '/static/file_icons/archive.png'),
    ('filesystem/some_filesystem', '/static/file_icons/filesystem.png'),
    ('application/x-executable', '/static/file_icons/binary.png'),
    ('inode/symlink', '/static/file_icons/link.png'),
    ('text/html', '/static/file_icons/html.png'),
    ('firmware/generic', '/static/file_icons/firmware.png'),
    ('text/plain', '/static/file_icons/text.png'),
    ('image/png', '/static/file_icons/image.png'),
    ('audio/mpeg', '/static/file_icons/multimedia.png'),
    ('some unknown mime type', '/static/file_icons/unknown.png')
])
def test_get_correct_icon_for_mime(mime_type, icon):
    assert get_correct_icon_for_mime(mime_type) == icon


class TestFileTree(unittest.TestCase):
    def test_node_creation(self):
        parent_node = FileTreeNode('123', virtual=False, name='parent', size=1, mime_type='somefile')
        child_node = FileTreeNode('456', root_uid='123', virtual=True, name='child')
        parent_node.add_child_node(child_node)

        self.assertEqual(parent_node.uid, '123')
        self.assertEqual(parent_node.root_uid, None)
        self.assertEqual(child_node.root_uid, '123')
        self.assertFalse(parent_node.virtual)
        self.assertEqual(parent_node.size, 1)
        self.assertEqual(parent_node.type, 'somefile')
        self.assertTrue(parent_node.has_children)
        self.assertEqual(parent_node.get_list_of_child_nodes(), [child_node])
        self.assertEqual(parent_node.get_id(), ('parent', False))
        self.assertEqual(list(parent_node.children.keys()), [child_node.get_id()])
        self.assertEqual(parent_node.get_names_of_children(), [child_node.name])
        self.assertFalse(child_node.has_children)
        self.assertTrue(child_node in parent_node)
        assert 'Node ' in parent_node.__repr__()
        self.assertNotEqual(parent_node, child_node)
        assert parent_node.print_tree() is None

    def test_node_merging(self):
        parent_node = FileTreeNode('123', virtual=False, name='parent', size=1, mime_type='somefile')
        child_node_folder_1 = FileTreeNode(None, virtual=True, name='folder')
        child_node_folder_2 = FileTreeNode(None, virtual=True, name='folder')
        child_node_file_1 = FileTreeNode('abc', virtual=False, name='file_1')
        child_node_file_2 = FileTreeNode('def', virtual=False, name='file_2')
        child_node_folder_1.add_child_node(child_node_file_1)
        child_node_folder_2.add_child_node(child_node_file_2)
        parent_node.add_child_node(child_node_folder_1)
        parent_node.add_child_node(child_node_folder_2)

        self.assertTrue(parent_node.has_children)
        self.assertEqual(len(parent_node.get_list_of_child_nodes()), 1)
        self.assertEqual(list(parent_node.children.keys()), [child_node_folder_1.get_id()])
        self.assertTrue(child_node_folder_1 in parent_node)
        self.assertTrue(child_node_folder_2 in parent_node)
        self.assertEqual(len(parent_node.children[child_node_folder_1.get_id()].get_list_of_child_nodes()), 2)
        folder_id = child_node_folder_1.get_id()
        self.assertTrue(child_node_file_1 in parent_node.children[folder_id])
        self.assertTrue(child_node_file_2 in parent_node.children[folder_id])

    def test_get_partial_virtual_path(self):
        virtual_path = {'abc': ['|abc|def|ghi|folder_1/folder_2/file']}

        self.assertEqual(get_partial_virtual_path(virtual_path, 'abc'),
                         {'abc': ['|abc|def|ghi|folder_1/folder_2/file']})
        self.assertEqual(get_partial_virtual_path(virtual_path, 'ghi'),
                         {'ghi': ['|ghi|folder_1/folder_2/file']})
        self.assertEqual(get_partial_virtual_path(virtual_path, 'xyz'),
                         {'xyz': ['|xyz|']})
