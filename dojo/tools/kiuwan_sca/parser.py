import json
import hashlib
import io

from dojo.models import Finding

__author__ = "mwager"

class KiuwanSCAParser(object):
    SEVERITY = {
        "-" : "Low",
        "LOW" : "Low",
        "MEDIUM" : "Medium",
        "HIGH" : "High",
        "CRITICAL" : "Critical",
        "Low" : "Low",
        "Medium" : "Medium",
        "High" : "High",
        "Critical" : "Critical"
    }

    def get_scan_types(self):
        return ["Kiuwan SCA Scan"]

    def get_label_for_scan_types(self, scan_type):
        return scan_type

    def get_description_for_scan_types(self, scan_type):
        return "Import Kiuwan Insights Scan in JSON format. Export as JSON using Kiuwan REST API."

    def get_findings(self, filename, test):
        data = json.load(filename)

        dupes = dict()
        for row in data:
            # if a finding was "muted" in the Kiuwan UI, we ignore it (e.g. marked as false positive)
            if row["muted"] == True:
                continue

            finding = Finding(test=test)
            finding.unique_id_from_tool = row["id"]
            finding.title = row["cve"]
            finding.cve = row["cve"]
            finding.description = row["description"]
            finding.severity = self.SEVERITY[row["securityRisk"]]

            if "components" in row and len(row["components"]) > 0:
                finding.component_name = row["components"][0]["artifact"]
                finding.component_version = row["components"][0]["version"]

            if "cwe" in row:
                try:
                    finding.cwe = int(row["cwe"].replace("CWE-", ""))
                except Exception:
                    pass

            if "cVSSv3BaseScore" in row:
                finding.cvssv3_score = float(row["cVSSv3BaseScore"])

            finding.references = "See Kiuwan Web UI"
            finding.mitigation = "See Kiuwan Web UI"
            finding.static_finding = True

            key = hashlib.sha256(
                (
                    finding.cve
                    + "|"
                    + finding.severity
                    + "|"
                    + str(finding.cwe)
                ).encode("utf-8")
            ).hexdigest()

            if key not in dupes:
                dupes[key] = finding

        return list(dupes.values())