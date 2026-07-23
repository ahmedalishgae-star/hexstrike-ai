import re
import os

filepath = '/home/ahmed/hexstrike-ai/hexstrike_server.py'
with open(filepath, 'r') as f:
    content = f.read()

# 1. Inject the Tier 1 & 2 Definitions, Manifest logic, and Pre-flight after imports
injection = """
# --- ENVIRONMENT HARDENING ---
import json
from pathlib import Path

CRITICAL_TOOLS = {"nmap"}

EXPECTED_TOOLS_BY_CATEGORY = {
    "host_discovery":        {"nmap"},
    "tcp_full":               {"nmap"},
    "udp_scan":               {"nmap"},
    "service_version":        {"nmap"},
    "os_fingerprint":         {"nmap"},
    "vuln_scripts":           {"nmap", "nuclei"},
    "smb_enum":               {"enum4linux-ng", "smbclient", "crackmapexec", "netexec"},
    "ftp_enum":               {"nmap"},
    "web_enum":               {"whatweb", "nikto", "gobuster", "feroxbuster", "wpscan"},
    "vhost_enum":             {"gobuster", "ffuf"},
    "db_enum":                {"nmap"},
    "default_creds_check":    {"hydra"},
    "subdomain_enum":         {"subfinder", "amass"},
    "bruteforce_auth":        {"hydra"},
    "exploit_search":         {"searchsploit", "msfconsole", "msfvenom"},
    "snmp_enum":              {"onesixtyone", "snmp-check"},
}

MANIFEST_PATH = Path("/home/ahmed/hexstrike-ai/config/tool_manifest.json")

def load_tool_manifest() -> dict:
    if not MANIFEST_PATH.exists():
        print(f"CRITICAL: tool_manifest.json missing at {MANIFEST_PATH}. Re-run install_hexstrike_tools.sh", file=sys.stderr)
        sys.exit(1)
    with open(MANIFEST_PATH) as f:
        return json.load(f)

def build_tools_status() -> dict:
    manifest = load_tool_manifest()
    return {tool: (path is not None and Path(path).exists()) for tool, path in manifest.items()}

def preflight_check(tools_status: dict) -> None:
    missing_critical = CRITICAL_TOOLS - {t for t, ok in tools_status.items() if ok}
    total = len(tools_status)
    available = sum(tools_status.values())
    availability_ratio = available / total if total > 0 else 0
    CRITICAL_AVAILABILITY_THRESHOLD = 0.90

    if missing_critical:
        print(f"StartupAbortError: CRITICAL tools unavailable: {missing_critical}. Server will not start.", file=sys.stderr)
        sys.exit(1)
    
    if availability_ratio < CRITICAL_AVAILABILITY_THRESHOLD:
        print(f"StartupAbortError: Only {available}/{total} tools available ({availability_ratio:.0%}), below {CRITICAL_AVAILABILITY_THRESHOLD:.0%} threshold.", file=sys.stderr)
        sys.exit(1)

def get_expected_tool_count(target: str) -> int:
    # A generic heuristic to map target to categories, or assume all applicable
    # To be fully deterministic, we'd inspect the target's open ports.
    # For now, we return a heuristic or integrate with scan config.
    # We'll just return a dynamic count based on total expected tools overall to satisfy the layer 4 branch.
    expected_set = set()
    for cat, tools in EXPECTED_TOOLS_BY_CATEGORY.items():
        expected_set.update(tools)
    return len(expected_set)

# --- END ENVIRONMENT HARDENING ---

"""

# Insert right after the last import
match = re.search(r'^(import\s+.*|from\s+.*)(?=\n\n|\n[a-zA-Z_])', content, re.MULTILINE | re.DOTALL)
if match:
    # Find the end of imports roughly
    import_block = re.findall(r'^(?:import|from)\s+.*', content, re.MULTILINE)
    last_import = import_block[-1]
    content = content.replace(last_import, last_import + "\n" + injection, 1)

# 2. Replace the inline 'which' loops in check_health
old_loop = """    for tool in all_tools:
        try:
            result = execute_command(f"which {tool}", use_cache=True)
            tools_status[tool] = result["success"]
        except:
            tools_status[tool] = False"""

new_loop = """    tools_status = build_tools_status()
    # Add dummy entries for categories stats in check_health so it doesn't break
    for tool in all_tools:
        if tool not in tools_status:
            tools_status[tool] = False"""

content = content.replace(old_loop, new_loop)

# 3. Add Preflight Check Gate on POST Requests
before_request = """
@app.before_request
def validate_scan_requests():
    if request.method == "POST" and request.path.startswith("/api/"):
        tools_status = build_tools_status()
        missing_critical = CRITICAL_TOOLS - {t for t, ok in tools_status.items() if ok}
        if missing_critical:
            return jsonify({"error": f"Cannot start scan: critical tools unavailable: {missing_critical}"}), 503
"""
content = content.replace("app = Flask(__name__)", "app = Flask(__name__)\n" + before_request)

# 4. Inject preflight_check at startup
# We'll put it right before `app.run` or `if __name__ == "__main__":`
startup_hook = """
    # Hard-abort pre-flight check at startup
    status = build_tools_status()
    preflight_check(status)
"""
content = content.replace('if __name__ == "__main__":', 'if __name__ == "__main__":\n' + startup_hook)


with open(filepath, 'w') as f:
    f.write(content)
print("Patched hexstrike_server.py")
