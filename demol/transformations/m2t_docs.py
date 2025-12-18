#!/usr/bin/env python

"""
m2t_docs.py
Generates professional, styled PlantUML diagrams, HTML wiring diagrams, and hardware documentation from DeMoL models.
"""

import os
from jinja2 import Environment, FileSystemLoader

def generate_documentation(model):
    """Generates the high-level system diagram, wiring diagram, and hardware documentation."""
    
    # Setup Jinja2 Environment
    # Templates are located in ../templates relative to this file
    templates_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates', 'docs')
    env = Environment(loader=FileSystemLoader(templates_dir))
    
    generated_files = []

    # 1. System Diagram
    try:
        template_sys = env.get_template('device_diagram.puml.j2')
        sys_content = template_sys.render(model=model)
        sys_filename = f'{model.metadata.name}.pu'
        with open(sys_filename, 'w') as f:
            f.write(sys_content)
        print(f"Generated System Diagram: {sys_filename}")
        generated_files.append(sys_filename)
    except Exception as e:
        print(f"Error generating system diagram: {e}")

    # 2. Wiring Diagram (HTML + Image)
    try:
        from html2image import Html2Image
        
        template_wiring = env.get_template('device_wiring.html.j2')
        wiring_html_content = template_wiring.render(model=model)
        wiring_html_filename = f'{model.metadata.name}_wiring.html'
        wiring_img_filename = f'{model.metadata.name}_wiring.png'
        
        with open(wiring_html_filename, 'w') as f:
            f.write(wiring_html_content)
        print(f"Generated Wiring Diagram HTML: {wiring_html_filename}")
        
        # Convert to Image
        hti = Html2Image(output_path='.', custom_flags=['--default-background-color=ffffff', '--hide-scrollbars'])
        # We need to pass the file path as a URL or absolute path
        file_path = os.path.abspath(wiring_html_filename)
        hti.screenshot(url=f'file://{file_path}', save_as=wiring_img_filename, size=(1200, 800))
        
        print(f"Generated Wiring Diagram Image: {wiring_img_filename}")
        # We append the image filename so the CLI can report it (though CLI expects .pu usually, we'll see)
        generated_files.append(wiring_img_filename)
        
    except ImportError:
        print("Error: html2image library not found. Install it with 'pip install html2image'.")
    except Exception as e:
        print(f"Error generating wiring diagram: {e}")

    # 3. Hardware Documentation
    try:
        template_doc = env.get_template('hardware_doc.md.j2')
        doc_content = template_doc.render(model=model)
        doc_filename = f'{model.metadata.name}_hardware_doc.md'
        with open(doc_filename, 'w') as f:
            f.write(doc_content)
        print(f"Generated Hardware Documentation: {doc_filename}")
    except Exception as e:
        print(f"Error generating hardware documentation: {e}")
    
    # 4. Single HTML Documentation
    try:
        import base64
        
        # Helper to encode image to base64
        def encode_image(image_path):
            if os.path.exists(image_path):
                with open(image_path, "rb") as image_file:
                    return base64.b64encode(image_file.read()).decode('utf-8')
            return None

        # Generate System Diagram Image (using PlantUML if available)
        # We need to run plantuml on the generated .pu file to get the .png
        # The CLI usually does this, but for the single doc we need it now.
        sys_img_filename = f'{model.metadata.name}.png'
        try:
            import plantuml
            pl = plantuml.PlantUML(url='http://www.plantuml.com/plantuml/img/')
            # We assume the .pu file was generated in step 1
            sys_pu_filename = f'{model.metadata.name}.pu'
            if os.path.exists(sys_pu_filename):
                # This saves the image to the current directory with the same basename
                # Note: plantuml library behavior might vary, let's try to fetch raw content
                raw_png = pl.processes(sys_content)
                with open(sys_img_filename, 'wb') as f:
                    f.write(raw_png)
                print(f"Generated System Diagram Image: {sys_img_filename}")
        except Exception as e:
            print(f"Could not generate system diagram image for embedding: {e}")

        # Encode images
        sys_b64 = encode_image(sys_img_filename)
        # Wiring image was generated in step 2
        wiring_img_filename = f'{model.metadata.name}_wiring.png'
        wiring_b64 = encode_image(wiring_img_filename)

        template_full_doc = env.get_template('device_documentation.html.j2')
        full_doc_content = template_full_doc.render(
            model=model,
            system_diagram_b64=sys_b64,
            wiring_diagram_b64=wiring_b64
        )
        
        full_doc_filename = f'{model.metadata.name}_documentation.html'
        with open(full_doc_filename, 'w') as f:
            f.write(full_doc_content)
        print(f"Generated Single HTML Documentation: {full_doc_filename}")
        
    except Exception as e:
        print(f"Error generating single HTML documentation: {e}")
    
    return generated_files
