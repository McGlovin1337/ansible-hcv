"""CLI Module to access HashiCorp Vault for ansible-vault keys"""
import argparse
import os
from pathlib import Path
import pkg_resources
import hvac
import tomli
import urllib3
from fernetstring.fernetstr import FernetString


ANSIBLE_HCV_CONFIG_PATH = Path(Path.joinpath(Path.home(), '.ansible-hcv'))
ANSIBLE_HCV_CONFIG_FILE = 'ansible-hcv-config.toml'
ANSIBLE_HCV_CONFIG = Path.joinpath(ANSIBLE_HCV_CONFIG_PATH, ANSIBLE_HCV_CONFIG_FILE)


def _install_config() -> None:
    """Install a default configuration file"""
    source_cfg = pkg_resources.resource_stream(__name__, 'data/default-config.toml')

    if not Path.exists(ANSIBLE_HCV_CONFIG_PATH):
        Path.mkdir(
            ANSIBLE_HCV_CONFIG_PATH,
            mode=0o700
        )

    os.umask(0)
    descriptor = os.open(
        path=ANSIBLE_HCV_CONFIG,
        flags=(
            os.O_WRONLY
            | os.O_CREAT
            | os.O_TRUNC
        ),
        mode=0o600
    )
    with open(descriptor, 'wb') as config_file:
        config_file.writelines(source_cfg)


def _read_config_file() -> dict:
    """Read the ansible-hcv-config.toml file

    Returns:
        dict: Dictionary of configuration data
    """
    with open(ANSIBLE_HCV_CONFIG, 'rb') as hcv_config_file:
        hcv_config = tomli.load(hcv_config_file)

    return hcv_config


def _set_hcv_token(token: str) -> None:
    """Set the HashiCorp Vault Token used to access HashiCorp Vault

    Args:
        token (str): The HashiCorp Vault Token
    """
    vault_config = _read_config_file()

    encrypted_token = FernetString(token)

    os.umask(0)
    descriptor = os.open(
        path=os.path.expanduser(vault_config['vault']['token_path']),
        flags=(
            os.O_WRONLY
            | os.O_CREAT
            | os.O_TRUNC
        ),
        mode=0o600
    )
    with open(descriptor, 'wb') as token_file:
        token_file.write(encrypted_token.secure_string)


def _fetch_ansible_key(vault_id: str) -> str:
    """Return the ansible key specified by ansible-vault-id

    Args:
        vault_id (str): The ansible-vault-id to lookup

    Returns:
        str: The requested key
    """
    # Read the configuration file
    vault_config = _read_config_file()

    encrypted_token = None

    # Read the encrypted token used to access Hashicorp Vault
    with open(os.path.expanduser(vault_config['vault']['token_path']), 'rb') as token_file:
        encrypted_token = FernetString.from_secure_string(token_file.readline())

    if encrypted_token is None:
        return None

    if not vault_config['vault']['verify_tls']:
        urllib3.disable_warnings()

    # Create Hashicorp Vault Client
    hcv_client = hvac.Client(
        url=vault_config['vault']['uri'],
        token=encrypted_token.decrypt(),
        verify=vault_config['vault']['verify_tls'],
        namespace=vault_config['vault']['namespace'],
        timeout=vault_config['vault']['timeout']
    )

    # Version 1 KV Secrets Engine
    if vault_config['vault']['kv_version'] == 1:
        client_response = hcv_client.secrets.kv.v1.read_secret(
            mount_point=vault_config['vault']['kv_mount'],
            path=vault_id
        )
        return client_response['data'][vault_config['vault']['key_name']]

    # Version 2 KV Secrets Engine (only latest version is read)
    if vault_config['vault']['kv_version'] == 2:
        client_response = hcv_client.secrets.kv.v2.read_secret_version(
            mount_point=vault_config['vault']['kv_mount'],
            path=vault_id,
            raise_on_deleted_version=False
        )
        return client_response['data']['data'][vault_config['vault']['key_name']]


def main():
    """Module main entry"""

    # Argument Parser
    parser = argparse.ArgumentParser(
        prog='ansible-hcv-client',
        description='Store and Retrieve ansible-vault keys using HashiCorp Vault'
    )
    arg_group = parser.add_mutually_exclusive_group(required=True)
    arg_group.add_argument('--vault-id', type=str, help='Specify the ansible-vault-id')
    arg_group.add_argument('--set-token', type=str, help='Set the HashiCorp Vault Token used to authenticate with HashiCorp Vault')
    arg_group.add_argument('--install-config', action='store_true', help=f'Install default configuration file to {ANSIBLE_HCV_CONFIG}')
    args = parser.parse_args()

    if args.install_config:
        _install_config()
        return

    if args.set_token:
        _set_hcv_token(args.set_token)
        return

    if args.vault_id:
        data = _fetch_ansible_key(args.vault_id)
        print(data)
        return


if __name__ == '__main__':
    main()
