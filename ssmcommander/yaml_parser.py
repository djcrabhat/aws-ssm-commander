from click import open_file, secho
import yaml
import treelib
import logging

log = logging.getLogger()

# TODO: understand this loader nonsense better
loader = yaml.SafeLoader


def kms_ctor(loader, node):
    # TODO: parse kms
    return node.value


yaml.add_constructor(u'!kms', kms_ctor, yaml.SafeLoader)


class InputFile:
    def __init__(self, file):

        with open_file(file) as f:
            self.raw_data = yaml.load(f, loader)

        self.build_config_tree()

    def build_config_tree(self):
        self.input_tree = treelib.Tree()
        self.input_tree.create_node("{root}", "{root}")
        self._build_tree(self.input_tree, self.raw_data, "{root}")

    def _build_tree(self, tree, data, parent):
        if isinstance(data, dict):
            for key, value in data.items():
                if parent:
                    key_id = "/".join([parent, key])
                else:
                    key_id = key

                if isinstance(value, str):
                    tree.create_node(key, key_id, parent=parent, data=value)
                else:
                    tree.create_node(key, key_id, parent=parent)
                    self._build_tree(tree, value, key_id)

    def write_to_ssm(self, session, prefix, show=True, overwrite=False):
        if show:
            self.input_tree.show()

        if prefix[0] != "/":
            prefix = "/" + prefix
        if prefix[-1] == "/":
            prefix = prefix[:-1]

        param_count = 0
        leaves = self.input_tree.leaves()

        client = session.client('ssm')
        for leaf in leaves:
            ssm_path = leaf.identifier.format(root=prefix)
            try:
                key_id = None
                description = None
                if isinstance(leaf.data, str):
                    value = leaf.data
                    type = 'String'
                elif isinstance(leaf.data, dict):
                    value = leaf.data['value']
                    key_id = leaf.data['kms_key_id']
                    type = 'SecureString'
                elif isinstance(leaf.data, list):
                    value = ",".join(leaf.data)
                    type = 'StringList'
                else:
                    raise ValueError("{} was not a string, list or dictionary, {}".format(ssm_path, leaf.data))
                params = dict(Name=ssm_path,
                              Value=value,
                              Type=type,
                              Overwrite=overwrite)
                if key_id:
                    params['KeyId'] = key_id
                if description:
                    params['Description'] = description

                log.debug("writing to {}".format(ssm_path))
                response = client.put_parameter(**params)
                param_count += 1
            except Exception as ex:
                log.exception("error witting to ssm")
                secho("cannot write to SSM: {}".format(ex), fg='red')

        secho("Wrote {} params to SSM on path {}".format(param_count, prefix))
