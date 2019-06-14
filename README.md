# aws-ssm-commander

[![Build Status](https://travis-ci.org/djcrabhat/aws-ssm-commander.svg?branch=master)](https://travis-ci.org/djcrabhat/aws-ssm-commander)

Inspired by [aws-ssm-tree](https://github.com/brunorubin/aws-ssm-tree)

## Install
```
pip install aws-ssm-commander
```

## Usage
```
Options:
  --debug
  --help   Show this message and exit.

Commands:
  dump   Dump the values in ssm to a param file, for backup or inspection.
  tree   Print out a tree of your SSM parameters
  write  take a yaml file, put it in to SSM
```

### dump
Dumps the params on a path to a json or yaml output
```
~> aws-ssm-commander dump /abc/123
section_a:
  username: abc123
section_b:
  password: blah
  username: foobar
```
    
### tree
See a visual representation of params on a path.  Useful for making sure your params out in SSM are structured as 
expected
```
~> aws-ssm-commander tree /abc/123/
abc
└── 123
    ├── section_a
    │   └── username
    ├── section_b
    │   ├── password
    │   └── username
```

### write
Takes a yaml input file and a path prefix, and writes params to SSM.

```
~> aws-ssm-commander write /abc/123/ my_file.yml
```

### Saving secrets

There are two ways of saving secrets. First is by supplying a KMS key ID along with the value to encrypt. The second is to use custom KMS to store kms blobs. The former is less secure than the latter.

#### Supplying a KMS key ID along with the value to encrypt
A KMS key ID can be supplied:

password:
  kms_key_id: f0e79e90-5672-431d-b100b-84b8ac8f1525
  value: supersecretpassword

Keep in mind that if the params file is in git, the secret will be exposed in plain text!

#### Using custom KMS keys to store kms blobs in the yaml file
A lot of the stuff you want to put in Param Store are secrets, and you don't store plaintext secrets in git!  Now you could encrypt and decrypt these files on your own, but aws-ssm-commander supports putting a KMS blob in a config file.

You can put a KMS secret in your config files by prefixing a value with a `!kms` tag

To get a kms blob, 
```bash

KEY_ID=1234abcd-12ab-34cd-56ef-1234567890ab
aws kms encrypt --key-id $KEY_ID --plaintext "MY_SECRET" --output text --query CiphertextBlob 
```

take that output, then drop it in a value in a yaml file like so:

```yaml
my_thing:
  username: foobar
  password: !kms WW05aWJHRjNZbXh2WWc9PQ==
```
