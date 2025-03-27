# SPDX-License-Identifier: Apache-2.0

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

# This file is unmodified from its original version developed by Telicent Ltd.,
# and is now included as part of a repository maintained by the National Digital Twin Programme.
# All support, maintenance and further development of this code is now the responsibility
# of the National Digital Twin Programme.

from telicent_lib.access import SecurityLabelBuilder, EDHSecurityLabelsV2

def string_to_label(security_label: str, delimiter:str = ","):
    labels = security_label.split(delimiter)
    groups = []
    slb = SecurityLabelBuilder()
    attrs = dict() 
    for label in labels:
        attribute_value = label.split("=")
        attribute = attribute_value[0]
        
        if len(attribute_value) == 1:
            groups.append(label)
            continue
        value = attribute_value[1]
        match attribute:
            case EDHSecurityLabelsV2.PERMITTED_ORGANISATIONS.value.name:
                if EDHSecurityLabelsV2.PERMITTED_ORGANISATIONS.name not in attrs:
                    attrs[EDHSecurityLabelsV2.PERMITTED_ORGANISATIONS.name] = []
                attrs[EDHSecurityLabelsV2.PERMITTED_ORGANISATIONS.name].append(value)
            case EDHSecurityLabelsV2.PERMITTED_NATIONALITIES.value.name:
                if EDHSecurityLabelsV2.PERMITTED_NATIONALITIES.name not in attrs:
                    attrs[EDHSecurityLabelsV2.PERMITTED_NATIONALITIES.name] = []
                attrs[EDHSecurityLabelsV2.PERMITTED_NATIONALITIES.name].append(value)
            case EDHSecurityLabelsV2.CLASSIFICATION.value.name:
                attrs[EDHSecurityLabelsV2.CLASSIFICATION.name] = value
            case _: 
                print(f"Attribute {attribute}, not valid in handling model")
    for group in groups:
        details = group.split(":")
        group_type = details[-1]
        match group_type:
            case "and":
                if EDHSecurityLabelsV2.AND_GROUPS.value.name not in attrs:
                    attrs[EDHSecurityLabelsV2.AND_GROUPS.name] = []
                attrs[EDHSecurityLabelsV2.AND_GROUPS.name].append(":".join(details[:-1]))
            case "or":
                if EDHSecurityLabelsV2.OR_GROUPS.value.name not in attrs:
                    attrs[EDHSecurityLabelsV2.OR_GROUPS.name] = []
                attrs[EDHSecurityLabelsV2.OR_GROUPS.name].append(":".join(details[:-1]))
            case _: 
                print(f"Group {group}, is not valid in handling model, must be an and or or group")
   
    for k in attrs: 
        if isinstance(type(attrs[k]), list):
            slb.add_multiple(EDHSecurityLabelsV2[k].value, *attrs[k])
        else: 
            slb.add(EDHSecurityLabelsV2[k].value, attrs[k])
    return slb.build()
            





