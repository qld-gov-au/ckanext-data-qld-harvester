# encoding: utf-8

# based on facet_list.html functionality
# {% set label = label_function(item) if label_function else item.display_name %}
# {% set label_truncated = h.truncate(label, 22) if not label_function else label %}
def custom_label_function(facet_item):
    if facet_item.name  == 'dataset':
        label ='data.qld.gov.au'
    elif facet_item.name  == 'geoscience':
        label ='geoscience.data.qld.gov.au'
    else:
        label = facet_item.display_name
    return  label