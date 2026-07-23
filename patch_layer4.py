import os

filepath = '/home/ahmed/hexstrike-ai/hexstrike_server.py'
with open(filepath, 'r') as f:
    content = f.read()

layer4_code = """
from enum import Enum

class ScanCompletionStatus(Enum):
    FAILED_NO_TOOLS_RAN = "FAILED_NO_TOOLS_RAN"
    DEGRADED = "DEGRADED"
    SUCCESS_CLEAN = "SUCCESS_CLEAN"
    SUCCESS = "SUCCESS"

def get_findings_count(scan_id: str) -> int:
    try:
        import psycopg2
        conn = psycopg2.connect("postgresql://hexstrike:hexstrike@127.0.0.1:5432/hexstrike")
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM findings WHERE scan_id = %s", (scan_id,))
        count = cur.fetchone()[0]
        cur.close()
        conn.close()
        return count
    except Exception as e:
        print(f"DB Error get_findings_count: {e}")
        return 0

def get_tools_invoked_count(scan_id: str) -> int:
    try:
        import psycopg2
        conn = psycopg2.connect("postgresql://hexstrike:hexstrike@127.0.0.1:5432/hexstrike")
        cur = conn.cursor()
        cur.execute("SELECT COUNT(DISTINCT tool_name) FROM tool_logs WHERE scan_id = %s", (scan_id,))
        count = cur.fetchone()[0]
        cur.close()
        conn.close()
        return count
    except Exception as e:
        print(f"DB Error get_tools_invoked_count: {e}")
        return 0

def validate_scan_completion(scan_id: str, target: str) -> ScanCompletionStatus:
    findings_count = get_findings_count(scan_id)
    tools_invoked = get_tools_invoked_count(scan_id)
    tools_expected = get_expected_tool_count(target)

    if tools_invoked == 0:
        return ScanCompletionStatus.FAILED_NO_TOOLS_RAN
    if tools_invoked < tools_expected * 0.5:
        return ScanCompletionStatus.DEGRADED
    if findings_count == 0 and tools_invoked >= tools_expected:
        return ScanCompletionStatus.SUCCESS_CLEAN
    return ScanCompletionStatus.SUCCESS

"""

# Append it to the file before if __name__ == "__main__":
content = content.replace('if __name__ == "__main__":', layer4_code + '\nif __name__ == "__main__":')

with open(filepath, 'w') as f:
    f.write(content)
print("Patched Layer 4 into hexstrike_server.py")
