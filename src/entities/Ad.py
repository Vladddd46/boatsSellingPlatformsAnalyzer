class Ad:
    def __init__(
        self,
        name,
        currency,
        price,
        favorites_count,
        year_built,
        ad_date,
        views,
        other=None,
    ):
        self.name = name
        self.currency = currency
        self.price = price
        self.favorites_count = favorites_count
        self.year_built = year_built
        self.ad_date = ad_date
        self.views = views
        self.other = other

    def __repr__(self):
        return (
            f"Ad(name={self.name}, currency={self.currency}, "
            f"price={self.price if self.price != -1 else "Price on Request"}, favorites_count={self.favorites_count}, "
            f"year_built={self.year_built}, ad_date={self.ad_date}, views={self.views}, "
            f"other={self.other})"
        )

    def to_json(self):
        return {
            "name": self.name,
            "currency": self.currency,
            "price": self.price if self.price != -1 else "Price on Request",
            "favorites_count": self.favorites_count,
            "year_built": self.year_built,
            "ad_date": self.ad_date,
            "views": self.views,
            "other": self.other,
        }
