import math

def device_to_svg(model, output_file=None):
    """
    Generates a professional SVG diagram from a device model.
    Shows interconnection between board and peripherals at PIN level.
    Layout: Schematic style with Board in center, Peripherals on Left/Right.
    """
    if not output_file:
        output_file = f"{model.metadata.name}.svg"

    # --- Configuration ---
    # Colors
    COLOR_BG = "#ffffff"
    COLOR_BOARD_FILL = "#2c3e50" # Dark Blue-Grey
    COLOR_BOARD_STROKE = "#34495e"
    COLOR_BOARD_TEXT = "#ecf0f1"
    
    COLOR_PERIPH_FILL = "#f8f9fa" # Light Grey
    COLOR_PERIPH_STROKE = "#bdc3c7"
    COLOR_PERIPH_TEXT = "#2c3e50"
    
    COLOR_PIN_TEXT = "#7f8c8d"
    COLOR_PIN_MARKER = "#95a5a6"
    
    COLOR_LINE_DEFAULT = "#3498db" # Blue
    COLOR_LINE_POWER = "#e74c3c"   # Red
    COLOR_LINE_GND = "#2c3e50"     # Dark
    
    # Dimensions
    PIN_SPACING = 25
    PIN_MARGIN_TOP = 40
    PIN_MARGIN_BOTTOM = 20
    
    PERIPH_WIDTH = 180
    BOARD_WIDTH = 300
    
    GAP_BOARD_PERIPH = 200 # Space for wires
    MARGIN_X = 50
    MARGIN_Y = 50
    
    # Font Sizes
    FONT_TITLE = 24
    FONT_COMP_TITLE = 16
    FONT_PIN = 12

    # --- Data Extraction & Organization ---
    connections = model.connections
    if not connections:
        print("No connections found.")
        return

    # Group connections into Left and Right sets to balance the diagram
    left_peripherals = []
    right_peripherals = []
    
    # We can just alternate for balance
    for i, conn in enumerate(connections):
        # Extract all pins for this connection
        pin_pairs = [] # list of (board_pin, periph_pin, type)
        
        # Data Connections
        if hasattr(conn, 'dataConns'):
            for dc in conn.dataConns:
                for pin in dc.pins:
                    pin_pairs.append({
                        'board': str(pin.boardPin),
                        'periph': str(pin.peripheralPin),
                        'type': 'data'
                    })
        
        # Power Connections
        if hasattr(conn, 'powerConns'):
            for pc in conn.powerConns:
                p_type = 'power'
                b_pin_lower = str(pc.boardPin).lower()
                if 'gnd' in b_pin_lower:
                    p_type = 'gnd'
                pin_pairs.append({
                    'board': str(pc.boardPin),
                    'periph': str(pc.peripheralPin),
                    'type': p_type
                })

        periph_data = {
            'name': conn.peripheral.name,
            'type': conn.peripheral.ref.type if hasattr(conn.peripheral.ref, 'type') else 'Peripheral',
            'pins': pin_pairs,
            'height': PIN_MARGIN_TOP + len(pin_pairs) * PIN_SPACING + PIN_MARGIN_BOTTOM
        }
        
        if i % 2 == 0:
            right_peripherals.append(periph_data) # Start right, usually looks better reading left-to-right flow? Actually schematic usually inputs left, outputs right. But this is star topology. Let's alternate.
        else:
            left_peripherals.append(periph_data)

    # --- Layout Calculation ---
    
    # Calculate total height required for each side
    def get_total_stack_height(periph_list):
        h = 0
        for p in periph_list:
            h += p['height'] + 30 # + gap between peripherals
        return h

    height_left = get_total_stack_height(left_peripherals)
    height_right = get_total_stack_height(right_peripherals)
    
    # Board height needs to accommodate all pins on the busiest side
    # Count total pins on left vs right
    pins_on_left_edge = sum(len(p['pins']) for p in left_peripherals)
    pins_on_right_edge = sum(len(p['pins']) for p in right_peripherals)
    
    max_pins_side = max(pins_on_left_edge, pins_on_right_edge)
    min_board_height = PIN_MARGIN_TOP + max_pins_side * PIN_SPACING + PIN_MARGIN_BOTTOM
    
    # The canvas height is determined by the max stack height or board height
    total_content_height = max(height_left, height_right, min_board_height)
    
    CANVAS_HEIGHT = total_content_height + 2 * MARGIN_Y
    CANVAS_WIDTH = MARGIN_X + PERIPH_WIDTH + GAP_BOARD_PERIPH + BOARD_WIDTH + GAP_BOARD_PERIPH + PERIPH_WIDTH + MARGIN_X
    
    # Center Y
    center_y = CANVAS_HEIGHT / 2
    
    # Board Position
    board_x = MARGIN_X + PERIPH_WIDTH + GAP_BOARD_PERIPH
    board_h = max(min_board_height, total_content_height * 0.6) # Make board at least 60% of height if stacks are huge, or min required
    board_y = center_y - board_h / 2
    
    board_rect = {
        'x': board_x, 'y': board_y, 'w': BOARD_WIDTH, 'h': board_h,
        'name': connections[0].board.name
    }

    # --- SVG Generation Helpers ---
    svg_elements = []
    
    def svg_rect(x, y, w, h, fill, stroke, r=8):
        return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="{stroke}" stroke-width="2" rx="{r}" ry="{r}" />'
    
    def svg_text(x, y, text, size, color, anchor="middle", weight="normal", baseline="middle"):
        return f'<text x="{x}" y="{y}" font-family="Segoe UI, Roboto, Helvetica, Arial, sans-serif" font-size="{size}" font-weight="{weight}" fill="{color}" text-anchor="{anchor}" dominant-baseline="{baseline}">{text}</text>'
    
    def svg_line(x1, y1, x2, y2, color):
        return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="2" />'

    def svg_bezier(x1, y1, x2, y2, color):
        # Control points
        dist = abs(x2 - x1) * 0.5
        cp1x = x1 + dist if x2 > x1 else x1 - dist
        cp1y = y1
        cp2x = x2 - dist if x2 > x1 else x2 + dist
        cp2y = y2
        return f'<path d="M {x1} {y1} C {cp1x} {cp1y}, {cp2x} {cp2y}, {x2} {y2}" stroke="{color}" stroke-width="2" fill="none" />'

    def svg_circle(cx, cy, r, fill):
        return f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}" />'

    # --- Draw Board ---
    svg_elements.append(f'<!-- Board -->')
    svg_elements.append(svg_rect(board_rect['x'], board_rect['y'], board_rect['w'], board_rect['h'], COLOR_BOARD_FILL, COLOR_BOARD_STROKE))
    svg_elements.append(svg_text(board_rect['x'] + board_rect['w']/2, board_rect['y'] + 30, board_rect['name'], FONT_COMP_TITLE, COLOR_BOARD_TEXT, weight="bold"))
    
    # --- Draw Peripherals & Connections ---
    
    # Helper to draw a stack
    def draw_stack(periphs, is_left_side):
        # Calculate starting Y to center the stack
        stack_h = get_total_stack_height(periphs)
        start_y = center_y - stack_h / 2
        
        current_y = start_y
        
        # Board pin tracking
        # We need to distribute board pins for these peripherals along the board edge
        # To avoid crossing, we should map them proportionally to the peripheral's Y position
        # But simpler: just stack them in the same order as peripherals
        
        # Calculate total pins for this side to determine board pin spacing
        total_pins = sum(len(p['pins']) for p in periphs)
        board_edge_x = board_rect['x'] if is_left_side else board_rect['x'] + board_rect['w']
        
        # Distribute pins on board edge
        # Available height on board
        avail_h = board_rect['h'] - PIN_MARGIN_TOP - PIN_MARGIN_BOTTOM
        # If we have many pins, spacing might need to shrink, or we use standard spacing
        # Let's use standard spacing and center the block of pins
        req_h = total_pins * PIN_SPACING
        pin_start_y = board_rect['y'] + (board_rect['h'] - req_h) / 2 + PIN_SPACING/2
        
        global_pin_idx = 0
        
        for p in periphs:
            # Peripheral Coords
            p_x = MARGIN_X if is_left_side else CANVAS_WIDTH - MARGIN_X - PERIPH_WIDTH
            p_y = current_y
            p_w = PERIPH_WIDTH
            p_h = p['height']
            
            # Draw Peripheral Box
            svg_elements.append(f'<!-- Peripheral: {p["name"]} -->')
            svg_elements.append(svg_rect(p_x, p_y, p_w, p_h, COLOR_PERIPH_FILL, COLOR_PERIPH_STROKE))
            svg_elements.append(svg_text(p_x + p_w/2, p_y + 25, p["name"], FONT_COMP_TITLE, COLOR_PERIPH_TEXT, weight="bold"))
            
            # Draw Pins and Connections
            # Peripheral Pin X: facing the board
            periph_pin_x = p_x + p_w if is_left_side else p_x
            
            # Text Anchors
            periph_text_anchor = "end" if is_left_side else "start"
            periph_text_x = periph_pin_x - 10 if is_left_side else periph_pin_x + 10
            
            board_text_anchor = "start" if is_left_side else "end"
            board_text_x = board_edge_x + 10 if is_left_side else board_edge_x - 10
            
            for i, pin in enumerate(p['pins']):
                # Periph Pin Y
                pp_y = p_y + PIN_MARGIN_TOP + i * PIN_SPACING
                
                # Board Pin Y
                bp_y = pin_start_y + global_pin_idx * PIN_SPACING
                global_pin_idx += 1
                
                # Determine Color
                line_color = COLOR_LINE_DEFAULT
                if pin['type'] == 'power': line_color = COLOR_LINE_POWER
                elif pin['type'] == 'gnd': line_color = COLOR_LINE_GND
                
                # Draw Connection (Bezier)
                svg_elements.append(svg_bezier(board_edge_x, bp_y, periph_pin_x, pp_y, line_color))
                
                # Draw Markers
                svg_elements.append(svg_circle(board_edge_x, bp_y, 4, line_color))
                svg_elements.append(svg_circle(periph_pin_x, pp_y, 4, line_color))
                
                # Draw Labels
                # Board Pin Label
                svg_elements.append(svg_text(board_text_x, bp_y, pin['board'], FONT_PIN, COLOR_BOARD_TEXT, anchor=board_text_anchor))
                
                # Periph Pin Label
                svg_elements.append(svg_text(periph_text_x, pp_y, pin['periph'], FONT_PIN, COLOR_PIN_TEXT, anchor=periph_text_anchor))

            current_y += p_h + 30 # Next peripheral

    draw_stack(left_peripherals, is_left_side=True)
    draw_stack(right_peripherals, is_left_side=False)

    # --- Final Output ---
    try:
        with open(output_file, "w") as f:
            f.write(f'<svg xmlns="http://www.w3.org/2000/svg" width="{CANVAS_WIDTH}" height="{CANVAS_HEIGHT}" viewBox="0 0 {CANVAS_WIDTH} {CANVAS_HEIGHT}" style="background-color: {COLOR_BG};">\n')
            # Title
            f.write(svg_text(CANVAS_WIDTH/2, 30, f"Device Diagram: {model.metadata.name}", FONT_TITLE, "#333333", weight="bold"))
            f.write("\n".join(svg_elements))
            f.write('\n</svg>')
        print(f"Successfully generated SVG: {output_file}")
    except Exception as e:
        print(f"Error writing SVG file: {e}")
