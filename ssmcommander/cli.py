import click
from ssmcommander.tree import Tree
from ssmcommander.yaml_parser import InputFile
from ssmcommander import CommanderSession
import logging
import boto3

log = logging.getLogger()


def get_session(region=None, ssm_override_url=None, kms_override_url=None):
    overrides = {}
    if ssm_override_url:
        overrides["ssm"] = ssm_override_url
    if kms_override_url:
        overrides["kms"] = kms_override_url

    return CommanderSession(region_name=region, endpoint_overrides=overrides)


@click.group()
@click.option('--debug', prompt=False, is_flag=True)
def cli(debug):
    if debug:
        log.setLevel(logging.DEBUG)

        handler = logging.StreamHandler()
        handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        log.addHandler(handler)

        log.debug("debug logging on")
    pass


@click.command()
@click.option('--region', prompt=False)
@click.option('--ssm-override-url', prompt=False)
@click.argument('ssm_prefix')
def dump(region, ssm_prefix, ssm_override_url=None):
    """Dump the values in ssm to a param file, for backup or inspection.  Suitable for sending in to the write command"""
    session = get_session(region, ssm_override_url=ssm_override_url)
    tree = Tree(ssm_prefix, session)
    tree.fetch_from_ssm(with_decryption=True)
    tree.dump()


@click.command("tree")
@click.option('--ssm-override-url', prompt=False)
@click.option('--region', prompt=False)
@click.argument('ssm_prefix')
def tree_func(region, ssm_prefix, ssm_override_url=None):
    """Print out a tree of your SSM parameters"""
    session = get_session(region, ssm_override_url=ssm_override_url)
    tree = Tree(ssm_prefix, session)
    tree.fetch_from_ssm()
    tree.echo()


@click.command()
@click.option('--region', prompt=False)
@click.option('--ssm-override-url', prompt=False)
@click.option('--kms-override-url', prompt=False)
@click.option('--overwrite/--no-overwrite', default=False, prompt=False)
@click.argument('ssm_prefix')
@click.argument('file')
def write(region, ssm_prefix, file, overwrite, ssm_override_url=None, kms_override_url=None):
    """take a yaml file, put it in to SSM"""
    parsed_file = InputFile(file)
    session = get_session(region, ssm_override_url=ssm_override_url, kms_override_url=kms_override_url)
    parsed_file.write_to_ssm(session, ssm_prefix, overwrite=overwrite)


cli.add_command(dump)
cli.add_command(tree_func)
cli.add_command(write)

if __name__ == "__main__":
    cli()
