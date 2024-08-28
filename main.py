from src.Scrapper_boat24 import Scrapper_boat24
from src.StatisticCalculator import StatisticsCalculator
from src.ReportBuilder import ReportBuilder


def main():
    boat24_scrapper = Scrapper_boat24()
    calculator = StatisticsCalculator()

    list_of_scrapped_ads = boat24_scrapper.get_ads()
    statistics = calculator.get_statistics(list_of_scrapped_ads)
    reportBuilder = ReportBuilder(list_of_scrapped_ads, statistics)
    reportBuilder.build_report("reports/report.xlsx")


if __name__ == "__main__":
    main()
