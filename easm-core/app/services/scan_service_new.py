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
                "error_message": scan.error_message,
                "progress": 100 if scan.status == "completed" else (50 if scan.status == "running" else 0)
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
        try:
            # Create findings from scan results
            open_ports = results.get("open_ports", [])
            services = results.get("services", {})
            
            for port in open_ports:
                service_name = services.get(str(port), "unknown")
                
                finding = Finding(
                    id=str(uuid4()),
                    scan_id=scan_id,
                    target=results.get("target", "unknown"),
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
            
            self.db.commit()
            logger.info(f"Created {len(open_ports)} findings for scan {scan_id}")
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to process scan results: {e}")
            raise
