import xmltodict
import re
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("filename", help="web.xml filename")
parser.add_argument("-o", '--open', help="Show open routes.", action='store_true')
parser.add_argument("-c", "--constrained", help="Show constrained routes.", action='store_true')
parser.add_argument("-r", "--roles", help="Show roles.", action='store_true')
parser.add_argument("-R", "--role", help="Show constrained rotes, accessible by role.")
args = parser.parse_args()


def get_urls(main_node):
    res = {}
    if 'servlet-mapping' in main_node:
        for servlet_mapping in main_node['servlet-mapping']:
            if servlet_mapping['servlet-name'] in res:
                res[servlet_mapping['url-pattern']].append([servlet_mapping['servlet-name']])
            else:
                res[servlet_mapping['url-pattern']] = [servlet_mapping['servlet-name']]

    return res


def check_in_list_url(url, constrained_urls):
    if url in constrained_urls:
        return True

    # wildcard
    for constrained_url in constrained_urls:
        if '*' in constrained_url:
            pattern = re.escape(constrained_url).replace('\*', '.*')
            pattern = re.sub('^', '^', pattern)

            if re.search(pattern, url):
                return True
    return False


def get_open_urls(main_node):
    res = {}
    urls = get_urls(main_node)
    constrained_urls = get_constrained_urls(main_node)

    for key, value in urls.items():
        if check_in_list_url(key, constrained_urls):
            continue

        res[key] = value

    return res


def get_constrains(main_node):
    constraints = []
    if 'security-constraint' in main_node:
        for constraint in main_node['security-constraint']:
            constraints.append(constraint)
    return constraints


def get_constrained_urls(main_node):
    constraints = get_constrains(main_node)

    res = {}
    if len(constraints):
        for constraint in constraints:
            urls = None
            auth_constraint = None
            auth_roles = None
            resource_name = None

            if 'auth-constraint' in constraint:
                auth_constraint = constraint['auth-constraint']
                if isinstance(constraint['auth-constraint']['role-name'], list):
                    auth_roles = constraint['auth-constraint']['role-name']
                else:
                    auth_roles = [constraint['auth-constraint']['role-name']]

            if 'web-resource-collection' in constraint:
                if 'url-pattern' in constraint['web-resource-collection']:
                    if isinstance(constraint['web-resource-collection']['url-pattern'], list):
                        urls = constraint['web-resource-collection']['url-pattern']
                    else:
                        urls = [constraint['web-resource-collection']['url-pattern']]

                    for url in urls:
                        if url in res:
                            res[url] = list(set(res[url] + auth_roles))
                        else:
                            res[url] = auth_roles
        return res


def get_roles(main_node):
    roles = set()
    for key, value in get_constrained_urls(main_node).items():
        roles = set(list(roles) + value)

    return roles


def get_open_urls_by_role(role):
    res = {}
    for key, value in get_constrained_urls(main_node).items():
        if role in value or '*' in value:
            res[key] = value
    return res


########

main_node_name = 'web-app'
filename = args.filename

with open(filename, 'r', encoding='utf-8') as file:
    my_xml = file.read()
my_dict = xmltodict.parse(my_xml)

if main_node_name in my_dict:
    main_node = my_dict[main_node_name]
else:
    print(f'Node {main_node_name} not found.')
    exit()

if args.open:
    urls = get_open_urls(main_node)
    for key in sorted(urls):
        servlets = ', '.join(urls[key])
        print(f'{key}\t{servlets}')
elif args.constrained:
    if args.role:
        urls = get_open_urls_by_role(args.role)
    else:
        urls = get_constrained_urls(main_node)

    for key in sorted(urls):
        roles = ', '.join(urls[key])
        print(f'{key}\t{roles}')
elif args.roles:
    for role in sorted(get_roles(main_node)):
        print(role)
