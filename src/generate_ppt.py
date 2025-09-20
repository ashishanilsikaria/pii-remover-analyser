import math
import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN, MSO_VERTICAL_ANCHOR, MSO_AUTO_SIZE

base_dir = os.path.dirname(__file__)


def create_presentation(data, output_filename):

    prs = Presentation()
    prs.slide_width = Inches(10)
    prs.slide_height = Inches(7.5)

    slide_layout_title = prs.slide_layouts[0]
    slide = prs.slides.add_slide(slide_layout_title)
    title = slide.shapes.title
    subtitle = slide.placeholders[1]
    title.text = "Automating File Cleansing and Analysis Leveraging AI"  # type: ignore
    subtitle.text = (  # type: ignore
        "Case Study Solution Presentation"
        "\nGroup Number: 45"
        "\nTeam Members: Ashish, John, Jane, Doe"
    )

    slide_layout_content = prs.slide_layouts[1]

    info_slides = [
        {
            "title": "Case Study Overview",
            "content": (
                "File Cleansing: Automatically detect and remove or mask all client-specific details and PII from various documents to ensure complete anonymization.\n\n"
                "Data Standardization: Pre-process diverse file formats (.jpeg, .png, .pdf, .xlsx, etc.) into a consistent, structured format suitable for analysis. \n\n"
                "Insight Extraction: Analyze the cleansed data to identify and extract meaningful security information, such as firewall rules, IAM policy statements, or IDS/IPS logs. The final output is presented in a standardized and readable format."
            ),
        },
        {
            "title": "Approach Taken",
            "content": "Populate this slide with the strategy you used to address the case challenges.",
        },
        # {
        #     "title": "Functional Design Diagram",
        #     "content": None,
        # },
    ]

    for info in info_slides:
        slide = prs.slides.add_slide(slide_layout_content)
        slide.shapes.title.text = info["title"]  # type: ignore
        content_shape = slide.placeholders[1]
        # if info["content"]:
        content_shape.text = info["content"]  # type: ignore
        for paragraph in content_shape.text_frame.paragraphs:  # type: ignore
            paragraph.font.size = Pt(20)

    system_design_slide = prs.slides.add_slide(prs.slide_layouts[5])
    system_design_slide.shapes.title.text = "Functional Design Diagram"  # type: ignore
    img_path = os.path.join(base_dir, "assets", "system_design.png")
    left = Inches(1)
    top = Inches(1.5)
    height = Inches(6)
    system_design_slide.shapes.add_picture(img_path, left, top, height=height)

    ppt_headers = ["File Name", "File Type", "File Description", "Key Findings"]
    rows_per_slide = 2
    num_data_slides = math.ceil(len(data) / rows_per_slide)

    slide_layout = prs.slide_layouts[5]

    for i in range(num_data_slides):
        slide = prs.slides.add_slide(slide_layout)
        title = slide.shapes.title
        title.text = "File Analysis Sample Output"  # type: ignore

        start_index = i * rows_per_slide
        end_index = start_index + rows_per_slide
        slide_data = data[start_index:end_index]

        num_rows_in_table = len(slide_data) + 1
        num_cols = 4
        left = Inches(0.25)
        top = Inches(1.5)
        width = Inches(9.5)
        height = Inches(5.5)

        table = slide.shapes.add_table(
            num_rows_in_table, num_cols, left, top, width, height
        ).table

        table.columns[0].width = Inches(1.4)
        table.columns[1].width = Inches(0.8)
        table.columns[2].width = Inches(3.6)
        table.columns[3].width = Inches(3.7)

        # Populate header row
        for col_idx, header_text in enumerate(ppt_headers):
            cell = table.cell(0, col_idx)
            cell.text = header_text
            p = cell.text_frame.paragraphs[0]
            p.font.bold = True
            p.font.size = Pt(14)
            p.alignment = PP_ALIGN.CENTER
            cell.vertical_anchor = MSO_VERTICAL_ANCHOR.MIDDLE
            # Set row height to auto-adjust to text content
        table.rows[0].height = Inches(0.7)  # Auto height for header row

        # Populate data rows
        for row_idx, record in enumerate(slide_data, start=1):
            # --- Column 1: File Name ---
            cell = table.cell(row_idx, 0)
            cell.text = record[0]

            # --- Column 2: File Type ---
            cell = table.cell(row_idx, 1)
            cell.text = record[1]

            # Set formatting for simple text cells (File Name, File Type)
            for col_idx in [0, 1]:
                cell = table.cell(row_idx, col_idx)
                # cell.vertical_anchor = MSO_VERTICAL_ANCHOR.TOP
                tf = cell.text_frame
                tf.auto_size = MSO_AUTO_SIZE.TEXT_TO_FIT_SHAPE
                tf.paragraphs[0].font.size = Pt(11)

            # --- Column 3: File Description (merged with heading) ---
            cell = table.cell(row_idx, 2)
            cell.vertical_anchor = MSO_VERTICAL_ANCHOR.TOP
            tf = cell.text_frame
            # tf.clear()
            tf.auto_size = MSO_AUTO_SIZE.TEXT_TO_FIT_SHAPE  # Apply autofit

            p_heading = tf.paragraphs[0]
            p_heading.text = record[2]
            p_heading.font.bold = True
            p_heading.font.size = Pt(11)

            p_desc = tf.add_paragraph()
            p_desc.text = record[3]
            p_desc.font.size = Pt(10)

            # --- Column 4: Key Findings (bullet points) ---
            cell = table.cell(row_idx, 3)
            cell.vertical_anchor = MSO_VERTICAL_ANCHOR.TOP
            tf = cell.text_frame
            # tf.clear()
            tf.auto_size = MSO_AUTO_SIZE.TEXT_TO_FIT_SHAPE  # Apply autofit
            first = 0
            for finding in record[4]:
                if first == 0:
                    p_finding = tf.paragraphs[0]
                    p_finding.text = f"• {finding}"
                    p_finding.level = 0
                    p_finding.font.size = Pt(10)
                    first = 1
                else:
                    p_finding = tf.add_paragraph()
                    p_finding.text = f"• {finding}"
                    p_finding.level = 0
                    p_finding.font.size = Pt(10)

    prs.save(output_filename)


if __name__ == "__main__":
    sample_data = [
        [
            "File_001.png",
            ".png",
            "Access Control System (Card Reader)",
            "The image depicts an individual using an RFID/NFC-based access control card to gain entry through a card reader, likely to a restricted area such as an IDF/Electrical room. The system is designed for physical security and access management.",
            [
                "The use of a physical access card with a photo ID enhances security by allowing visual verification of the cardholder.",
                "Access control systems like this provide granular control over who can enter specific areas and when, improving overall physical security.",
                "The room designation 'IDF/ELECTRICAL' indicates a critical infrastructure space, underscoring the importance of restricted access.",
                "Potential vulnerabilities include card cloning, loss or theft of access cards, or tailgating if not properly enforced.",
            ],
        ],
        [
            "File_002.png",
            ".png",
            "Biometric Access Control System",
            "The image displays a multi-factor authentication access control system featuring a keypad, a fingerprint scanner, and a camera, likely used for secure entry into a building or restricted area.",
            [
                "The presence of a fingerprint scanner indicates biometric authentication, which offers a higher level of security compared to traditional key or card systems.",
                "The keypad suggests an additional layer of security, possibly requiring a PIN in combination with biometrics (multi-factor authentication).",
                "The integrated camera could be used for facial recognition or recording individuals attempting to gain access, adding an extra layer of surveillance and identity verification.",
                "The system enhances physical security by controlling and monitoring entry points, deterring unauthorized access and providing an audit trail of entries.",
            ],
        ],
        [
            "File_003.png",
            ".png",
            "Visitors Log Book",
            "The image shows a traditional paper-based visitors log book, used to record visitor details, reasons for visit, and entry/exit times. It highlights manual data entry and the physical storage of visitor information.",
            [
                "Privacy concerns exist as visitor names and reasons for visit are visible to subsequent visitors.",
                "Data accuracy can be compromised due to illegible handwriting or human error during manual entry.",
                "Lack of advanced security features like access control, audit trails, or real-time alerts.",
                "Physical log books are susceptible to damage, loss, or unauthorized alteration, and do not offer robust data backup.",
            ],
        ],
        [
            "File_001.png",
            ".png",
            "Access Control System (Card Reader)",
            "The image depicts an individual using an RFID/NFC-based access control card to gain entry through a card reader, likely to a restricted area such as an IDF/Electrical room. The system is designed for physical security and access management.",
            [
                "The use of a physical access card with a photo ID enhances security by allowing visual verification of the cardholder.",
                "Access control systems like this provide granular control over who can enter specific areas and when, improving overall physical security.",
                "The room designation 'IDF/ELECTRICAL' indicates a critical infrastructure space, underscoring the importance of restricted access.",
                "Potential vulnerabilities include card cloning, loss or theft of access cards, or tailgating if not properly enforced.",
            ],
        ],
        [
            "File_002.png",
            ".png",
            "Biometric Access Control System",
            "The image displays a multi-factor authentication access control system featuring a keypad, a fingerprint scanner, and a camera, likely used for secure entry into a building or restricted area.",
            [
                "The presence of a fingerprint scanner indicates biometric authentication, which offers a higher level of security compared to traditional key or card systems.",
                "The keypad suggests an additional layer of security, possibly requiring a PIN in combination with biometrics (multi-factor authentication).",
                "The integrated camera could be used for facial recognition or recording individuals attempting to gain access, adding an extra layer of surveillance and identity verification.",
                "The system enhances physical security by controlling and monitoring entry points, deterring unauthorized access and providing an audit trail of entries.",
            ],
        ],
        [
            "File_003.png",
            ".png",
            "Visitors Log Book",
            "The image shows a traditional paper-based visitors log book, used to record visitor details, reasons for visit, and entry/exit times. It highlights manual data entry and the physical storage of visitor information.",
            [
                "Privacy concerns exist as visitor names and reasons for visit are visible to subsequent visitors.",
                "Data accuracy can be compromised due to illegible handwriting or human error during manual entry.",
                "Lack of advanced security features like access control, audit trails, or real-time alerts.",
                "Physical log books are susceptible to damage, loss, or unauthorized alteration, and do not offer robust data backup.",
            ],
        ],
    ]
    create_presentation(sample_data, "case_study_presentation.pptx")
