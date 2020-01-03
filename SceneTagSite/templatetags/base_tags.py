from django import template

register = template.Library()


@register.inclusion_tag('SceneTagSite/nav_bar.html', takes_context=True)
def nav_bar(context):
    try:
        return {
            'user': context['user'],
            'video': context['video'],
        }
    except KeyError:
        return {
            'user': context['user']
        }


@register.filter
def index(List, i):
    return List[int(i)]


@register.inclusion_tag('SceneTagSite/util_image_ajax.html')
def util_get_image():
    return
