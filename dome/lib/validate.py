from dome.config import *

# Check whether an entity is valid for this context
def validEntity(ha_name):
    ha_type = ha_name.split('.')[0]

    valid_type = ha_type in ENTITY_WHITELIST
    not_blacklisted = ha_name not in DEVICE_BLACKLIST

    return valid_type and not_blacklisted