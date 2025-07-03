import asyncio
import aiohttp
import time
import statistics
from typing import List, Dict, Any

class PerformanceTester:
    """Performance testing for EASM API"""
    
    def __init__(self, base_url: str = "http://localhost:8080"):
        self.base_url = base_url
        self.results: List[Dict[str, Any]] = []
    
    async def test_scan_creation_performance(self, concurrent_requests: int = 10, total_requests: int = 100):
        """Test concurrent scan creation performance"""
        
        print(f"🚀 Testing scan creation with {concurrent_requests} concurrent requests...")
        print(f"📊 Total requests: {total_requests}")
        
        semaphore = asyncio.Semaphore(concurrent_requests)
        
        async def create_scan(session: aiohttp.ClientSession, request_id: int):
            async with semaphore:
                start_time = time.time()
                
                scan_data = {
                    "target": f"192.168.1.{(request_id % 254) + 1}",
                    "scanner": "nmap",
                    "options": {"ports": "80,443"}
                }
                
                try:
                    async with session.post(
                        f"{self.base_url}/api/v1/scan",
                        json=scan_data
                    ) as response:
                        result = await response.json()
                        duration = time.time() - start_time
                        
                        return {
                            "request_id": request_id,
                            "duration": duration,
                            "status_code": response.status,
                            "success": response.status == 200,
                            "scan_id": result.get("scan_id") if response.status == 200 else None
                        }
                        
                except Exception as e:
                    duration = time.time() - start_time
                    return {
                        "request_id": request_id,
                        "duration": duration,
                        "status_code": 0,
                        "success": False,
                        "error": str(e)
                    }
        
        # Run the tests
        async with aiohttp.ClientSession() as session:
            tasks = [
                create_scan(session, i) 
                for i in range(total_requests)
            ]
            
            start_time = time.time()
            results = await asyncio.gather(*tasks)
            total_duration = time.time() - start_time
        
        # Analyze results
        self.analyze_performance_results(results, total_duration)
        
        return results
    
    def analyze_performance_results(self, results: List[Dict[str, Any]], total_duration: float):
        """Analyze and display performance results"""
        
        successful_requests = [r for r in results if r["success"]]
        failed_requests = [r for r in results if not r["success"]]
        
        if not successful_requests:
            print("❌ No successful requests!")
            return
        
        durations = [r["duration"] for r in successful_requests]
        
        print(f"\n📈 Performance Results:")
        print(f"   Total Duration: {total_duration:.2f}s")
        print(f"   Total Requests: {len(results)}")
        print(f"   Successful: {len(successful_requests)} ({len(successful_requests)/len(results)*100:.1f}%)")
        print(f"   Failed: {len(failed_requests)} ({len(failed_requests)/len(results)*100:.1f}%)")
        print(f"   Requests/sec: {len(results)/total_duration:.2f}")
        
        print(f"\n⏱️  Response Times:")
        print(f"   Mean: {statistics.mean(durations):.3f}s")
        print(f"   Median: {statistics.median(durations):.3f}s")
        print(f"   Min: {min(durations):.3f}s")
        print(f"   Max: {max(durations):.3f}s")
        
        if len(durations) > 1:
            print(f"   Std Dev: {statistics.stdev(durations):.3f}s")
        
        # Percentiles
        sorted_durations = sorted(durations)
        p95_index = int(0.95 * len(sorted_durations))
        p99_index = int(0.99 * len(sorted_durations))
        
        print(f"   95th percentile: {sorted_durations[p95_index]:.3f}s")
        print(f"   99th percentile: {sorted_durations[p99_index]:.3f}s")

async def main():
    """Run performance tests"""
    tester = PerformanceTester()
    
    print("🧪 EASM Performance Testing")
    print("=" * 50)
    
    # Test 1: Low concurrency
    await tester.test_scan_creation_performance(concurrent_requests=5, total_requests=50)
    
    print("\n" + "=" * 50)
    
    # Test 2: Higher concurrency
    await tester.test_scan_creation_performance(concurrent_requests=20, total_requests=100)

if __name__ == "__main__":
    asyncio.run(main())
