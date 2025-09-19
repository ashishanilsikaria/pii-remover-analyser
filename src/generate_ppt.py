import math
from pptx import Presentation
from pptx.util import Inches, Pt


def estimate_row_content_lines(
    record, chars_per_line_desc=55, chars_per_line_findings=60
):

    heading_lines = math.ceil(len(record[2]) / chars_per_line_desc)
    desc_lines = math.ceil(len(record[3]) / chars_per_line_desc)

    findings_lines = 0
    for finding in record[4]:
        findings_lines += math.ceil(len(finding) / chars_per_line_findings)

    return max(heading_lines + desc_lines, findings_lines) + 2


def create_presentation(data, output_filename):

    prs = Presentation()
    prs.slide_width = Inches(10)
    prs.slide_height = Inches(7.5)

    slide_layout_title = prs.slide_layouts[0]
    slide = prs.slides.add_slide(slide_layout_title)
    title = slide.shapes.title
    subtitle = slide.placeholders[1]
    title.text = "Automating File Cleansing and Analysis Leveraging AI"
    subtitle.text = (
        "Case Study Solution Presentation"
        "\nGroup Number: 45"
        "\nTeam Members: Ashish, John, Jane, Doe"
    )

    slide_layout_content = prs.slide_layouts[1]
    static_slides_info = [
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
        {
            "title": "Functional Design Diagram",
            "content": "Populate this slide with the functional design diagram of your application...",
        },
    ]

    for info in static_slides_info:
        slide = prs.slides.add_slide(slide_layout_content)
        slide.shapes.title.text = info["title"]
        content_shape = slide.placeholders[1]
        content_shape.text = info["content"]
        for paragraph in content_shape.text_frame.paragraphs:
            paragraph.font.size = Pt(20)

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
    ]
    create_presentation(sample_data, "case_study_presentation.pptx")
