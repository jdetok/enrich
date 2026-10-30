import argparse

def parse_cli_args(prog_name: str, prog_desc: str, args_conf: dict) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog=prog_name, description=prog_desc)
    for key in args_conf:         
        parser.add_argument(
            f'-{key}', 
            f'--{args_conf[key]['long']}', 
            action=args_conf[key]['action'] if 'action' in args_conf[key] else None, 
            default=args_conf[key]['default'] if 'default' in args_conf[key] else None, 
            help=args_conf[key]['help'] if 'help' in args_conf[key] else None
        )
    return parser.parse_args()