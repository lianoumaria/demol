import os
from textx import metamodel_from_file
import textx.scoping.providers as scoping_providers
from textx import get_location, TextXSemanticError
from demol.definitions import *


def get_component_mm(global_repo: bool = False):
    # Get meta-model from language description
    mm = metamodel_from_file(
        os.path.join(METAMODEL_REPO_PATH, 'component.tx'),
        auto_init_attributes=True,
        global_repository=global_repo,
        debug=False
    )

    mm.register_scope_providers(
        {
            "*.*": scoping_providers.FQNImportURI(importAs=True),
        }
    )

    mm.register_obj_processors({
    })

    return mm



