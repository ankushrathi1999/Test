from collections import  defaultdict
import pandas as pd
import json
import yaml
import logging

from .db import get_vehicle_models, get_vehicle_part_mapping
from config.config import save_vehicle_parts_lookup_lh, save_vehicle_parts_lookup_rh, get_artificats

logger = logging.getLogger(__name__)

class ValidationError(Exception):
    pass

def group_part_types(vehicle_parts, part_master_lookup):
    generic_parts = []
    for part in vehicle_parts:
        details = part_master_lookup.loc[part['part_number']]
        generic_parts.append([part, details])
    return {
        'generic_parts': generic_parts
    }

def process_generic_parts(vehicle_data, generic_parts, missing_class_name_lookup, OK_class_name_lookup, color_classification_parts):
    for part, details in generic_parts:
        if details['is_supported'] == 0:
            continue
        part_class = part.get('part_class', details.part_class)
        data = vehicle_data[part_class] = {
            "part_name": details.part_name_msil,
            "part_number": part['part_number'],
            "part_name_long": part['part_name'],
            "color_classification_enabled": part_class in color_classification_parts
        }
        if part.get('is_miss'):
            data['is_miss'] = True
        if len(details.part_group_name.strip()) > 0:
            data["is_group"] = True
            data["part_group"] = details.part_group_name.strip()
        missing_class_name = missing_class_name_lookup.get(part_class)
        if missing_class_name is not None:
            data['missing_class_name'] = missing_class_name
        OK_class_name = OK_class_name_lookup.get(part_class)
        if OK_class_name is not None:
            data['OK_class_name'] = OK_class_name

def prepare_vehicle_master(vehicle_model, vehicle_description, metadata):
    (vehicle_part_type_groups, missing_class_name_lookup, OK_class_name_lookup, color_classification_parts) = metadata
    
    errors = []
    vehicle_data = {
        'vehicle_description': vehicle_description,
    }

    if vehicle_model not in vehicle_part_type_groups:
        errors.append(f"No parts have been registered for {vehicle_model}.")
        return None, errors
    vehicle_part_type_groups = vehicle_part_type_groups[vehicle_model]
    
    process_generic_parts(vehicle_data, vehicle_part_type_groups['generic_parts'], missing_class_name_lookup,
                          OK_class_name_lookup, color_classification_parts)

    return vehicle_data, errors

    
def get_metadata(vehicle_models, db_name=None, keep_inactive_parts=False):
    # Part Master CSV
    part_master = pd.read_csv('./config/part_master.csv').fillna('')
    part_master_lookup = part_master.set_index('part_number')
    logger.debug("Parts loaded: %s", len(part_master))

    mapping = get_vehicle_part_mapping(vehicle_models, db_name, keep_inactive_parts=keep_inactive_parts)
    logger.debug("Vehicle part mapping: %s", len(mapping))

    with open('./config/missing_class_names.json', 'r') as f:
        missing_class_name_lookup = json.load(f)
    logger.debug("Missing classes registered: %s", len(missing_class_name_lookup))

    with open('./config/Ok_class_names.json', 'r') as f:
        OK_class_name_lookup = json.load(f)
    logger.debug("OK classes registered: %s", len(OK_class_name_lookup))

    logger.debug("Count of parts by vechicle model:")
    for vehicle_model, vehicle_parts in mapping.items():
        logger.debug("%s=%s", vehicle_model, len(vehicle_parts))

    vehicle_part_type_groups = {vehicle_model: group_part_types(vehicle_parts, part_master_lookup)
                                for vehicle_model, vehicle_parts in mapping.items()}
    
    with open('./config/color_classification_parts.json', 'r') as f:
        color_classification_parts = set(json.load(f))
    logger.debug("Parts registered for color classification: %s", len(color_classification_parts))
    
    return vehicle_part_type_groups, missing_class_name_lookup, OK_class_name_lookup, color_classification_parts


def validate_vehicle_part_data(vehicle_model, artifact_code):
    artifacts = [artifact for artifact in get_artificats()['artifacts'] if artifact['code'] == artifact_code]
    if len(artifacts) != 1:
        return False, [f"Invalid artifact code: {artifact_code}"]
    artifact = artifacts[0]
    metadata = get_metadata([vehicle_model], db_name=artifact['database'], keep_inactive_parts=True)
    try:
        data, errors = prepare_vehicle_master(vehicle_model, None, metadata)
        is_valid = len(errors) == 0
    except Exception as ex:
        message = f"Failed to validate parts data for {vehicle_model}. [INTERNAL ERROR]."
        logger.exception(message)
        errors = [message]
        is_valid = False
    return is_valid, errors


def build_all_vehicle_master():
    artifacts = get_artificats()['artifacts']

    for artifact in artifacts:
        logger.debug("Building vehicle master for artifact: %s", artifact['code'])
        
        vehicle_models = get_vehicle_models(db_name=artifact['database'])
        logger.debug("Vehicle models: %s", len(vehicle_models))

        metadata = get_metadata(vehicle_models, db_name=artifact['database'])
        
        vehicle_data = defaultdict(dict)
        for vehicle_model, vehicle_description in vehicle_models:
            try:
                data, errors = prepare_vehicle_master(vehicle_model, vehicle_description, metadata)
                if len(errors) > 0:
                    logger.error("Validation errors for %s", vehicle_model)
                    for err in errors:
                        logger.error(str(err))
                if data is not None:
                    vehicle_data[vehicle_model] = data
            except Exception as ex:
                logger.exception("Error processing %s. %s", vehicle_model, ex)

        if len(vehicle_data) > 0:
            if artifact['code'] == 'DOOR_LH':
                save_vehicle_parts_lookup_lh(dict(vehicle_data))
            elif artifact['code'] == 'DOOR_RH':
                save_vehicle_parts_lookup_rh(dict(vehicle_data))
            else:
                logger.error("Unknown artifact code: %s", artifact['code'])
            logger.debug("Vehicle master successfully written for artifact: %s", artifact['code'])
        else:
            logger.error("No vehicles were successfully processed.")