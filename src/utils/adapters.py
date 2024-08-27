from src.entities.Ad import Ad

def boat24_json_to_ad(boat_info):
    # Mapping the dictionary keys to the constructor arguments of the Ad class
    ad = Ad(
        name=boat_info.get('ads_name', None),
        currency=boat_info.get('currency', None),
        price=boat_info.get('price', None),
        favorites_count=boat_info.get('favorites_count', None),
        year_built=boat_info.get('year_built', None),
        ad_date=boat_info.get('ad_date', None),
        views=boat_info.get('views', None),
        other=boat_info.get('other', None)
    )
    return ad