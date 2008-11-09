from jinja2 import Environment


def test_load():
    from coffin.template.defaulttags import LoadExtension
    env = Environment(extensions=[LoadExtension])

    # the load tag is a no-op
    env.from_string('a{% load %}c').render() == 'ab'
    env.from_string('a{% load news.photos %}b').render() == 'ab'
    env.from_string('a{% load "news.photos" %}b').render() == 'ab'