from coffin.contrib.syndication.feeds import Feed


class TestFeed(Feed):
    title = 'Foo'
    link = '/'

    def items(self):
        return [1,2,3]

    def item_link(self, item):
        return '/item'

    title_template = 'feeds_app/feed_title.html'
    description_template = 'feeds_app/feed_description.html'