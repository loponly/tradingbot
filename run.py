from tradingbot.commands import cli_options

option = cli_options.AVAILABLE_CLI_OPTIONS['hyperopt_show_no_header']

if __name__ == "__main__":
    import argparse
    _common_parser = argparse.ArgumentParser(add_help=False)
    group = _common_parser.add_argument_group("Common arguments")
    group.add_argument(*option.cli)
    #print(*option.cli)
    print(_common_parser.get_default(*option.cli))
