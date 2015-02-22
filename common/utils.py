from django.http import QueryDict


def querydict_from_dict(input_dict):
    querydict = QueryDict('', mutable=True)
    querydict.update(input_dict)
    return querydict
