import configparser
from stake import params

@params.string("config_file", short="c", help="Relative path to the config file")
def parser(config_file, **__):
    "Parses a config file returning values preceded by their namespace"
    config_parser = configparser.ConfigParser()
    config_parser.read(config_file)

    extracted_values = {}
    for section in config_parser.sections():
        for option, value in config_parser.items(section):
            if section == "Base":
                extracted_values[option] = value
            else:
                extracted_values["%s:%s" % (section.lower(), option)] = value
    return extracted_values
