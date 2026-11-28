# YamBMS ( Yet another multi-BMS Merging Solution )
# GitHub  : https://github.com/Sleeper85/esphome-yambms
#
# This file is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation, either version 3
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.

"""Make entities on ESPHome sub-devices unique for MQTT and Prometheus.

Since YamBMS 1.6.0 each BMS, shunt, balancer, ... is an ESPHome sub-device and
its entities no longer carry the device name (e.g. "Charging Power" on device
"BMS 1" instead of "BMS 1 Charging Power"). The Home Assistant API keeps them
apart with the device id, but ESPHome builds MQTT topics and Prometheus labels
from the entity name only, so with several BMS every BMS publishes to the same
`<prefix>/sensor/charging_power/state` topic / `id="charging_power"` label.

This component prefixes them with the sub-device name, at code generation time:

  MQTT       : <topic_prefix>/<type>/<device>_<object_id>/state (and /command)
  Prometheus : id="<device>_<object_id>", name="<device name> <entity name>"

Entities that already set `state_topic` / `command_topic`, or that already have
a Prometheus `relabel` entry, are left untouched.
"""

import logging

import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.const import (
    CONF_COMMAND_TOPIC,
    CONF_DEVICE_ID,
    CONF_DEVICES,
    CONF_ID,
    CONF_MQTT,
    CONF_MQTT_ID,
    CONF_NAME,
    CONF_RELABEL,
    CONF_STATE_TOPIC,
    CONF_TOPIC_PREFIX,
)
from esphome.core import CORE, ID
from esphome.cpp_types import EntityBase
from esphome.helpers import sanitize, snake_case

_LOGGER = logging.getLogger(__name__)

CODEOWNERS = ["@Sleeper85"]

CONF_PROMETHEUS = "prometheus"

# Entity domain -> (MQTT component type, has a command topic).
# Domains whose MQTT component uses several topics of its own (climate, cover,
# fan, light, valve, alarm_control_panel) are not handled.
ENTITY_DOMAINS = {
    "binary_sensor": ("binary_sensor", False),
    "sensor": ("sensor", False),
    "text_sensor": ("sensor", False),  # ESPHome publishes text sensors as "sensor"
    "event": ("event", False),
    "update": ("update", True),
    "button": ("button", True),
    "switch": ("switch", True),
    "number": ("number", True),
    "select": ("select", True),
    "text": ("text", True),
    "lock": ("lock", True),
    "date": ("date", True),
    "time": ("time", True),
    "datetime": ("datetime", True),
}

CONFIG_SCHEMA = cv.Schema(
    {
        cv.Optional(CONF_MQTT, default=True): cv.boolean,
        cv.Optional(CONF_PROMETHEUS, default=True): cv.boolean,
    }
)


def _object_id(name: str) -> str:
    """Same as the C++ EntityBase::write_object_id_to()."""
    return sanitize(snake_case(name))


def _iter_entities(value):
    """Yield every entity config (top-level or nested in a platform) of a domain."""
    if isinstance(value, dict):
        entity_id = value.get(CONF_ID)
        if (
            isinstance(entity_id, ID)
            and entity_id.type is not None
            and entity_id.type.inherits_from(EntityBase)
            and value.get(CONF_DEVICE_ID) is not None
        ):
            yield value
        for child in value.values():
            yield from _iter_entities(child)
    elif isinstance(value, list):
        for child in value:
            yield from _iter_entities(child)


async def to_code(config):
    devices = {
        dev[CONF_ID].id: dev[CONF_NAME]
        for dev in CORE.config.get("esphome", {}).get(CONF_DEVICES, [])
    }

    topic_prefix = None
    if config[CONF_MQTT] and CONF_MQTT in CORE.config:
        topic_prefix = CORE.config[CONF_MQTT].get(CONF_TOPIC_PREFIX)
        if not topic_prefix:
            _LOGGER.warning(
                "yambms_sub_device_topics: mqtt topic_prefix is empty, MQTT topics are not changed"
            )

    prometheus = None
    relabeled = set()
    if config[CONF_PROMETHEUS] and CONF_PROMETHEUS in CORE.config:
        prom_conf = CORE.config[CONF_PROMETHEUS]
        prometheus = await cg.get_variable(prom_conf[CONF_ID])
        relabeled = {key.id for key in prom_conf.get(CONF_RELABEL, {})}

    if not topic_prefix and prometheus is None:
        return

    for domain, (mqtt_type, has_command) in ENTITY_DOMAINS.items():
        for entity in _iter_entities(CORE.config.get(domain)):
            name = entity.get(CONF_NAME)
            device_name = devices.get(entity[CONF_DEVICE_ID].id)
            if not name or not device_name:
                # Unnamed entities already take the device name as their name
                continue

            unique_id = f"{_object_id(device_name)}_{_object_id(name)}"

            mqtt_id = entity.get(CONF_MQTT_ID)
            if topic_prefix and mqtt_id is not None:
                mqtt_var = await cg.get_variable(mqtt_id)
                base = f"{topic_prefix}/{mqtt_type}/{unique_id}"
                if CONF_STATE_TOPIC not in entity:
                    cg.add(mqtt_var.set_custom_state_topic(f"{base}/state"))
                if has_command and CONF_COMMAND_TOPIC not in entity:
                    cg.add(mqtt_var.set_custom_command_topic(f"{base}/command"))

            if prometheus is not None and entity[CONF_ID].id not in relabeled:
                entity_var = await cg.get_variable(entity[CONF_ID])
                cg.add(prometheus.add_label_id(entity_var, unique_id))
                cg.add(prometheus.add_label_name(entity_var, f"{device_name} {name}"))
