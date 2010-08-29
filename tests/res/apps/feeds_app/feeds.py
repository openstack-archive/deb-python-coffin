from coffin.contrib.syndication.feeds import Feed as OldFeed


class TestOldFeed(OldFeed):
    title = 'Foo'
    link = '/'

    def items(self):
        return [1,2,3]

    def item_link(self, item):
        return '/item'

    title_template = 'feeds_app/feed_title.html'
    description_template = 'feeds_app/feed_description.html'


try:
    from coffin.contrib.syndication.views import Feed as NewFeed
except ImportError:
    pass
else:
    class TestNewFeed(NewFeed):
        title = 'Foo'
        link = '/'

        def items(self):
            return [1,2,3]

        def item_link(self, item):
            return '/item'

        title_template = 'feeds_app/feed_title.html'
        description_template = 'feeds_app/feed_description.html'