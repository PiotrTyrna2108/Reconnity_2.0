from typing import Dict, Any, List
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class RiskEngine:
    """
    Risk scoring engine for EASM findings
    Calculates risk scores based on various factors
    """
    
    # Risk factors and their weights
    RISK_WEIGHTS = {
        "open_ports": 0.3,
        "services": 0.25,
        "vulnerabilities": 0.35,
        "exposure": 0.1
    }
    
    # Port risk levels
    HIGH_RISK_PORTS = {21, 23, 135, 139, 445, 1433, 1521, 3389, 5432, 5984, 6379, 9200, 27017}
    MEDIUM_RISK_PORTS = {22, 25, 53, 80, 110, 143, 443, 993, 995, 3306, 5432}
    
    @classmethod
    def calculate_asset_risk(cls, findings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate risk score for an asset based on its findings
        
        Args:
            findings: List of finding dictionaries
            
        Returns:
            Dictionary with risk score and factors
        """
        if not findings:
            return {
                "score": 0,
                "level": "none",
                "factors": {},
                "calculated_at": datetime.utcnow().isoformat()
            }
        
        # Calculate individual risk factors
        port_risk = cls._calculate_port_risk(findings)
        service_risk = cls._calculate_service_risk(findings)
        vuln_risk = cls._calculate_vulnerability_risk(findings)
        exposure_risk = cls._calculate_exposure_risk(findings)
        
        # Calculate weighted total
        total_score = (
            port_risk * cls.RISK_WEIGHTS["open_ports"] +
            service_risk * cls.RISK_WEIGHTS["services"] +
            vuln_risk * cls.RISK_WEIGHTS["vulnerabilities"] +
            exposure_risk * cls.RISK_WEIGHTS["exposure"]
        )
        
        # Normalize to 0-100 scale
        normalized_score = min(100, max(0, int(total_score)))
        
        return {
            "score": normalized_score,
            "level": cls._get_risk_level(normalized_score),
            "factors": {
                "open_ports": port_risk,
                "services": service_risk,
                "vulnerabilities": vuln_risk,
                "exposure": exposure_risk
            },
            "calculated_at": datetime.utcnow().isoformat()
        }
    
    @classmethod
    def _calculate_port_risk(cls, findings: List[Dict[str, Any]]) -> float:
        """Calculate risk based on open ports"""
        open_ports = []
        
        for finding in findings:
            if finding.get("finding_type") == "open_port" and finding.get("port"):
                open_ports.append(finding["port"])
        
        if not open_ports:
            return 0.0
        
        risk_score = 0.0
        
        for port in open_ports:
            if port in cls.HIGH_RISK_PORTS:
                risk_score += 30
            elif port in cls.MEDIUM_RISK_PORTS:
                risk_score += 15
            else:
                risk_score += 5
        
        # Cap at 100
        return min(100.0, risk_score)
    
    @classmethod
    def _calculate_service_risk(cls, findings: List[Dict[str, Any]]) -> float:
        """Calculate risk based on detected services"""
        services = []
        
        for finding in findings:
            if finding.get("finding_type") == "service" and finding.get("service"):
                services.append(finding["service"].lower())
        
        if not services:
            return 0.0
        
        # High-risk services
        high_risk_services = {
            "ftp", "telnet", "rlogin", "rsh", "finger", "tftp",
            "mysql", "postgresql", "mongodb", "redis", "elasticsearch",
            "rdp", "vnc", "ssh", "smb"
        }
        
        risk_score = 0.0
        
        for service in services:
            if any(hrs in service for hrs in high_risk_services):
                risk_score += 20
            else:
                risk_score += 5
        
        return min(100.0, risk_score)
    
    @classmethod
    def _calculate_vulnerability_risk(cls, findings: List[Dict[str, Any]]) -> float:
        """Calculate risk based on vulnerabilities"""
        vulnerabilities = [
            f for f in findings 
            if f.get("finding_type") == "vulnerability"
        ]
        
        if not vulnerabilities:
            return 0.0
        
        risk_score = 0.0
        
        for vuln in vulnerabilities:
            severity = vuln.get("severity", "low").lower()
            
            if severity == "critical":
                risk_score += 40
            elif severity == "high":
                risk_score += 25
            elif severity == "medium":
                risk_score += 15
            elif severity == "low":
                risk_score += 5
        
        return min(100.0, risk_score)
    
    @classmethod
    def _calculate_exposure_risk(cls, findings: List[Dict[str, Any]]) -> float:
        """Calculate risk based on internet exposure"""
        # This is a simplified calculation
        # In practice, you'd check if the asset is internet-facing
        
        open_ports = len([
            f for f in findings 
            if f.get("finding_type") == "open_port"
        ])
        
        if open_ports == 0:
            return 0.0
        elif open_ports <= 3:
            return 20.0
        elif open_ports <= 10:
            return 50.0
        else:
            return 80.0
    
    @classmethod
    def _get_risk_level(cls, score: int) -> str:
        """Convert numeric score to risk level"""
        if score >= 80:
            return "critical"
        elif score >= 60:
            return "high"
        elif score >= 40:
            return "medium"
        elif score >= 20:
            return "low"
        else:
            return "info"
