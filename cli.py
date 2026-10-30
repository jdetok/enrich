import argparse

def parse_cli_args(prog_name: str, prog_desc: str, args_conf: dict) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog=prog_name, description=prog_desc)
    for key, conf in args_conf.items():
        conf = dict(conf)
        parser.add_argument(f'-{key}', f'--{conf.pop('long')}', **conf)
    return parser.parse_args()

ID_TYPES = {
    'bid': 'Banner ID',
    'pidm': 'PIDM',
    'ssn': 'SSN',
}

CLI_ARGS = {
    'd': {'long': 'dry', 'action': 'store_true', 'help': 'execute a dry run'},
    'n': {
        'long': 'id-column', 'default': 'bid', 
        'help': 'the ID type in the existing file to join to'
    },
    'f': {
        'long': 'file-in', 'default': 'test.csv', 
        'help': 'the ID type in the existing file to join to'
    },
    'i': {
        'long': 'id-in', 'default': 'bid', 'choices': list(ID_TYPES),
        'help': 'the ID type in the existing file to join to'
    },
    'o': {
        'long': 'id-out', 'default': 'ssn', 'metavar': f"[{','.join(ID_TYPES)}]",
        'help': f"options: {', '.join(f'{k}={v}' for k, v in ID_TYPES.items())}"
    },
    'q': {
        'long': 'query', 'default': 'current', 'choices': ['all', 'current'], 
        'help': 'choose which database query to use: all of spriden or current students'
    },
    'j': {
        'long': 'join-type', 'default': 'left', 'choices': ['left', 'inner'], 
        'help': 'join type: preserve all rows from file or only write joined rows'
    },
    'l': {
        'long': 'little', 'nargs': '?', 'type': int, 'const': 100, 'default': None, 'metavar': 'N', 
        'help': 'add `fetch first n rows only` to the database query. -l as flag for default amount or -l n for n rows'
    },
    'c': {
        'long': 'save-csv', 'action': 'store_true', 
        'help': 'save output file as CSV regardless of input type'
    },
    'x': {
        'long': 'save-xl', 'action': 'store_true', 
        'help': 'save output file as Excel regardless of input type'
    },
    'z': {
        'long': 'db-batch-size', 'default': 30_000, 'type': int, 
        'help': 'set the batch array size for the oracledb driver'
    },
}
