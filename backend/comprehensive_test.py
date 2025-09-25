#!/usr/bin/env python3
"""
Comprehensive test suite for KRAI System v0.6
Tests all functionality based on old database logic and component grouping
"""

import asyncio
import logging
import json
import time
from typing import Dict, List, Any
from pathlib import Path
import sys
import os

# Add project root to path
sys.path.append(str(Path(__file__).parent))

import httpx
from app.core.logging import setup_logging, log_test_result

# Initialize logging
setup_logging()
logger = logging.getLogger("krai.tests")

class KRAISystemTester:
    """Comprehensive tester for KRAI System"""

    def __init__(self, base_url: str = "http://localhost:8002"):
        self.base_url = base_url
        self.test_results = []
        self.passed_tests = 0
        self.failed_tests = 0

    async def log_test(self, test_name: str, status: str, details: Dict = None, error: str = None):
        """Log test result"""
        self.test_results.append({
            "test_name": test_name,
            "status": status,
            "details": details,
            "error": error,
            "timestamp": time.time()
        })

        if status == "PASSED":
            self.passed_tests += 1
        else:
            self.failed_tests += 1

        log_test_result(test_name, status, details, error)

    async def test_backend_health(self) -> bool:
        """Test if backend is running and healthy"""
        try:
            async with httpx.AsyncClient() as client:
                # Test root endpoint
                response = await client.get(f"{self.base_url}/")
                if response.status_code == 200:
                    data = response.json()
                    await self.log_test("Backend Root Endpoint", "PASSED", {
                        "status_code": response.status_code,
                        "version": data.get("version"),
                        "message": data.get("message")
                    })
                else:
                    await self.log_test("Backend Root Endpoint", "FAILED", {
                        "status_code": response.status_code,
                        "response": response.text
                    })
                    return False

                # Test health endpoint
                health_response = await client.get(f"{self.base_url}/health")
                if health_response.status_code == 200:
                    health_data = health_response.json()
                    await self.log_test("Backend Health Check", "PASSED", {
                        "status": health_data.get("status"),
                        "version": health_data.get("version")
                    })
                else:
                    await self.log_test("Backend Health Check", "FAILED", {
                        "status_code": health_response.status_code
                    })
                    return False

                return True

        except Exception as e:
            await self.log_test("Backend Connection", "FAILED", error=str(e))
            return False

    async def test_api_endpoints(self) -> bool:
        """Test all API endpoints"""
        endpoints_to_test = [
            ("GET", "/api/v1/models/", "Models List"),
            ("GET", "/api/v1/models/stats/summary", "Models Stats"),
            ("GET", "/api/v1/materials/", "Materials List"),
            ("GET", "/api/v1/materials/stats/summary", "Materials Stats"),
            ("GET", "/api/v1/warehouse/stock", "Warehouse Stock"),
            ("GET", "/api/v1/warehouse/stats/summary", "Warehouse Stats"),
            ("GET", "/api/v1/warehouse/alerts/low-stock", "Low Stock Alerts"),
            ("GET", "/api/v1/production/orders", "Production Orders"),
            ("GET", "/api/v1/production/stats/summary", "Production Stats"),
            ("GET", "/api/v1/references/size-runs", "Size Runs"),
            ("GET", "/api/v1/references/specifications", "Specifications"),
        ]

        all_passed = True
        async with httpx.AsyncClient() as client:
            for method, endpoint, test_name in endpoints_to_test:
                try:
                    response = await client.request(method, f"{self.base_url}{endpoint}")

                    if response.status_code == 200:
                        data = response.json()
                        await self.log_test(f"API {test_name}", "PASSED", {
                            "endpoint": endpoint,
                            "status_code": response.status_code,
                            "response_size": len(str(data))
                        })
                    else:
                        await self.log_test(f"API {test_name}", "FAILED", {
                            "endpoint": endpoint,
                            "status_code": response.status_code,
                            "response": response.text[:500]
                        })
                        all_passed = False

                except Exception as e:
                    await self.log_test(f"API {test_name}", "FAILED", {
                        "endpoint": endpoint,
                        "error": str(e)
                    })
                    all_passed = False

        return all_passed

    async def test_models_crud(self) -> bool:
        """Test Models CRUD operations"""
        test_model = {
            "article": "TEST-001",
            "name": "Test Boot Model",
            "gender": "MALE",
            "model_type": "BOOT",
            "category": "WORK",
            "size_min": 40,
            "size_max": 46,
            "retail_price": 5000,
            "wholesale_price": 3500,
            "is_active": True
        }

        async with httpx.AsyncClient() as client:
            try:
                # Test CREATE
                create_response = await client.post(
                    f"{self.base_url}/api/v1/models/",
                    json=test_model
                )

                if create_response.status_code in [200, 201]:
                    created_model = create_response.json()
                    model_id = created_model.get("id")
                    await self.log_test("Models CREATE", "PASSED", {
                        "model_id": model_id,
                        "article": test_model["article"]
                    })

                    # Test READ
                    read_response = await client.get(f"{self.base_url}/api/v1/models/{model_id}")
                    if read_response.status_code == 200:
                        await self.log_test("Models READ", "PASSED", {"model_id": model_id})
                    else:
                        await self.log_test("Models READ", "FAILED", {
                            "model_id": model_id,
                            "status_code": read_response.status_code
                        })

                    # Test UPDATE
                    update_data = {"name": "Updated Test Boot Model", "retail_price": 5500}
                    update_response = await client.put(
                        f"{self.base_url}/api/v1/models/{model_id}",
                        json=update_data
                    )
                    if update_response.status_code == 200:
                        await self.log_test("Models UPDATE", "PASSED", {"model_id": model_id})
                    else:
                        await self.log_test("Models UPDATE", "FAILED", {
                            "model_id": model_id,
                            "status_code": update_response.status_code
                        })

                    # Test DELETE
                    delete_response = await client.delete(f"{self.base_url}/api/v1/models/{model_id}")
                    if delete_response.status_code in [200, 204]:
                        await self.log_test("Models DELETE", "PASSED", {"model_id": model_id})
                    else:
                        await self.log_test("Models DELETE", "FAILED", {
                            "model_id": model_id,
                            "status_code": delete_response.status_code
                        })

                    return True

                else:
                    await self.log_test("Models CREATE", "FAILED", {
                        "status_code": create_response.status_code,
                        "response": create_response.text[:500]
                    })
                    return False

            except Exception as e:
                await self.log_test("Models CRUD", "FAILED", error=str(e))
                return False

    async def test_materials_functionality(self) -> bool:
        """Test materials management based on old DB logic"""
        # Test material groups from old system
        material_groups = ["leather", "sole", "hardware", "lining", "chemical", "packaging"]

        test_materials = [
            {
                "article": "MAT-LEATHER-001",
                "name": "Premium Black Leather",
                "group_type": "leather",
                "unit": "dm2",
                "price": 150.00,
                "supplier": "Leather Supplier Co",
                "is_active": True
            },
            {
                "article": "MAT-SOLE-001",
                "name": "Rubber Sole Size 42",
                "group_type": "sole",
                "unit": "pair",
                "price": 200.00,
                "supplier": "Sole Factory Ltd",
                "is_active": True
            }
        ]

        async with httpx.AsyncClient() as client:
            try:
                for material in test_materials:
                    # Test material creation
                    response = await client.post(
                        f"{self.base_url}/api/v1/materials/",
                        json=material
                    )

                    if response.status_code in [200, 201]:
                        await self.log_test(f"Material Create - {material['group_type']}", "PASSED", {
                            "article": material["article"],
                            "group": material["group_type"]
                        })
                    else:
                        await self.log_test(f"Material Create - {material['group_type']}", "FAILED", {
                            "status_code": response.status_code,
                            "article": material["article"]
                        })

                # Test filtering by material groups
                for group in material_groups:
                    response = await client.get(
                        f"{self.base_url}/api/v1/materials/",
                        params={"group_type": group}
                    )

                    if response.status_code == 200:
                        await self.log_test(f"Material Filter - {group}", "PASSED", {
                            "group": group,
                            "count": len(response.json().get("items", []))
                        })
                    else:
                        await self.log_test(f"Material Filter - {group}", "FAILED", {
                            "group": group,
                            "status_code": response.status_code
                        })

                return True

            except Exception as e:
                await self.log_test("Materials Functionality", "FAILED", error=str(e))
                return False

    async def test_specification_logic(self) -> bool:
        """Test specification logic based on old component grouping"""
        # Test specification creation and component management
        test_spec = {
            "model_article": "TEST-SPEC-001",
            "name": "Test Boot Specification",
            "components": [
                {
                    "material_article": "MAT-LEATHER-001",
                    "component_name": "Upper Leather",
                    "quantity": 40.0,
                    "unit": "dm2",
                    "component_group": "upper"
                },
                {
                    "material_article": "MAT-SOLE-001",
                    "component_name": "Main Sole",
                    "quantity": 1.0,
                    "unit": "pair",
                    "component_group": "sole"
                }
            ]
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/api/v1/references/specifications",
                    json=test_spec
                )

                if response.status_code in [200, 201]:
                    await self.log_test("Specification Creation", "PASSED", {
                        "model_article": test_spec["model_article"],
                        "components_count": len(test_spec["components"])
                    })
                    return True
                else:
                    await self.log_test("Specification Creation", "FAILED", {
                        "status_code": response.status_code,
                        "response": response.text[:500]
                    })
                    return False

            except Exception as e:
                await self.log_test("Specification Logic", "FAILED", error=str(e))
                return False

    async def test_warehouse_operations(self) -> bool:
        """Test warehouse operations"""
        async with httpx.AsyncClient() as client:
            try:
                # Test stock adjustment
                adjustment_data = {
                    "quantity": 100,
                    "reason": "Initial stock test"
                }

                # First get stock items
                stock_response = await client.get(f"{self.base_url}/api/v1/warehouse/stock")
                if stock_response.status_code == 200:
                    await self.log_test("Warehouse Stock List", "PASSED", {
                        "items_count": len(stock_response.json().get("items", []))
                    })

                    # Test stock adjustment if items exist
                    stock_items = stock_response.json().get("items", [])
                    if stock_items:
                        first_item = stock_items[0]
                        adjust_response = await client.post(
                            f"{self.base_url}/api/v1/warehouse/stock/{first_item['id']}/adjust",
                            json=adjustment_data
                        )

                        if adjust_response.status_code == 200:
                            await self.log_test("Warehouse Stock Adjustment", "PASSED", {
                                "item_id": first_item['id'],
                                "adjustment": adjustment_data["quantity"]
                            })
                        else:
                            await self.log_test("Warehouse Stock Adjustment", "FAILED", {
                                "status_code": adjust_response.status_code
                            })

                else:
                    await self.log_test("Warehouse Stock List", "FAILED", {
                        "status_code": stock_response.status_code
                    })

                return True

            except Exception as e:
                await self.log_test("Warehouse Operations", "FAILED", error=str(e))
                return False

    async def test_production_workflow(self) -> bool:
        """Test production workflow"""
        test_order = {
            "order_number": "PO-TEST-001",
            "model_article": "TEST-001",
            "quantity": 50,
            "priority": "normal",
            "deadline": "2024-12-31",
            "size_distribution": {
                "40": 5,
                "41": 10,
                "42": 15,
                "43": 12,
                "44": 8
            }
        }

        async with httpx.AsyncClient() as client:
            try:
                # Test production order creation
                response = await client.post(
                    f"{self.base_url}/api/v1/production/orders",
                    json=test_order
                )

                if response.status_code in [200, 201]:
                    await self.log_test("Production Order Creation", "PASSED", {
                        "order_number": test_order["order_number"],
                        "quantity": test_order["quantity"]
                    })
                    return True
                else:
                    await self.log_test("Production Order Creation", "FAILED", {
                        "status_code": response.status_code,
                        "response": response.text[:500]
                    })
                    return False

            except Exception as e:
                await self.log_test("Production Workflow", "FAILED", error=str(e))
                return False

    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all tests and return comprehensive report"""
        logger.info("Starting comprehensive KRAI System test suite...")

        test_functions = [
            ("Backend Health Check", self.test_backend_health),
            ("API Endpoints", self.test_api_endpoints),
            ("Models CRUD", self.test_models_crud),
            ("Materials Functionality", self.test_materials_functionality),
            ("Specification Logic", self.test_specification_logic),
            ("Warehouse Operations", self.test_warehouse_operations),
            ("Production Workflow", self.test_production_workflow),
        ]

        start_time = time.time()

        for test_name, test_func in test_functions:
            logger.info(f"Running test: {test_name}")
            try:
                await test_func()
            except Exception as e:
                await self.log_test(test_name, "FAILED", error=str(e))

        end_time = time.time()
        duration = end_time - start_time

        # Generate final report
        report = {
            "test_summary": {
                "total_tests": len(self.test_results),
                "passed": self.passed_tests,
                "failed": self.failed_tests,
                "success_rate": (self.passed_tests / len(self.test_results) * 100) if self.test_results else 0,
                "duration_seconds": duration
            },
            "test_results": self.test_results,
            "backend_url": self.base_url,
            "timestamp": time.time()
        }

        # Save report to file
        report_file = Path("logs/test_report.json")
        report_file.parent.mkdir(exist_ok=True)
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False, default=str)

        logger.info(f"Test suite completed. Report saved to {report_file}")
        return report


async def main():
    """Main test runner"""
    tester = KRAISystemTester()
    report = await tester.run_all_tests()

    print("\n" + "="*80)
    print("KRAI SYSTEM TEST REPORT")
    print("="*80)
    print(f"Total Tests: {report['test_summary']['total_tests']}")
    print(f"Passed: {report['test_summary']['passed']}")
    print(f"Failed: {report['test_summary']['failed']}")
    print(f"Success Rate: {report['test_summary']['success_rate']:.1f}%")
    print(f"Duration: {report['test_summary']['duration_seconds']:.2f} seconds")
    print("="*80)

    if report['test_summary']['failed'] > 0:
        print("\nFAILED TESTS:")
        for result in report['test_results']:
            if result['status'] == 'FAILED':
                print(f"❌ {result['test_name']}: {result.get('error', 'Unknown error')}")
    else:
        print("\n✅ All tests passed!")

    return report


if __name__ == "__main__":
    asyncio.run(main())