class AdsStatistics:
    def __init__(
        self,
        total_ads,
        total_views,
        average_views,
        oldest_date,
        newest_date,
        ads_with_no_date,
        min_year_built,
        max_year_built,
        average_price_per_currency,
        min_price_for_each_currency,
        max_price_for_each_currency,
        currency_usage_count,
        favorites_sum,
        num_of_ads_by_day,
        average_ads_by_day,
    ):
        self.total_ads = total_ads
        self.total_views = total_views
        self.average_views = average_views
        self.oldest_date = oldest_date
        self.newest_date = newest_date
        self.ads_with_no_date = ads_with_no_date
        self.min_year_built = min_year_built
        self.max_year_built = max_year_built
        self.average_price_per_currency = average_price_per_currency
        self.min_price_for_each_currency = min_price_for_each_currency
        self.max_price_for_each_currency = max_price_for_each_currency
        self.currency_usage_count = currency_usage_count
        self.favorites_sum = favorites_sum
        self.num_of_ads_by_day = num_of_ads_by_day
        self.average_ads_by_day = average_ads_by_day

    def __str__(self):
        return (
            f"\nAds Statistics:\n"
            f"Total Ads: {self.total_ads}\n"
            f"Total Views: {self.total_views}\n"
            f"Average Views: {self.average_views}\n"
            f"Oldest Ad Date: {self.oldest_date}\n"
            f"Newest Ad Date: {self.newest_date}\n"
            f"Ads with No Date: {self.ads_with_no_date}\n"
            f"Min Year Built: {self.min_year_built}\n"
            f"Max Year Built: {self.max_year_built}\n"
            f"Average Price per Currency: {self.average_price_per_currency}\n"
            f"Min Price per Currency: {self.min_price_for_each_currency}\n"
            f"Max Price per Currency: {self.max_price_for_each_currency}\n"
            f"Currency Usage Count: {self.currency_usage_count}\n"
            f"Favorites Sum: {self.favorites_sum}\n"
            f"Number of Ads by Day: {self.num_of_ads_by_day}\n"
            f"Average ads by day: {self.average_ads_by_day}\n"
        )

    def __repr__(self):
        return (
            f"AdsStatistics(total_ads={self.total_ads}, total_views={self.total_views}, average_views={self.average_views}, "
            f"oldest_date='{self.oldest_date}', newest_date='{self.newest_date}', ads_with_no_date={self.ads_with_no_date}, "
            f"min_year_built={self.min_year_built}, max_year_built={self.max_year_built}, "
            f"average_price_per_currency={self.average_price_per_currency}, min_price_for_each_currency={self.min_price_for_each_currency}, "
            f"max_price_for_each_currency={self.max_price_for_each_currency}, currency_usage_count={self.currency_usage_count}, "
            f"favorites_sum={self.favorites_sum}, num_of_ads_by_day={self.num_of_ads_by_day}, average_ads_by_day={self.average_ads_by_day})"
        )
