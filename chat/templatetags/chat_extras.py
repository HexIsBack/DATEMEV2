from django import template
register = template.Library()

@register.filter
def get_reactions(reactions_map, msg_id):
    """Usage: {{ reactions_map|get_reactions:msg.id }}"""
    return reactions_map.get(msg_id, [])
