from datetime import datetime, timedelta
from src.utils.utils import convert_strdate_to_date, convert_to_euro
from src.entities.AdsStatistics import AdsStatistics


class StatisticsCalculator:

    def __init__(self):
        self.m_ads = []

    def get_statistics(self, ads):
        self.m_ads = ads

        total_ads = self.__total_number_of_ads()
        total_views = self.__total_views()
        average_views = self.__average_views()
        oldest_date = self.__oldest_ad_date()
        newest_date = self.__newest_ad_date()
        ads_with_no_date = self.__count_ads_with_no_ad_date()
        min_year_built = self.__min_year_built()
        max_year_built = self.__max_year_built()
        average_price_per_currency = self.__average_price_for_each_currency()
        min_price_for_each_currency = self.__min_price_for_each_currency()
        max_price_for_each_currency = self.__max_price_for_each_currency()
        currency_usage_count = self.__currency_usage_count()
        favorites_sum = self.__favorites_sum()
        num_of_ads_by_day = self.__number_of_ads_by_day(oldest_date, newest_date)
        average_ads_by_day = round(
            total_ads
            / (
                convert_strdate_to_date(newest_date)
                - convert_strdate_to_date(oldest_date)
            ).days
        )
        divided_price_by_euro = self.__divide_ads_by_euro_price(10000)
        other = {"price_division": {"over_10000_euro": divided_price_by_euro["over"], "under_10000_euro": divided_price_by_euro["under"]}}

        return AdsStatistics(
            total_ads=total_ads,
            total_views=total_views,
            average_views=average_views,
            oldest_date=oldest_date,
            newest_date=newest_date,
            ads_with_no_date=ads_with_no_date,
            min_year_built=min_year_built,
            max_year_built=max_year_built,
            average_price_per_currency=average_price_per_currency,
            min_price_for_each_currency=min_price_for_each_currency,
            max_price_for_each_currency=max_price_for_each_currency,
            currency_usage_count=currency_usage_count,
            favorites_sum=favorites_sum,
            num_of_ads_by_day=num_of_ads_by_day,
            average_ads_by_day=average_ads_by_day,
            other=other
        )


    def __divide_ads_by_euro_price(self, divide_price):
        res = {"over": 0, "under": 0}
        for i in self.m_ads:
            tmp_price = i.price
            if i.currency != "EUR":
                tmp_price = convert_to_euro(i.currency, i.price)
            if tmp_price >= divide_price:
                res["over"] += 1
            else:
                res["under"] += 1
        return res

    def __get_ads_by_date(self, target_date):
        matched_ads = []

        # Convert target_date to datetime object if it's a string
        if isinstance(target_date, str):
            target_date = convert_strdate_to_date(target_date)

        # Iterate through the list of ads and match by ad_date
        for ad in self.m_ads:
            if ad.ad_date:
                ad_date_obj = convert_strdate_to_date(ad.ad_date)
                if ad_date_obj == target_date:
                    matched_ads.append(ad)

        return matched_ads

    def __number_of_ads_by_day(self, from_date, to_date):
        res = {}
        start_date = convert_strdate_to_date(from_date)
        end_date = convert_strdate_to_date(to_date)
        current_date = start_date

        while current_date <= end_date:
            res[str(current_date)] = len(self.__get_ads_by_date(current_date))
            current_date += timedelta(days=1)
        return res

    # calculate the total number of 'favorits' in all ads.
    def __favorites_sum(self):
        total_favorites_count = 0
        for ad in self.m_ads:
            if ad.favorites_count != None:
                try:
                    total_favorites_count += int(ad.favorites_count)
                except:
                    pass
        return total_favorites_count

    # calculate how many times each currency used.
    def __currency_usage_count(self):
        currency_count = {}
        for ad in self.m_ads:
            if ad.currency in currency_count:
                currency_count[ad.currency] += 1
            else:
                currency_count[ad.currency] = 1
        # TODO: tmp solution:
        currency_count = {
            currency: count
            for currency, count in currency_count.items()
            if count > 7
            and currency != None
            and currency != "Price"
            and currency != "Under"
        }
        return currency_count

    def __max_price_for_each_currency(self):
        max_price_per_currency = {}

        # Find the highest price for each currency
        for ad in self.m_ads:
            if ad.currency in max_price_per_currency and ad.price != None:
                max_price_per_currency[ad.currency] = max(
                    max_price_per_currency[ad.currency], ad.price
                )
            elif ad.price != None:
                max_price_per_currency[ad.currency] = ad.price
        return max_price_per_currency

    def __min_price_for_each_currency(self):
        min_price_per_currency = {}

        # Find the lowest price for each currency
        for ad in self.m_ads:
            if ad.currency in min_price_per_currency and ad.price != None:
                min_price_per_currency[ad.currency] = min(
                    min_price_per_currency[ad.currency], ad.price
                )
            elif ad.price != None:
                min_price_per_currency[ad.currency] = ad.price

        return min_price_per_currency

    def __average_price_for_each_currency(self):
        price_sum_per_currency = {}
        count_per_currency = {}

        # Calculate the sum and count of prices for each currency
        for ad in self.m_ads:
            if ad.currency in price_sum_per_currency and ad.price != None:
                price_sum_per_currency[ad.currency] += ad.price
                count_per_currency[ad.currency] += 1
            elif ad.price != None:
                price_sum_per_currency[ad.currency] = ad.price
                count_per_currency[ad.currency] = 1

        # Calculate the average for each currency
        average_price_per_currency = {
            currency: round(
                price_sum_per_currency[currency] / count_per_currency[currency]
            )
            for currency in price_sum_per_currency
        }
        return average_price_per_currency

    def __max_year_built(self):
        max_year_built = None

        for ad in self.m_ads:
            if max_year_built is None or (
                ad.year_built != None
                and ad.year_built != "N/A"
                and ad.year_built > max_year_built
            ):
                max_year_built = ad.year_built

        return max_year_built

    def __min_year_built(self):
        min_year_built = None

        for ad in self.m_ads:
            if min_year_built is None or (
                ad.year_built != None
                and str(ad.year_built) != "-1"
                and ad.year_built < min_year_built
            ):
                min_year_built = ad.year_built
        return min_year_built

    def __count_ads_with_no_ad_date(self):
        count = 0
        for ad in self.m_ads:
            if ad.ad_date is None or ad.ad_date == "":
                count += 1
        return count

    def __oldest_ad_date(self):
        oldest_ad_date = None

        for ad in self.m_ads:
            if ad.ad_date:
                ad_date_obj = datetime.strptime(ad.ad_date, "%d.%m.%Y")
                if oldest_ad_date is None or ad_date_obj < oldest_ad_date:
                    oldest_ad_date = ad_date_obj

        return oldest_ad_date.strftime("%d.%m.%Y") if oldest_ad_date else None

    def __newest_ad_date(self):
        newest_ad_date = None

        for ad in self.m_ads:
            if ad.ad_date:
                ad_date_obj = datetime.strptime(ad.ad_date, "%d.%m.%Y")
                if newest_ad_date is None or ad_date_obj > newest_ad_date:
                    newest_ad_date = ad_date_obj

        return newest_ad_date.strftime("%d.%m.%Y") if newest_ad_date else None

    def __total_views(self):
        total_views = 0

        for ad in self.m_ads:
            if (
                ad.views is not None and ad.views != ""
            ):  # Check if views is not None # TODO delete ""
                total_views += ad.views

        return total_views

    def __average_views(self):
        total_views = 0
        count = 0

        for ad in self.m_ads:
            if (
                ad.views is not None and ad.views != ""
            ):  # Check if views is not None # TODO delete ""
                total_views += ad.views
                count += 1
        res = round(total_views / count if count > 0 else 0)
        return res

    def __total_number_of_ads(self):
        return len(self.m_ads)
