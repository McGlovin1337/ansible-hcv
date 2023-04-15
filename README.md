# Ansible-HCV

Provides an ansible-vault client to return ansible-vault keys from a Hashicorp Vault Version 1 or 2 KV Secrets Engine.

## Usage

### Create Configuration File
The client requires a configuration file to define the Hashicorp Vault settings. This can be installed with the following command:

```shell
ansible-hcv-client --install-config
```

This will install a template configuration file to ~/.anisble-hcv/ansible-hcv-config.toml
Edit this file to define your Hashicorp Vault connection settings.

### Set Hashicorp Vault Token
A Hashicorp Vault token must be provided that will be used to access the configured Secrets Engine, it's recommended that this is a long lived token.
Once a token has been issued you must set it using the following command:

```shell
ansible-hcv-client --set-token token
```

This will write the token to the path specified in the configuration file (default ~/.ansible-hcv/.hcvtoken) in an encrypted format.

### Add ansible-vault vault-id's to Hashicorp Vault
Add your ansible-vault vault-id's to your KV Store. The path format should be MountPoint/VaultId. By default the key to add is named password, but this can be changed in the configuration file. For example:

```shell
vault put secrets/default password=Password123
```

### Use ansible-vault to encrypt using the vault-id in Hashicorp Vault
Use ansible-vault in the usual way to encrypt strings and files, specifying ansible-hcv-client in the --vault-id parameter, e.g.

```shell
ansible-vault encrypt_string --vault-id default@ansible-hcv-client --stdin-name my_secret_var
```

This would encrypt a string for an ansible variable named my_secret_var using the password stored in Hashicorp Vault at the secrets/default path.

### Specify the vault-id in the ansible-playbook
In much the same way as using ansible-vault, specify the ansible-hcv-client in the --vault-id parameter when running a playbook, e.g.

```shell
ansible-playbook --vault-id default@ansible-hcv-client main.yml
```
