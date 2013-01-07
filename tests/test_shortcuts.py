def test_render():
    """Test the render shortcut."""
    from coffin.shortcuts import render
    response = render(None, 'render-x.html', {'x': 'foo'})
    assert response.content == 'foo'
