import json

def custom_rules():
    with open('CustomRules.json') as f:
        data = json.load(f)
        if data['proxyname_rule']['proxyname_prefix'] == "":
            proxyname_prefix = None
        else:
            proxyname_prefix = data['proxyname_rule']['proxyname_prefix']

        if data['proxyname_rule']['proxyname_postfix'] == "":
            proxyname_postfix = None
        else:
            proxyname_postfix = data['proxyname_rule']['proxyname_postfix']
        if data['method_rule']['method'] == "":
            method = None
        else:
            method = data['method_rule']['method']
        if data['regex_rule']['allowed'] == "":
            allowed = None
        else:
            allowed = data['regex_rule']['allowed']

        return proxyname_prefix, proxyname_postfix, method, allowed
