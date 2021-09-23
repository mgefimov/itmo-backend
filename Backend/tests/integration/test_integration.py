from ...items import read_item, DiscountItem


def test_apply_discount():
    item = read_item(123)
    discount_item = DiscountItem(**item.dict(), username='test')
    assert discount_item.is_valid()
    discount_item.apply_discount()
    assert discount_item.price == 80.0


def test_read_unknown_item():
    item = read_item(666)
    assert item is None


def test_invalid_item():
    item = read_item(124)
    item.price -= 1000
    discount_item = DiscountItem(**item.dict(), username='test')
    assert discount_item.is_valid() is False
