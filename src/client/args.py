import argparse

# Default values for named arguments and flags
default_values = {
    'ip': None, # Automatically tries the public ip if not given
    'port': 1000,
    'no_auto_convert': False,
    "no_debug": False
}

# Create the parser
parser = argparse.ArgumentParser(description='ARG Module')

# Dynamically add arguments based on the default values
for arg, default in default_values.items():
    if isinstance(default, bool):
        # It's a flag, use store_true action
        parser.add_argument(f'-{arg}', action='store_true', help=f'A flag argument for {arg}')
    else:
        # It's a named argument with a default value
        parser.add_argument(f'-{arg}', type=type(default), default=default, help=f'A named argument for {arg}')

# Parse the arguments
args = parser.parse_args()

# Update default values with any provided command-line arguments
args = {arg: getattr(args, arg) for arg in default_values}

if __name__ == "__main__":
    print('Updated Values:', args)
