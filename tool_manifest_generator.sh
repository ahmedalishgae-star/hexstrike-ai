#!/bin/bash
# tool_manifest_generator.sh — run at the end of install_hexstrike_tools.sh
MANIFEST="/home/ahmed/hexstrike-ai/config/tool_manifest.json"
mkdir -p "$(dirname "$MANIFEST")"

TOOLS=(
  aircrack-ng aireplay-ng airmon-ng airodump-ng amass anew angr arjun arp-scan autorecon binwalk 
  censys-cli checkov checksec curl dalfox dirb dirsearch docker-bench-security enum4linux enum4linux-ng 
  evil-winrm exiftool feroxbuster ffuf fierce file foremost gau gdb gobuster hakrawler hash-identifier 
  hashcat httpie httpx hydra jaeles john jwt-analyzer katana kismet kube-hunter masscan medusa 
  msfconsole msfvenom nbtscan nikto nmap nuclei objdump one-gadget ophcrack outguess paramspider 
  photorec prowler pwninit pwntools qsreplace radare2 responder ropgadget ropper rpcclient rustscan 
  scalpel scout-suite searchsploit sherlock shodan-cli smbmap social-analyzer spiderfoot sqlmap 
  steghide strings subfinder tcpdump terrascan testdisk trivy tshark uro vol volatility3 wafw00f 
  waybackurls wfuzz wireshark wpscan x8 xsser xxd zaproxy zsteg whatweb nxc onesixtyone snmpcheck
)

# Source every possible install location so this script sees what an interactive shell would see
export PATH="/home/ahmed/hexstrike-ai/bin:$PATH:/usr/local/go/bin:/home/ahmed/go/bin:/home/ahmed/.cargo/bin:/home/ahmed/.local/bin:/opt/metasploit-framework/bin:/home/ahmed/tools/patator:/home/ahmed/tools/dnsenum:/home/ahmed/tools/libc-database:/home/ahmed/tools/hashcat-utils/src:/home/ahmed/tools/jwt_tool"

echo "{" > "$MANIFEST"
first=true
for tool in "${TOOLS[@]}"; do
    resolved="$(command -v "$tool" 2>/dev/null)"
    [ "$first" = true ] && first=false || echo "," >> "$MANIFEST"
    if [ -n "$resolved" ]; then
        printf '  "%s": "%s"' "$tool" "$resolved" >> "$MANIFEST"
    else
        printf '  "%s": null' "$tool" >> "$MANIFEST"
        echo "WARNING: $tool not found during manifest generation" >&2
    fi
done
echo "" >> "$MANIFEST"
echo "}" >> "$MANIFEST"

echo "Tool manifest written to $MANIFEST"
