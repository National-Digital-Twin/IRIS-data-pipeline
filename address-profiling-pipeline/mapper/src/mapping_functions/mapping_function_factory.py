# SPDX-License-Identifier: Apache-2.0
# Originally developed by Telicent Ltd.; subsequently adapted, enhanced, and maintained by the National Digital Twin Programme.

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

#  Modifications made by the National Digital Twin Programme (NDTP)
#  © Crown Copyright 2025. This work has been developed by the National Digital Twin Programme
#  and is legally attributed to the Department for Business and Trade (UK) as the governing entity.

from .epc_assessment import epc_assessment_function
from .floor import floor_function
from .heating import heating_function
from .roof import roof_function
from .structure_unit import structure_unit_function
from .wall import wall_function
from .window import window_function


def get_mapping_function(mapper_sub_type: str) -> str:
    """
    Returns a mapping function for the provided sub type.

    Args:
        A sub type of the mapper. One of [STRUCTURE_UNIT, EPC_ASSESSMENT, FLOOR, ROOF, WALL, WINDOW, HEATING].

    Returns:
        A function to map a record to the sub type.
    """

    if mapper_sub_type == "STRUCTURE_UNIT":
        return structure_unit_function
    elif mapper_sub_type == "EPC_ASSESSMENT":
        return epc_assessment_function
    elif mapper_sub_type == "FLOOR":
        return floor_function
    elif mapper_sub_type == "ROOF":
        return roof_function
    elif mapper_sub_type == "WALL":
        return wall_function
    elif mapper_sub_type == "WINDOW":
        return window_function
    elif mapper_sub_type == "HEATING":
        return heating_function
    else:
        raise NotImplementedError(
            "Error no mapping function exists for the provided sub type please provide one of STRUCTURE_UNIT, EPC_ASSESSMENT, FLOOR, ROOF, WALL, WINDOW OR HEATING"
        )
