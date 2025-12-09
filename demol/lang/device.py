import os
from textx import metamodel_from_file
import textx.scoping.providers as scoping_providers
from textx import get_location, TextXSemanticError
from demol.definitions import *


GRAMMAR_BULTINS = {}


def raise_validation_error(obj, msg):
    raise TextXSemanticError(
        f'{msg}',
        **get_location(obj)
    )


def model_proc(model, metamodel):
    """
    Enhanced model processor with comprehensive validation based on formal semantics.
    
    Implements validation rules from SEMANTICS.md:
    - Section 4.1: Well-formedness rules
    - Section 6.7: Invariants
    - Section 8.1: Safety properties
    - Section 8.4: Well-formedness conditions
    """
    from demol.lang.semantics import (
        raise_validation_error,
        validate_power_connection,
        validate_gpio_connection,
        validate_i2c_connection,
        validate_spi_connection,
        validate_uart_connection,
        validate_no_pin_conflicts,
        validate_i2c_address_uniqueness,
        validate_voltage_limits,
        validate_all_peripherals_connected,
        validate_broker_requirements,
        validate_io_voltage_compatibility,
        validate_common_ground,
        validate_connections,
        validate_unique_peripheral_names,
    )
    
    device_name = model.metadata.name.strip('"')

    print(f'[*] Processing model: {model._tx_filename}')
    
    # ========================================================================
    # Model Enrichment
    # ========================================================================
    enrich_model(model)
    
    # ========================================================================
    # Well-Formedness: All peripherals must be connected
    # ========================================================================
    validate_all_peripherals_connected(model)

    # ========================================================================
    # Well-Formedness: Unique peripheral names
    # ========================================================================
    validate_unique_peripheral_names(model)
    
    # ========================================================================
    # Well-Formedness: Broker requirements
    # ========================================================================
    validate_broker_requirements(model)
    
    # ========================================================================
    # Well-Formedness: Common ground check
    # ========================================================================
    validate_common_ground(model)
    
    # ========================================================================
    # Connection Validation
    # ========================================================================
    validate_connections(model)
    
    # ========================================================================
    # Global Safety Validations
    # ========================================================================
    
    # Safety: No pin conflicts (unique pins per connection)
    validate_no_pin_conflicts(model.connections)
    
    # Safety: I2C addresses must be unique on the same bus
    validate_i2c_address_uniqueness(model.connections)
    
    # Safety: Voltage limits must not be exceeded
    validate_voltage_limits(model)
    
    # Safety: IO Voltage compatibility
    validate_io_voltage_compatibility(model)
    
    # Safety: Common ground connection
    validate_common_ground(model)
    
    print("[✓] All validation checks passed!")


def enrich_model(model):
    """
    Enrich the model with auto-generated values.
    """
    device_name = model.metadata.name.strip('"')
    
    for c in model.connections:
        # Set the board for easy navigation in M2M and M2T transformations
        setattr(c, 'board', model.components.board)
        
        # ====================================================================
        # Auto-generate topic if not specified
        # ====================================================================
        if not c.remote:
            peripheral_def = c.peripheral
            peripheral_ref = peripheral_def.ref
            peripheral_def_name = peripheral_def.name
            peripheral_type = type(peripheral_ref).__name__
            peripheral_msg = peripheral_ref.type
            
            default_topic = f'"{device_name}.{peripheral_type}.{peripheral_msg}.{peripheral_def_name}"'
            c.remote = default_topic.lower().strip('""')


def get_device_mm(debug: bool = False, global_repo: bool = False):
    mm = metamodel_from_file(
        os.path.join(METAMODEL_REPO_PATH, 'device.tx'),
        auto_init_attributes=True,
        global_repository=global_repo,
        textx_tools_support=True,
        debug=debug
    )

    mm.register_scope_providers(
        {
            "*.*": scoping_providers.FQN(),
            "*.*": scoping_providers.FQNImportURI(importAs=True),
            "Components.peripherals": scoping_providers.FQNGlobalRepo(
                os.path.join(PERIPHERAL_MODEL_REPO_PATH, '*.hwd')
            ),
            "Components.board": scoping_providers.FQNGlobalRepo(
                os.path.join(BOARD_MODEL_REPO_PATH, '*.hwd')
            ),

        }
    )

    mm.register_model_processor(model_proc)

    mm.register_obj_processors({

        # EMPTY
    })

    return mm
