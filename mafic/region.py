# SPDX-License-Identifier: MIT

from __future__ import annotations

from enum import Enum

__all__ = ("Group", "Region", "VoiceRegion")


# This is taken from Vibr logs, javacord and nextcord enums and may not be complete.
# Discord only documents and exposes 13 of these regions, but there are more.
class VoiceRegion(Enum):
    """Represents a Discord voice region.

    All the attributes here are best effort but may not be complete.
    The value is what you find in ``region[number].discord.media`` endpoints.
    """

    OREGON = "oregon"
    MONTREAL = "montreal"
    SOUTH_AFRICA = "southafrica"
    JAPAN = "japan"
    DUBAI = "dubai"
    SANTA_CLARA = "santa-clara"
    FINLAND = "finland"
    MADRID = "madrid"
    ST_PETE = "st-pete"
    INDIA = "india"
    SEATTLE = "seattle"
    RUSSIA = "russia"
    SYDNEY = "sydney"
    HONG_KONG = "hongkong"
    MILAN = "milan"
    NEWARK = "newark"
    US_CENTRAL = "us-central"
    US_WEST = "us-west"
    SANTIAGO = "santiago"
    STOCKHOLM = "stockholm"
    BUENOS_AIRES = "buenos-aires"
    US_SOUTH = "us-south"
    US_EAST = "us-east"
    SINGAPORE = "singapore"
    BUCHAREST = "bucharest"
    ATLANTA = "atlanta"
    BRAZIL = "brazil"
    ROTTERDAM = "rotterdam"
    FRANKFURT = "frankfurt"
    LONDON = "london"
    SOUTH_KOREA = "south-korea"
    EUROPE = "europe"
    AMSTERDAM = "amsterdam"

    def __repr__(self) -> str:
        return f"VoiceRegion.{self.name}"


class Region(Enum):
    """Represents a region of voice regions.

    This groups voice regions by geographical location.
    """

    EAST_NA = (VoiceRegion.MONTREAL, VoiceRegion.US_EAST, VoiceRegion.ATLANTA)
    CENTRAL_NA = (VoiceRegion.US_CENTRAL,)
    WEST_NA = (
        VoiceRegion.OREGON,
        VoiceRegion.SANTA_CLARA,
        VoiceRegion.SEATTLE,
        VoiceRegion.US_WEST,
    )
    SOUTH_NA = (VoiceRegion.US_SOUTH,)
    SOUTH_AMERICA = (VoiceRegion.SANTIAGO, VoiceRegion.BUENOS_AIRES, VoiceRegion.BRAZIL)
    SOUTH_AFRICA = (VoiceRegion.SOUTH_AFRICA,)
    NORTH_ASIA = (VoiceRegion.RUSSIA,)
    EAST_ASIA = (VoiceRegion.JAPAN, VoiceRegion.HONG_KONG)
    SOUTH_ASIA = (VoiceRegion.INDIA, VoiceRegion.SINGAPORE)
    WEST_ASIA = (VoiceRegion.DUBAI,)
    NORTH_EUROPE = (VoiceRegion.FINLAND, VoiceRegion.ST_PETE, VoiceRegion.STOCKHOLM)
    EAST_EUROPE = (VoiceRegion.BUCHAREST,)
    CENTRAL_EUROPE = (VoiceRegion.FRANKFURT, VoiceRegion.EUROPE)
    SOUTH_EUROPE = (VoiceRegion.MILAN,)
    WEST_EUROPE = (
        VoiceRegion.MADRID,
        VoiceRegion.NEWARK,
        VoiceRegion.ROTTERDAM,
        VoiceRegion.LONDON,
        VoiceRegion.AMSTERDAM,
    )
    OCEANIA = (VoiceRegion.SYDNEY,)

    def __repr__(self) -> str:
        return f"<Region.{self.name}>"


class Group(Enum):
    """Represents a group of regions.

    This groups regions by geographical location. These are very generic and should
    be used rarely.
    """

    WEST = (
        Region.EAST_NA,
        Region.WEST_NA,
        Region.SOUTH_NA,
        Region.CENTRAL_NA,
        Region.SOUTH_AMERICA,
    )
    CENTRAL = (
        Region.NORTH_EUROPE,
        Region.WEST_EUROPE,
        Region.SOUTH_EUROPE,
        Region.EAST_EUROPE,
        Region.SOUTH_AFRICA,
    )
    EAST = (
        Region.NORTH_ASIA,
        Region.EAST_ASIA,
        Region.SOUTH_ASIA,
        Region.WEST_ASIA,
        Region.OCEANIA,
    )

    def __repr__(self) -> str:
        return f"<Group.{self.name}>"
