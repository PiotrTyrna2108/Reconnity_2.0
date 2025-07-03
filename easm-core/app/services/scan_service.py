from typing import Dict, Any, List, Optional
from uuid import uuid4
from datetime import datetime
from sqlalchemy.orm import Session
from ..core.logging import get_logger
from ..models import Scan, Asset, Finding
from ..risk_engine import RiskEngine

logger = get_logger(__name__)

class ScanService:
    """
    Service for managing scan operations with database persistence
    """
    
    def __init__(self, db: Session = None):
        self.db = db
    
    async def create_scan(self, target: str, scanner: str, options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Create a new scan request and save to database"""
        scan_id = str(uuid4())
        
        # Create database session if not provided
        if not self.db:
            from ..database import SessionLocal
            self.db = SessionLocal()
            should_close = True
        else:
            should_close = False
        
        try:
            # Create new scan record
            scan_record = Scan(
                id=scan_id,
                target=target,
                scanner=scanner,
                status="queued",
                created_at=datetime.utcnow(),
                options=options or {},
            )
            
            # Save to database
            self.db.add(scan_record)
            self.db.commit()
            self.db.refresh(scan_record)
            
            logger.info(
                f"Scan created in database",
                scan_id=scan_id,
                target=target,
                scanner=scanner
            )
            
            return {
                "scan_id": scan_id,
                "status": "queued",
                "message": f"Scan queued for target {target}"
            }
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to create scan: {e}")
            raise
        finally:
            if should_close:
                self.db.close()
    
    async def get_scan_status(self, scan_id: str) -> Optional[Dict[str, Any]]:
        """Get scan status and results from database"""
        if not self.db:
            from ..database import SessionLocal
            self.db = SessionLocal()
            should_close = True
        else:
            should_close = False
            
        try:
            scan = self.db.query(Scan).filter(Scan.id == scan_id).first()
            
            if not scan:
                logger.warning(f"Scan not found in database: {scan_id}")
                return None
                
            # Convert to dictionary
            scan_data = {
                "scan_id": scan.id,
                "target": scan.target,
                "scanner": scan.scanner,
                "status": scan.status,
                "created_at": scan.created_at.isoformat() if scan.created_at else None,
                "started_at": scan.started_at.isoformat() if scan.started_at else None,
                "completed_at": scan.completed_at.isoformat() if scan.completed_at else None,
                "options": scan.options,
                "results": scan.results,
                "error": scan.error_message,  # Map to error as expected by ScanStatus schema
                "progress": 100 if scan.status == "completed" else (50 if scan.status == "running" else 0),
                "findings": None,  # Initialize with None, will be populated if completed
                "risk_score": None  # Initialize with None, will be populated if completed
            }
            
            # Get findings if scan is completed
            if scan.status == "completed":
                findings = self.db.query(Finding).filter(Finding.scan_id == scan_id).all()
                scan_data["findings"] = [
                    {
                        "id": f.id,
                        "finding_type": f.finding_type,
                        "severity": f.severity,
                        "title": f.title,
                        "description": f.description,
                        "port": f.port,
                        "service": f.service,
                        "finding_metadata": f.finding_metadata
                    }
                    for f in findings
                ]
                
                # Get risk score for target
                target = scan.target
                risk_score = self.db.query(RiskScore).filter(RiskScore.target == target).first()
                if risk_score:
                    scan_data["risk_score"] = {
                        "score": risk_score.score,
                        "level": self._get_risk_level(risk_score.score),
                        "factors": risk_score.factors,
                        "calculated_at": risk_score.calculated_at.isoformat() if risk_score.calculated_at else None
                    }
            
            return scan_data
            
        except Exception as e:
            logger.error(f"Failed to get scan status: {e}")
            raise
        finally:
            if should_close:
                self.db.close()

    async def complete_scan(self, scan_id: str, results: Dict[str, Any]) -> bool:
        """Mark scan as completed with results"""
        if not self.db:
            from ..database import SessionLocal
            self.db = SessionLocal()
            should_close = True
        else:
            should_close = False
            
        try:
            scan = self.db.query(Scan).filter(Scan.id == scan_id).first()
            
            if not scan:
                logger.warning(f"Scan not found for completion: {scan_id}")
                return False

            # Update scan record
            scan.status = "completed"
            scan.completed_at = datetime.utcnow()
            scan.results = results
            
            self.db.commit()

            # Process findings and calculate risk
            await self._process_scan_results(scan_id, results)
            
            logger.info(f"Scan completed in database", scan_id=scan_id)
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to complete scan: {e}")
            raise
        finally:
            if should_close:
                self.db.close()

    async def fail_scan(self, scan_id: str, error: str) -> bool:
        """Mark scan as failed"""
        if not self.db:
            from ..database import SessionLocal
            self.db = SessionLocal()
            should_close = True
        else:
            should_close = False
            
        try:
            scan = self.db.query(Scan).filter(Scan.id == scan_id).first()
            
            if not scan:
                logger.warning(f"Scan not found for failure: {scan_id}")
                return False

            scan.status = "failed"
            scan.completed_at = datetime.utcnow()
            scan.error_message = error
            
            self.db.commit()

            logger.error(f"Scan failed in database", scan_id=scan_id, error=error)
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to mark scan as failed: {e}")
            raise
        finally:
            if should_close:
                self.db.close()

    async def _process_scan_results(self, scan_id: str, results: Dict[str, Any]):
        """Process scan results and extract findings"""
        start_time = datetime.utcnow()
        try:
            # Create findings from scan results
            open_ports = results.get("open_ports", [])
            services = results.get("services", {})
            target = results.get("target", "unknown")
            scan_findings = []
            
            for port in open_ports:
                service_info = services.get(str(port), "unknown")
                
                # Extract service name from service info (handle both string and dict formats)
                if isinstance(service_info, dict):
                    service_name = service_info.get("name", "unknown")
                else:
                    service_name = service_info if service_info else "unknown"
                
                finding = Finding(
                    id=str(uuid4()),
                    scan_id=scan_id,
                    target=target,
                    finding_type="open_port",
                    severity="medium",
                    title=f"Open port {port}",
                    description=f"Port {port} is open and running {service_name}",
                    port=port,
                    service=service_name,
                    created_at=datetime.utcnow(),
                    finding_metadata={"scanner": results.get("scanner")}
                )
                
                self.db.add(finding)
                scan_findings.append({
                    "finding_type": "open_port",
                    "severity": "medium",
                    "port": port,
                    "service": service_name
                })
            
            self.db.commit()
            logger.info(
                f"Created {len(open_ports)} findings for scan {scan_id}",
                scan_id=scan_id,
                finding_count=len(open_ports),
                processing_time=f"{(datetime.utcnow() - start_time).total_seconds():.2f}s"
            )
            
            # Create or update asset
            await self._create_or_update_asset(target, results)
            
            # Calculate risk score and save to database
            await self._calculate_and_save_risk_score(target, scan_findings)
            
        except Exception as e:
            self.db.rollback()
            logger.error(
                f"Failed to process scan results",
                error=str(e),
                scan_id=scan_id,
                processing_time=f"{(datetime.utcnow() - start_time).total_seconds():.2f}s"
            )
            raise
            
    async def _create_or_update_asset(self, target: str, results: Dict[str, Any]):
        """Create or update asset based on scan results"""
        try:
            # Determine asset type based on target format
            import re
            
            asset_type = "unknown"
            if re.match(r'^\d+\.\d+\.\d+\.\d+$', target):
                asset_type = "ip"
            elif re.match(r'^[a-zA-Z0-9][-a-zA-Z0-9.]+\.[a-zA-Z]{2,}$', target):
                asset_type = "domain"
            
            # Check if asset exists
            asset = self.db.query(Asset).filter(Asset.target == target).first()
            
            if asset:
                # Update existing asset
                asset.updated_at = datetime.utcnow()
                asset.asset_metadata = {
                    **(asset.asset_metadata or {}),
                    "last_scan_id": results.get("scan_id"),
                    "last_scan_time": datetime.utcnow().isoformat()
                }
                logger.info(f"Updated asset in database", target=target, asset_type=asset_type)
            else:
                # Create new asset
                asset = Asset(
                    id=str(uuid4()),
                    target=target,
                    asset_type=asset_type,
                    status="active",
                    created_at=datetime.utcnow(),
                    asset_metadata={
                        "first_scan_id": results.get("scan_id"),
                        "first_scan_time": datetime.utcnow().isoformat(),
                        "discovery_method": results.get("scanner", "unknown")
                    }
                )
                self.db.add(asset)
                logger.info(
                    f"Created new asset in database",
                    target=target,
                    asset_type=asset_type,
                    asset_id=asset.id
                )
                
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to create/update asset: {e}")
            return False
            
    async def _calculate_and_save_risk_score(self, target: str, findings: List[Dict[str, Any]]):
        """Calculate risk score and save to database"""
        try:
            # Calculate risk score
            start_time = datetime.utcnow()
            risk_data = RiskEngine.calculate_asset_risk(findings)
            
            # Create risk score record
            from datetime import timedelta
            
            risk_score = self.db.query(RiskScore).filter(RiskScore.target == target).first()
            
            if risk_score:
                # Update existing risk score
                risk_score.score = risk_data["score"]
                risk_score.factors = risk_data["factors"]
                risk_score.calculated_at = datetime.utcnow()
                risk_score.expires_at = datetime.utcnow() + timedelta(days=30)
            else:
                # Create new risk score
                risk_score = RiskScore(
                    id=str(uuid4()),
                    target=target,
                    score=risk_data["score"],
                    factors=risk_data["factors"],
                    calculated_at=datetime.utcnow(),
                    expires_at=datetime.utcnow() + timedelta(days=30)
                )
                self.db.add(risk_score)
                
            self.db.commit()
            
            logger.info(
                f"Calculated and saved risk score",
                target=target,
                score=risk_data["score"],
                level=risk_data["level"],
                processing_time=f"{(datetime.utcnow() - start_time).total_seconds():.2f}s"
            )
            return True
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to calculate risk score: {e}")
            return False
        
    def _get_risk_level(self, score: int) -> str:
        """Convert numeric risk score to text level"""
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
