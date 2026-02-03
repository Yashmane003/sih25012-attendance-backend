import qrcode
import json
from io import BytesIO
from django.core.files import File

def generate_student_qr(student):
    qr_payload = {
        "student_uid": str(student.student_uid),
        "class_id": student.student_class.id,
        "verification_key": student.verification_key
    }

    qr_data = json.dumps(qr_payload)

    qr = qrcode.make(qr_data)
    buffer = BytesIO()
    qr.save(buffer, format="PNG")

    filename = f"student_{student.student_uid}.png"
    student.qr_code_image.save(filename, File(buffer), save=False)
