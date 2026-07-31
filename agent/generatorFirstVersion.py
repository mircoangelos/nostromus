import datetime
import os
from dotenv import load_dotenv

load_dotenv()
REPORTS_DIR = os.getenv("REPORTS_DIR", "reports")

def update_user_status(user_id: str, status: str):
    """simulation"""
    print(f"[DB ACTION] Usuario {user_id} actualizado a estado: {status}")
    return {"status": "success", "updated_user": user_id}

def generate_security_report(incident_details: str, severity: str):
    """Generates reports"""
    if not os.path.exists(REPORTS_DIR):
        os.makedirs(REPORTS_DIR)
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    report_id = f"REP_{timestamp}"
    file_path = os.path.join(REPORTS_DIR, f"{report_id}.txt")
    
    report_content = f"""
    NOSTROMUS SECURITY REPORT
    =========================
    ID: {report_id}
    Date: {datetime.datetime.now()}
    Severidad: {severity}
    Details: {incident_details}
    =========================
    Generado por: Nostromus Agent
    """
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(report_content)
    
    print(f"[REPORT GEN] File created: {file_path}")
    return {"report_id": report_id, "path": file_path}