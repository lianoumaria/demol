#!/usr/bin/env python3
"""Script to run m2t_rpi code generation on all RPI device examples.

This script identifies all .dev files that use RaspberryPi boards and
runs the m2t_rpi transformation on them.
"""

import os
import sys
from pathlib import Path
import logging

# Add project root to path
REPO_PATH = Path(__file__).parent.parent
sys.path.insert(0, str(REPO_PATH))

from demol.transformations.m2t_rpi import transform_device_model

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# RPI device examples identified from the examples directory
RPI_EXAMPLES = [
    # SmAutoExamples
    ("SmAutoExamples/EntranceLEDs.dev", "rpi_out/SmAutoExamples/EntranceLEDs"),
    ("SmAutoExamples/ParkingLeds.dev", "rpi_out/SmAutoExamples/ParkingLeds"),
    ("SmAutoExamples/ParkingSensor.dev", "rpi_out/SmAutoExamples/ParkingSensor"),
    ("SmAutoExamples/RPiFan.dev", "rpi_out/SmAutoExamples/RPiFan"),
    ("SmAutoExamples/SmartWindow.dev", "rpi_out/SmAutoExamples/SmartWindow"),
    
    # ThesisExamples
    ("ThesisExamples/LoCScenario1.dev", "rpi_out/ThesisExamples/LoCScenario1"),
    ("ThesisExamples/LoCScenario2.dev", "rpi_out/ThesisExamples/LoCScenario2"),
    ("ThesisExamples/ThesisExample.dev", "rpi_out/ThesisExamples/ThesisExample"),
    
    # moreExamples
    ("moreExamples/RPi_ADC.dev", "rpi_out/moreExamples/RPi_ADC"),
    ("moreExamples/RPi_gas_led.dev", "rpi_out/moreExamples/RPi_gas_led"),
    ("moreExamples/rpi5_ToF.dev", "rpi_out/moreExamples/rpi5_ToF"),
    ("moreExamples/rpi_5_TCRT.dev", "rpi_out/moreExamples/rpi_5_TCRT"),
    ("moreExamples/rpi_constraint_bme.dev", "rpi_out/moreExamples/rpi_constraint_bme"),
    ("moreExamples/rpi_iot_device.dev", "rpi_out/moreExamples/rpi_iot_device"),
]


def main():
    """Run m2t_rpi transformation on all RPI examples."""
    logger.info(f"Starting RPI code generation for {len(RPI_EXAMPLES)} examples")
    
    successful = []
    failed = []
    
    for dev_model, output_dir in RPI_EXAMPLES:
        logger.info(f"\n{'='*70}")
        logger.info(f"Processing: {dev_model}")
        logger.info(f"Output to: {output_dir}")
        logger.info(f"{'='*70}")
        
        try:
            transform_device_model(dev_model, output_dir)
            successful.append(dev_model)
            logger.info(f"✓ Successfully generated code for {dev_model}")
        except Exception as e:
            failed.append((dev_model, str(e)))
            logger.error(f"✗ Failed to generate code for {dev_model}: {e}")
            # Continue with next example instead of stopping
    
    # Summary
    logger.info(f"\n{'='*70}")
    logger.info("GENERATION SUMMARY")
    logger.info(f"{'='*70}")
    logger.info(f"Total examples: {len(RPI_EXAMPLES)}")
    logger.info(f"Successful: {len(successful)}")
    logger.info(f"Failed: {len(failed)}")
    
    if successful:
        logger.info("\n✓ Successful generations:")
        for example in successful:
            logger.info(f"  - {example}")
    
    if failed:
        logger.info("\n✗ Failed generations:")
        for example, error in failed:
            logger.info(f"  - {example}")
            logger.info(f"    Error: {error}")
    
    # Exit with appropriate code
    sys.exit(0 if not failed else 1)


if __name__ == "__main__":
    main()
