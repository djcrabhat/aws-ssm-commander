# aws-ssm-commander

Inspired by [aws-ssm-tree](https://github.com/brunorubin/aws-ssm-tree)

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
