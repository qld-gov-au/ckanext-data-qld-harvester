# encoding: utf-8

# based on facet_list.html functionality
# {% set label = label_function(item) if label_function else item.display_name %}
def custom_label_function(facet_field, facet_item):
    if facet_field == 'dataset_type':
        if facet_item['name'] == 'dataset':
            return 'data.qld.gov.au'
        elif facet_item['name'] == 'geoscience':
            return 'geoscience.data.qld.gov.au'

    return facet_item['display_name']


# based on
# @core_helper
# def list_dict_filter(list_, search_field, output_field, value):
def custom_label_function_list_dict_filter(list_, facet_field, search_field, output_field, value):
    ''' Takes a list of dicts and returns the value of a given key if the
    item has a matching value for a supplied key

    :param list_: the list to search through for matching items
    :type list_: list of dicts

    :param facet_field: the field key which was used to find nice title
    :type string

    :param search_field: the key to use to find matching items
    :type search_field: string

    :param output_field: the key to use to output the value
    :type output_field: string

    :param value: the value to search for
    '''

    if facet_field == 'dataset_type':
        if value == 'dataset':
            return 'data.qld.gov.au'
        elif value == 'geoscience':
            return 'geoscience.data.qld.gov.au'

    for item in list_:
        if item.get(search_field) == value:
            return item.get(output_field, value)
    return value
