from click import open_file, secho
from click.exceptions import BadParameter
import yaml
import treelib
import logging
import boto3
import base64
from botocore.exceptions import ClientError
import binascii

log = logging.getLogger()

# TODO: understand this loader nonsense better
loader = yaml.SafeLoader


class InputFile:
    def __init__(self, file, kms_session=None):
        if kms_session:
            self.kms_session = kms_session
        else:
            self.kms_session = boto3.Session()

        yaml.add_constructor(u'!kms', self.kms_ctor, yaml.SafeLoader)

        with open_file(file) as f:
            self.raw_data = yaml.load(f, loader)

        self.build_config_tree()

    def kms_ctor(self, loader, node):
        try:
            binary_data = base64.b64decode(node.value)

            if self.kms_session is None:
                raise BadParameter("could not establish a KMS session")
            kms = self.kms_session.client('kms')
            meta = kms.decrypt(CiphertextBlob=binary_data)

            unencrypted = meta[u'Plaintext'].decode()
            return unencrypted
        except ClientError as ex:
            secho(ex.response['Error']['Code'])
            raise BadParameter("could not decode !kms value: {}".format(ex))
        except binascii.Error as ex:
            secho("Cannot parse b64 blob: {}".format(ex))
            raise BadParameter("could not decode !kms value: {}".format(ex))

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

                if isinstance(value, str) or isinstance(value, dict):
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
                client.put_parameter(**params)
                param_count += 1
            except Exception as ex:
                log.exception("error witting to ssm")
                secho("cannot write to SSM: {}".format(ex), fg='red')

        secho("Wrote {} params to SSM on path {}".format(param_count, prefix))
