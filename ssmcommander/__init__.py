import boto3


class CommanderSession:
    def __init__(self, endpoint_overrides=None, region_name=None):
        self.endpoint_override = {}
        if endpoint_overrides:
            self.endpoint_override.update(endpoint_overrides)
        params = {}
        if region_name:
            params["region_name"] = region_name

        self.session = boto3.Session(**params)

    def client(self, service, **kwargs):
        params = {}
        if service in self.endpoint_override:
            params["endpoint_url"] = self.endpoint_override[service]

        if kwargs:
            params.update(kwargs)

        client = self.session.client("ssm", **params)
        return client
