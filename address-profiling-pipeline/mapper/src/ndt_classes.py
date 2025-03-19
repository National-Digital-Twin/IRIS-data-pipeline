#
# Copyright (C) Telicent Ltd
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

wall_type_map = {
    "GraniteOrWhinstone": "GraniteOrWhinstoneWall",
    "Sandstone": "SandstoneWall",
    "SandstoneOrLimestone": "SandstoneOrLimestoneWall",
    "SolidBrick": "SolidBrickWall",
    "Cavity": "CavityWall",
    "CavityWall": "CavityWall",
    "TimberFrame": "TimberFrameWall",
    "SystemBuilt": "SystemBuiltWall",
    "CobWall": "CobWall",
    "Cob": "CobWall",
    "ParkHomeWall": "ParkHomeWall",
    "NULL": None,
    "": None,
    "Other": "Wall",
}

wall_insulation_map = {
    "External": "ExternalWallInsulation",
    "FilledCavity": "FilledCavityWallInsulation",
    "Internal": "InternalWallInsulation",
    "WithInternalInsulation": "InternalWallInsulation",
    "WithExternalInsulation": "ExternalWallInsulation",
    "AsBuilt": "AsBuiltWallInsulation",
    "Unknown": "UnknownWallInsulation",
    "FilledCavityAndInternalInsulation": "FilledCavityAndInternalWallInsulation",
    "FilledCavityAndExternalInsulation": "FilledCavityAndExternalWallInsulation",
    "FilledCavityPlusExternal": "FilledCavityAndInternalWallInsulation",
    "FilledCavityPlusInternal": "FilledCavityAndExternalWallInsulation",
    "WithAdditionalInsulation": "WallInsulationWithAdditionalInsulation",
    "NULL": None,
    "": None,
}

floor_type_map = {
    "Unknown": None,
    "Other": "Floor",
    "Solid": "SolidFloor",
    "SuspendedTimber": "Suspended",
    "SuspendedNotTimber": "Suspended",
    "Suspended": "Suspended",
    "OtherPremisesBelow": "OtherPremisesBelowFloor",
    "AnotherDwellingBelow": "AnotherDwellingBelowFloor",
    "NULL": None,
    "": None,
}

floor_insulation_map = {
    "AsBuilt": None,
    "RetroFitted": "InsulatedFloor",
    "NoInsulation": None,
    "Insulated": "InsulatedFloor",
    "LimitedInsulation": "LimitedFloorInsulation",
    "NULL": None,
    "": None,
}

roof_type_map = {
    "Flat": "FlatRoof",
    "AnotherDwellingAbove": "AnotherDwellingAboveRoof",
    "OtherPremisesAbove": "OtherPremisesAboveRoof",
    "Pitched": "PitchedRoof",
    "PitchedNormalLoftAccess": "PitchedRoof",
    "PitchedNormalNoLoftAccess": "PitchedRoof",
    "PitchedThatched": "ThatchedRoof",
    "PitchedWithSlopingCeiling": "PitchedRoof",
    "ParkHomeRoof": "ParkHomeRoof",
    "Thatched": "ThatchedRoof",
    "RoofRooms": "RoofWithRooms",
    "Other": "Roof",
    "NULL": None,
    "": None,
}

roof_insulation_map = {
    "Rafters": "RaftersRoofInsulation",
    "InsulatedAtRafters": "RaftersRoofInsulation",
    "Joists": "JoistsRoofInsulation",
    "CeilingInsulated": "CeilingInsulation",
    "Unknown": None,
    "None": None,
    "FlatRoofInsulation": "FlatRoofInsulation",
    "SlopingCeilingInsulation": "SlopingCeilingRoofInsulation",
    "NoInsulation": None,
    "NoInsulation(Assumed)": "AssumedNoInsulation",
    "LoftInsulation(Assumed)": "AssumedLoftInsulation",
    "LoftInsulation": "LoftInsulation",
    "LimitedInsulationAssumed": "AssumedLimitedInsulation",
    "LimitedInsulation": "LimitedInsulation",
    "InsulatedAssumed": "InsulatedAssumed",
    "NoInsulationAssumed": "NoInsulationAssumed",
    "Other": "RoofInsulation",
    "Insulated": "RoofInsulation",
    "Thatched": None,
    "ThatchedWithAdditionalInsulation": "ThatchedWithAdditionalRoofInsulation",
    "NULL": None,
    "": None,
}

window_type_map = {
    "DoubleGlazingPre2002": "DoubleGlazedBefore2002Window",
    "DoubleGlazing2002OrLater": "DoubleGlazedAfter2002Window",
    "DoubleGlazingAfter2002": "DoubleGlazedAfter2002Window",
    "DoubleGlazingBefore2002": "DoubleGlazedBefore2002Window",
    "DoubleGlazingUnknownAge": "DoubleGlazedWindow",
    "SecondaryGlazing": "SecondaryGlazedWindow",
    "SingleGlazing": "SingleGlazedWindow",
    "DoubleGlazing": "DoubleGlazingWindow",
    "TripleGlazing": "TripleGlazedWindow",
    "DoubleKnownData": "DoubleKnownDataWindow",
    "TripleKnownData": "TripleKnownDataWindow",
    "NULL": None,
    "": None,
}
