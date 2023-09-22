# WEB-XML-PARSER
Java web.xml parser to display open/closed/restricted routes.

USAGE:
python3 main.py -h
usage: main.py [-h] [-o] [-c] [-r] [-R ROLE] filename

positional arguments:
  filename              web.xml filename

options:
  -h, --help            show this help message and exit
  -o, --open            Show open routes.
  -c, --constrained     Show constrained routes.
  -r, --roles           Show roles.
  -R ROLE, --role ROLE  Show constrained rotes, accessible by role.