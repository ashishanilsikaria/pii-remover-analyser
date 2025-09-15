def list_to_html_ol(cell):
    if isinstance(cell, list):
        return "<ul>" + "".join(f"<li>{item}</li>" for item in cell) + "</ul>"
    return cell

