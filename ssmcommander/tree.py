import boto3
from click import echo
import treelib
import yaml

path_separator = '/'
secure_string_identifier = '[*]'


class Tree:
    def __init__(self, prefix, session):
        self.session = session

        if prefix[0] != "/":
            prefix = "/" + prefix
        self.prefix = prefix
        self.tree = treelib.Tree()

    def get_tree_from_path(self, path=None):
        path = path.split(path_separator)
        node_list = []
        for index, node in enumerate(path):
            if node:
                node_id = "/".join(path[0:index + 1])
                node_list.append({'node': node, 'id': node_id})
        for index, node in enumerate(path):
            if index == 1:
                node_list[index - 1]['parent'] = None
            else:
                node_list[index - 1]['parent'] = node_list[index - 2]['id']
        return node_list

    def fetch_from_ssm(self, with_decryption=False):
        client = self.session.client("ssm")
        paginator = client.get_paginator('get_parameters_by_path')
        pages = paginator.paginate(
            Path=self.prefix,
            Recursive=True,
            WithDecryption=with_decryption
        )
        ssm_params = []
        for page in pages:
            parameters_page = [{"name": entry['Name'],
                                "type": entry['Type'],
                                "value": entry['Value'],
                                "version": entry['Version']} for entry in page['Parameters']]
            ssm_params.extend(parameters_page)

        # build the tree from the params
        for item in ssm_params:
            for node in self.get_tree_from_path(item['name']):
                try:
                    self.tree.create_node(node['node'], node['id'], parent=node['parent'], data=item)
                except:
                    pass

    def echo(self):
        self.tree.show()

    def dump(self):
        prefix_id = self.prefix[:]
        if prefix_id[-1] == "/":
            prefix_id = prefix_id[:-1]

        # find node of prefix
        root_tree = self.tree.subtree(prefix_id)

        data = {}
        for node in root_tree.leaves():
            parts = node.identifier[len(prefix_id):].split("/")[1:]

            pointer = data
            index = 0
            for p in parts:
                if p not in pointer:
                    pointer[p] = {}

                if index == len(parts) - 1:
                    pointer[p] = node.data['value']
                else:
                    pointer = pointer[p]
                index += 1

        print(yaml.dump(data))
