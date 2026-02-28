"""
SAP S/4HANA Cloud Public Edition 2602 - Scope Item Catalogue
Source: FSD_CE2602.pdf, Available_Migration_Objects.xlsx, SAP Best Practices
Last updated: 2026-02 (aligned with 2602 release)
Refresh cadence: Every SAP release (~Feb, Aug)

Each entry:
  id            - Official SAP scope item code (e.g. BD9, J45)
  name          - Human-readable process name
  lob           - Line of Business (Finance, Procurement, Sales, etc.)
  process_group - Sub-group within LOB
  description   - Implementation-level description used for semantic matching
  migration_objects - Data migration objects required (from Available_Migration_Objects.xlsx)
  keywords      - Key terms for semantic search (lowercase)
"""

SCOPE_ITEMS = [
  {
    "id": "J58",
    "name": "General Ledger",
    "lob": "Finance",
    "process_group": "Accounting and Financial Close",
    "description": "Core general ledger accounting including chart of accounts, posting periods, journal entries, document splitting, parallel ledgers, and real-time financial reporting.",
    "migration_objects": [
      "G/L account balance",
      "G/L open items"
    ],
    "keywords": [
      "general ledger",
      "GL",
      "journal entries",
      "chart of accounts",
      "financial statements",
      "posting periods",
      "parallel ledgers"
    ]
  },
  {
    "id": "J59",
    "name": "Advanced Accounting and Financial Close",
    "lob": "Finance",
    "process_group": "Accounting and Financial Close",
    "description": "Period-end close, financial statement preparation, accruals, deferrals, intercompany reconciliation, and statutory reporting including month-end and year-end close activities.",
    "migration_objects": [],
    "keywords": [
      "financial close",
      "period end",
      "month end",
      "year end",
      "accruals",
      "intercompany",
      "reconciliation",
      "statutory reporting"
    ]
  },
  {
    "id": "J60",
    "name": "Cash Management",
    "lob": "Finance",
    "process_group": "Treasury and Cash Management",
    "description": "Real-time cash position management, liquidity planning, bank account management, payment factory, and cash flow forecasting.",
    "migration_objects": [],
    "keywords": [
      "cash management",
      "liquidity",
      "cash position",
      "payment factory",
      "bank accounts",
      "cash flow forecast",
      "treasury"
    ]
  },
  {
    "id": "J77",
    "name": "Group Reporting",
    "lob": "Finance",
    "process_group": "Financial Close and Consolidation",
    "description": "Legal and management consolidation including intercompany elimination, currency translation, equity pickup, and group financial statements.",
    "migration_objects": [],
    "keywords": [
      "group reporting",
      "consolidation",
      "intercompany elimination",
      "legal consolidation",
      "currency translation",
      "financial consolidation"
    ]
  },
  {
    "id": "J78",
    "name": "Treasury and Risk Management",
    "lob": "Finance",
    "process_group": "Treasury and Cash Management",
    "description": "Financial instrument management, hedge accounting, market risk analysis, counterparty risk, and treasury operations for bonds, FX, and derivatives.",
    "migration_objects": [],
    "keywords": [
      "treasury",
      "risk management",
      "hedge accounting",
      "financial instruments",
      "FX",
      "derivatives",
      "counterparty risk",
      "market risk"
    ]
  },
  {
    "id": "BFA",
    "name": "Bank Account Management",
    "lob": "Finance",
    "process_group": "Treasury and Cash Management",
    "description": "Centralized management of bank accounts, bank master data, signatories, and bank connectivity including SWIFT and SEPA.",
    "migration_objects": [
      "Bank"
    ],
    "keywords": [
      "bank account management",
      "BAM",
      "SWIFT",
      "SEPA",
      "bank master data",
      "signatories"
    ]
  },
  {
    "id": "BFB",
    "name": "Bank Statement Processing",
    "lob": "Finance",
    "process_group": "Treasury and Cash Management",
    "description": "Automated import and processing of bank statements in MT940, camt.053, and other formats with automatic clearing and reconciliation.",
    "migration_objects": [
      "Bank"
    ],
    "keywords": [
      "bank statement",
      "MT940",
      "camt",
      "bank reconciliation",
      "automatic clearing",
      "bank communication"
    ]
  },
  {
    "id": "O59",
    "name": "Electronic Bank Statement",
    "lob": "Finance",
    "process_group": "Accounting and Financial Close",
    "description": "Import of electronic bank statements with automated posting and clearing of open items against bank statement lines.",
    "migration_objects": [
      "Bank"
    ],
    "keywords": [
      "electronic bank statement",
      "EBS",
      "bank import",
      "automatic posting",
      "clearing"
    ]
  },
  {
    "id": "O60",
    "name": "Check Deposit",
    "lob": "Finance",
    "process_group": "Accounting and Financial Close",
    "description": "Processing of incoming check payments including check deposit management and clearing against open receivables.",
    "migration_objects": [],
    "keywords": [
      "check deposit",
      "incoming checks",
      "check management",
      "receivables clearing"
    ]
  },
  {
    "id": "OFA",
    "name": "Payment Approval",
    "lob": "Finance",
    "process_group": "Accounts Payable",
    "description": "Workflow-based approval of outgoing payments including dual control, authorization limits, and segregation of duties for payment runs.",
    "migration_objects": [],
    "keywords": [
      "payment approval",
      "payment workflow",
      "dual control",
      "authorization",
      "payment run",
      "segregation of duties"
    ]
  },
  {
    "id": "O77",
    "name": "Multi-Bank Connectivity",
    "lob": "Finance",
    "process_group": "Treasury and Cash Management",
    "description": "Connectivity to multiple banking partners via SWIFT, H2H, or bank portals for payment transmission and bank statement retrieval.",
    "migration_objects": [],
    "keywords": [
      "multi-bank connectivity",
      "SWIFT",
      "H2H",
      "bank portal",
      "payment transmission",
      "bank communication"
    ]
  },
  {
    "id": "O78",
    "name": "Payment Medium Formats",
    "lob": "Finance",
    "process_group": "Accounts Payable",
    "description": "Generation of payment files in country-specific formats including SEPA, ACH, BACS, and other national payment standards.",
    "migration_objects": [],
    "keywords": [
      "payment formats",
      "SEPA",
      "ACH",
      "BACS",
      "payment medium",
      "domestic payments",
      "international payments"
    ]
  },
  {
    "id": "J45",
    "name": "Accounts Payable",
    "lob": "Finance",
    "process_group": "Accounts Payable",
    "description": "End-to-end supplier invoice processing including vendor invoice posting, payment terms, automatic payment program, dunning, and supplier reconciliation.",
    "migration_objects": [
      "Vendor open items",
      "Vendor balances"
    ],
    "keywords": [
      "accounts payable",
      "AP",
      "supplier invoices",
      "vendor payments",
      "payment program",
      "invoice processing"
    ]
  },
  {
    "id": "MK1",
    "name": "Invoice Management with OCR",
    "lob": "Finance",
    "process_group": "Accounts Payable",
    "description": "Intelligent invoice capture using OCR and machine learning to automatically extract header and line item data from PDF and paper invoices.",
    "migration_objects": [],
    "keywords": [
      "invoice management",
      "OCR",
      "intelligent invoice",
      "automated invoice capture",
      "machine learning",
      "invoice scanning"
    ]
  },
  {
    "id": "J62",
    "name": "Invoice and Payables Management",
    "lob": "Finance",
    "process_group": "Accounts Payable",
    "description": "Supplier invoice verification, three-way match against PO and goods receipt, exception handling, and approval workflow for non-PO invoices.",
    "migration_objects": [],
    "keywords": [
      "invoice verification",
      "three-way match",
      "payables management",
      "supplier invoice",
      "GR-IR",
      "non-PO invoices"
    ]
  },
  {
    "id": "BEF",
    "name": "Budget Management for Purchase Orders",
    "lob": "Finance",
    "process_group": "Accounts Payable",
    "description": "Budget availability checking for purchasing documents with commitment management, budget consumption tracking, and budget exceeded warnings.",
    "migration_objects": [],
    "keywords": [
      "budget management",
      "commitment management",
      "budget check",
      "purchase order budget",
      "budget availability",
      "funds management"
    ]
  },
  {
    "id": "J44",
    "name": "Accounts Receivable",
    "lob": "Finance",
    "process_group": "Accounts Receivable",
    "description": "Customer invoice management, incoming payment processing, dunning, credit management, customer account reconciliation, and dispute management.",
    "migration_objects": [
      "Customer open items",
      "Customer balances"
    ],
    "keywords": [
      "accounts receivable",
      "AR",
      "customer invoices",
      "collections",
      "dunning",
      "credit management",
      "dispute management"
    ]
  },
  {
    "id": "ODA",
    "name": "Credit Management",
    "lob": "Finance",
    "process_group": "Accounts Receivable",
    "description": "Centralized customer credit limit management, real-time credit exposure calculation, credit checks during order processing, and credit decision workflow.",
    "migration_objects": [],
    "keywords": [
      "credit management",
      "credit limit",
      "credit exposure",
      "credit check",
      "customer credit",
      "credit decision",
      "credit risk"
    ]
  },
  {
    "id": "4A3",
    "name": "Dispute and Collections Management",
    "lob": "Finance",
    "process_group": "Accounts Receivable",
    "description": "Structured management of customer disputes, collection strategy definition, automated dunning, and collections worklist management.",
    "migration_objects": [],
    "keywords": [
      "dispute management",
      "collections",
      "dunning",
      "customer dispute",
      "collections worklist",
      "receivables management"
    ]
  },
  {
    "id": "ODD",
    "name": "SAP Digital Payments",
    "lob": "Finance",
    "process_group": "Accounts Receivable",
    "description": "Integration with digital payment providers for online payment acceptance including credit cards, digital wallets, and payment service providers.",
    "migration_objects": [],
    "keywords": [
      "digital payments",
      "online payments",
      "credit card",
      "payment gateway",
      "PSP",
      "payment service provider"
    ]
  },
  {
    "id": "J11",
    "name": "Fixed Asset Accounting",
    "lob": "Finance",
    "process_group": "Asset Accounting",
    "description": "Fixed asset lifecycle management including acquisition, capitalization, depreciation, revaluation, transfer, and retirement with parallel ledger support.",
    "migration_objects": [
      "Fixed asset master data",
      "Fixed asset balances"
    ],
    "keywords": [
      "fixed assets",
      "asset accounting",
      "depreciation",
      "capitalization",
      "asset lifecycle",
      "IFRS 16",
      "asset retirement"
    ]
  },
  {
    "id": "J12",
    "name": "Asset Accounting \u2013 Investment Management",
    "lob": "Finance",
    "process_group": "Asset Accounting",
    "description": "Management of capital investment projects from appropriation request through asset under construction to final asset capitalization.",
    "migration_objects": [],
    "keywords": [
      "investment management",
      "asset under construction",
      "AuC",
      "capitalization",
      "CAPEX",
      "capital projects",
      "appropriation request"
    ]
  },
  {
    "id": "J13",
    "name": "Lease Accounting",
    "lob": "Finance",
    "process_group": "Asset Accounting",
    "description": "IFRS 16 and ASC 842 compliant lease accounting covering right-of-use asset recognition, lease liability amortization, and lease modifications.",
    "migration_objects": [],
    "keywords": [
      "lease accounting",
      "IFRS 16",
      "ASC 842",
      "right-of-use",
      "lease liability",
      "operating lease",
      "finance lease"
    ]
  },
  {
    "id": "J14",
    "name": "Overhead Transparency for IT Assets",
    "lob": "Finance",
    "process_group": "Asset Accounting",
    "description": "IT asset cost transparency, allocation of IT infrastructure costs, chargeback to business units, and IT overhead cost management.",
    "migration_objects": [],
    "keywords": [
      "IT assets",
      "overhead transparency",
      "cost allocation",
      "chargeback",
      "IT cost",
      "infrastructure costs"
    ]
  },
  {
    "id": "56E",
    "name": "Asset Retirement Obligation",
    "lob": "Finance",
    "process_group": "Asset Accounting",
    "description": "Recognition and measurement of asset retirement obligations (ARO) under IFRS and US GAAP, including initial recognition, accretion, and settlement.",
    "migration_objects": [
      "Asset retirement obligation - Master data",
      "Asset retirement obligation - Postings"
    ],
    "keywords": [
      "asset retirement obligation",
      "ARO",
      "decommissioning",
      "environmental liability",
      "IFRS",
      "accretion"
    ]
  },
  {
    "id": "5IT",
    "name": "Enhanced Fixed Asset Depreciation",
    "lob": "Finance",
    "process_group": "Asset Accounting",
    "description": "Advanced depreciation methods including declining balance, units of production, and component accounting with simulation capabilities.",
    "migration_objects": [
      "Asset retirement obligation - Master data"
    ],
    "keywords": [
      "depreciation",
      "declining balance",
      "units of production",
      "component accounting",
      "depreciation simulation"
    ]
  },
  {
    "id": "1GA",
    "name": "Cost Center Accounting",
    "lob": "Finance",
    "process_group": "Management Accounting",
    "description": "Cost center planning, actual posting, allocation cycles, assessment, distribution, and variance analysis for overhead cost management.",
    "migration_objects": [
      "CO - Cost center"
    ],
    "keywords": [
      "cost center",
      "overhead costs",
      "allocation",
      "assessment",
      "distribution",
      "variance analysis",
      "cost center planning"
    ]
  },
  {
    "id": "1GE",
    "name": "Profit Center Accounting",
    "lob": "Finance",
    "process_group": "Management Accounting",
    "description": "Profit center based reporting of revenues and costs, segment reporting, internal profit and loss statements, and profit center planning.",
    "migration_objects": [
      "CO - Profit center"
    ],
    "keywords": [
      "profit center",
      "segment reporting",
      "internal P&L",
      "profit center planning",
      "managerial accounting"
    ]
  },
  {
    "id": "1GJ",
    "name": "Internal Orders",
    "lob": "Finance",
    "process_group": "Management Accounting",
    "description": "Cost collection on internal orders for jobs, projects, and campaigns, including budget management, settlement, and overhead allocation.",
    "migration_objects": [],
    "keywords": [
      "internal orders",
      "cost collection",
      "overhead allocation",
      "settlement",
      "budget control",
      "marketing campaigns",
      "job costing"
    ]
  },
  {
    "id": "1JE",
    "name": "Overhead Cost Controlling",
    "lob": "Finance",
    "process_group": "Management Accounting",
    "description": "Template allocation, activity-based costing, resource consumption planning, and multi-level overhead calculation for indirect costs.",
    "migration_objects": [],
    "keywords": [
      "overhead cost controlling",
      "activity-based costing",
      "ABC",
      "template allocation",
      "indirect costs",
      "cost allocation"
    ]
  },
  {
    "id": "J54",
    "name": "Product Cost Planning",
    "lob": "Finance",
    "process_group": "Management Accounting",
    "description": "Standard cost calculation for manufactured products including material, labor, overhead, and activity cost components with cost estimate versioning.",
    "migration_objects": [],
    "keywords": [
      "product cost planning",
      "standard cost",
      "cost estimate",
      "BOM costing",
      "routing costing",
      "cost components",
      "manufacturing cost"
    ]
  },
  {
    "id": "J55",
    "name": "Cost Object Controlling",
    "lob": "Finance",
    "process_group": "Management Accounting",
    "description": "Work-in-process calculation, production order variance analysis, actual cost settlement, and product cost collector management.",
    "migration_objects": [],
    "keywords": [
      "cost object controlling",
      "work in process",
      "WIP",
      "production order variance",
      "actual costing",
      "settlement",
      "manufacturing variance"
    ]
  },
  {
    "id": "1RU",
    "name": "Profitability Analysis",
    "lob": "Finance",
    "process_group": "Management Accounting",
    "description": "Margin analysis by customer, product, region, and sales channel using both costing-based and account-based COPA for strategic pricing decisions.",
    "migration_objects": [],
    "keywords": [
      "profitability analysis",
      "COPA",
      "margin analysis",
      "contribution margin",
      "customer profitability",
      "product profitability",
      "pricing analytics"
    ]
  },
  {
    "id": "1GH",
    "name": "Transfer Pricing",
    "lob": "Finance",
    "process_group": "Management Accounting",
    "description": "Intercompany transfer pricing management for legal entity valuation, markup calculation, and profit allocation between related entities.",
    "migration_objects": [],
    "keywords": [
      "transfer pricing",
      "intercompany",
      "markup",
      "legal entity valuation",
      "arm's length",
      "OECD",
      "intercompany profit"
    ]
  },
  {
    "id": "BJG",
    "name": "Tax Compliance",
    "lob": "Finance",
    "process_group": "Tax Management",
    "description": "Tax determination, tax posting, VAT reporting, and tax compliance for direct and indirect taxes across multiple jurisdictions.",
    "migration_objects": [],
    "keywords": [
      "tax compliance",
      "VAT",
      "GST",
      "tax determination",
      "indirect tax",
      "tax reporting",
      "sales tax",
      "use tax"
    ]
  },
  {
    "id": "5FJ",
    "name": "Advanced Compliance Reporting",
    "lob": "Finance",
    "process_group": "Tax Management",
    "description": "Country-specific statutory and regulatory reporting including SAF-T, Intrastat, EC Sales List, and other mandatory government filings.",
    "migration_objects": [
      "Characteristic"
    ],
    "keywords": [
      "compliance reporting",
      "SAF-T",
      "Intrastat",
      "EC Sales List",
      "statutory reporting",
      "regulatory compliance",
      "government reporting"
    ]
  },
  {
    "id": "54D",
    "name": "Tax on Goods Movements \u2013 Brazil",
    "lob": "Finance",
    "process_group": "Tax Management",
    "description": "Brazilian tax compliance including ICMS, IPI, PIS/COFINS calculation, electronic fiscal documents (NF-e, CT-e), and SPED reporting.",
    "migration_objects": [
      "Asset to control tax credits (Brazil)"
    ],
    "keywords": [
      "Brazil tax",
      "ICMS",
      "IPI",
      "PIS",
      "COFINS",
      "NF-e",
      "SPED",
      "Brazilian localization",
      "fiscal documents"
    ]
  },
  {
    "id": "J68",
    "name": "Real Estate Management",
    "lob": "Finance",
    "process_group": "Real Estate",
    "description": "Real estate portfolio management including property master data, lease contract management, rental billing, and service charge settlement.",
    "migration_objects": [],
    "keywords": [
      "real estate",
      "property management",
      "lease contract",
      "rental billing",
      "service charges",
      "facility management"
    ]
  },
  {
    "id": "BNX",
    "name": "Operational Procurement \u2013 Buy-Side",
    "lob": "Procurement",
    "process_group": "Operational Procurement",
    "description": "End-to-end purchase requisition to purchase order processing including approval workflow, goods receipt, and invoice matching.",
    "migration_objects": [],
    "keywords": [
      "purchase requisition",
      "purchase order",
      "PO",
      "procurement",
      "buying",
      "PR to PO",
      "goods receipt",
      "operational procurement"
    ]
  },
  {
    "id": "MO1",
    "name": "Supplier Qualification and Management",
    "lob": "Procurement",
    "process_group": "Sourcing and Contract Management",
    "description": "Supplier onboarding, qualification, evaluation, and classification including supplier registration portal and lifecycle management.",
    "migration_objects": [],
    "keywords": [
      "supplier qualification",
      "supplier management",
      "vendor onboarding",
      "supplier evaluation",
      "supplier portal",
      "supplier registration"
    ]
  },
  {
    "id": "BMC",
    "name": "Sourcing",
    "lob": "Procurement",
    "process_group": "Sourcing and Contract Management",
    "description": "Request for quotation (RFQ), supplier bid management, bid comparison, and award decisions for strategic and spot sourcing events.",
    "migration_objects": [],
    "keywords": [
      "sourcing",
      "RFQ",
      "request for quotation",
      "bid management",
      "supplier bids",
      "award decision",
      "spend analytics",
      "strategic sourcing"
    ]
  },
  {
    "id": "1EM",
    "name": "Contract Management",
    "lob": "Procurement",
    "process_group": "Sourcing and Contract Management",
    "description": "Central purchasing contract repository, contract creation, release orders against contracts, contract compliance monitoring, and expiry alerts.",
    "migration_objects": [],
    "keywords": [
      "contract management",
      "purchasing contracts",
      "blanket orders",
      "scheduling agreements",
      "contract compliance",
      "contract repository"
    ]
  },
  {
    "id": "J51",
    "name": "Procurement Analytics",
    "lob": "Finance",
    "process_group": "Procurement Analytics",
    "description": "Real-time procurement spend analysis, supplier performance dashboards, savings tracking, and procurement KPI reporting.",
    "migration_objects": [],
    "keywords": [
      "procurement analytics",
      "spend analysis",
      "supplier performance",
      "savings tracking",
      "procurement KPIs",
      "spend visibility",
      "purchasing reporting"
    ]
  },
  {
    "id": "4YI",
    "name": "Central Procurement",
    "lob": "Procurement",
    "process_group": "Operational Procurement",
    "description": "Centralized procurement across multiple systems and company codes with shared contracts, central sourcing, and consolidated reporting.",
    "migration_objects": [],
    "keywords": [
      "central procurement",
      "group purchasing",
      "procurement hub",
      "multi-company purchasing",
      "centralized buying"
    ]
  },
  {
    "id": "BJE",
    "name": "Material Requirements Planning",
    "lob": "Procurement",
    "process_group": "Operational Procurement",
    "description": "MRP-based planning of material replenishment including purchase requisition creation, planned orders, and supply/demand balancing.",
    "migration_objects": [
      "Batch unique at material"
    ],
    "keywords": [
      "material requirements planning",
      "MRP",
      "replenishment",
      "planned orders",
      "purchase requisition",
      "supply planning",
      "demand planning"
    ]
  },
  {
    "id": "BKK",
    "name": "Procurement Collaboration with Suppliers",
    "lob": "Procurement",
    "process_group": "Operational Procurement",
    "description": "Order collaboration portal for suppliers to acknowledge POs, confirm delivery dates, and submit advance shipping notifications (ASN).",
    "migration_objects": [],
    "keywords": [
      "procurement collaboration",
      "supplier portal",
      "PO acknowledgement",
      "ASN",
      "supplier confirmation",
      "B2B collaboration"
    ]
  },
  {
    "id": "MEM",
    "name": "Service Procurement",
    "lob": "Procurement",
    "process_group": "Operational Procurement",
    "description": "Procurement of external services including service orders, service entry sheets, limit orders, and service acceptance workflow.",
    "migration_objects": [],
    "keywords": [
      "service procurement",
      "service orders",
      "service entry sheet",
      "external services",
      "limit orders",
      "service acceptance"
    ]
  },
  {
    "id": "BNW",
    "name": "Procurement of Direct Materials",
    "lob": "Procurement",
    "process_group": "Operational Procurement",
    "description": "Direct material procurement including source determination, purchase order creation, inbound delivery, goods receipt, and invoice verification.",
    "migration_objects": [],
    "keywords": [
      "direct procurement",
      "direct materials",
      "source determination",
      "inbound delivery",
      "goods receipt",
      "invoice verification",
      "raw materials"
    ]
  },
  {
    "id": "4HP",
    "name": "Advanced Intercompany Stock Transfer",
    "lob": "Procurement",
    "process_group": "Operational Procurement",
    "description": "Intercompany and intra-company stock transfers with automated billing, transit inventory management, and multi-step approval.",
    "migration_objects": [],
    "keywords": [
      "intercompany stock transfer",
      "STO",
      "inter-company",
      "stock transport order",
      "transit stock",
      "transfer pricing",
      "intracompany transfer"
    ]
  },
  {
    "id": "1AV",
    "name": "Spend Performance Management",
    "lob": "Procurement",
    "process_group": "Procurement Analytics",
    "description": "Strategic spend analytics with category management, supplier segmentation, savings pipeline, and procurement performance benchmarking.",
    "migration_objects": [],
    "keywords": [
      "spend analytics",
      "category management",
      "supplier segmentation",
      "savings pipeline",
      "procurement performance",
      "spend management"
    ]
  },
  {
    "id": "BHA",
    "name": "Self-Service Procurement",
    "lob": "Procurement",
    "process_group": "Operational Procurement",
    "description": "Employee self-service for catalog-based ordering, shopping cart creation, and approval with integration to external marketplaces.",
    "migration_objects": [],
    "keywords": [
      "self-service procurement",
      "shopping cart",
      "catalog",
      "marketplace",
      "employee purchasing",
      "spot buy",
      "indirect procurement"
    ]
  },
  {
    "id": "BD9",
    "name": "Sell from Stock",
    "lob": "Sales",
    "process_group": "Sales Order Management",
    "description": "Standard order-to-cash process covering sales order creation, pricing, credit check, delivery, goods issue, and customer billing.",
    "migration_objects": [
      "Batch unique at material",
      "Characteristic"
    ],
    "keywords": [
      "sell from stock",
      "order to cash",
      "sales order",
      "delivery",
      "goods issue",
      "billing",
      "standard sales"
    ]
  },
  {
    "id": "BDA",
    "name": "Order-Based Revenue Recognition",
    "lob": "Sales",
    "process_group": "Sales Billing",
    "description": "Revenue recognition for sales orders based on IFRS 15 / ASC 606 including performance obligation identification and revenue allocation.",
    "migration_objects": [
      "Characteristic"
    ],
    "keywords": [
      "revenue recognition",
      "IFRS 15",
      "ASC 606",
      "performance obligation",
      "revenue allocation",
      "deferred revenue",
      "contract revenue"
    ]
  },
  {
    "id": "BDD",
    "name": "Make-to-Order Production with Variant Configuration",
    "lob": "Sales",
    "process_group": "Sales Order Management",
    "description": "Configure-to-order sales process where product variants are configured at order entry and drive production order creation.",
    "migration_objects": [
      "Characteristic"
    ],
    "keywords": [
      "make-to-order",
      "variant configuration",
      "configure-to-order",
      "CTO",
      "MTO",
      "product configuration",
      "custom products"
    ]
  },
  {
    "id": "BJ5",
    "name": "Returnable Packaging Management",
    "lob": "Sales",
    "process_group": "Sales Order Management",
    "description": "Management of returnable transport packaging (RTP) including deposit billing, returns tracking, and packaging balance reconciliation.",
    "migration_objects": [
      "Batch unique at material"
    ],
    "keywords": [
      "returnable packaging",
      "RTP",
      "deposit billing",
      "packaging returns",
      "container management",
      "packaging balance"
    ]
  },
  {
    "id": "BKJ",
    "name": "Advanced Available-to-Promise",
    "lob": "Sales",
    "process_group": "Sales Order Management",
    "description": "Sophisticated ATP checking with rules-based ATP, multi-level ATP, and backorder processing to maximize sales order fulfillment.",
    "migration_objects": [
      "Batch unique at material"
    ],
    "keywords": [
      "available to promise",
      "ATP",
      "backorder",
      "order fulfillment",
      "delivery scheduling",
      "capable-to-promise",
      "CTP"
    ]
  },
  {
    "id": "BKL",
    "name": "Customer Returns Management",
    "lob": "Sales",
    "process_group": "Sales Order Management",
    "description": "End-to-end returns processing including return sales orders, quality inspection, credit memo creation, and reverse logistics.",
    "migration_objects": [
      "Batch unique at material"
    ],
    "keywords": [
      "customer returns",
      "returns management",
      "RMA",
      "return merchandise authorization",
      "credit memo",
      "reverse logistics",
      "returns processing"
    ]
  },
  {
    "id": "BKX",
    "name": "Sales Order Collaboration",
    "lob": "Sales",
    "process_group": "Sales Order Management",
    "description": "EDI and B2B order collaboration with customers for order acknowledgement, shipping confirmation, and invoice exchange.",
    "migration_objects": [
      "Batch unique at material"
    ],
    "keywords": [
      "sales order collaboration",
      "EDI",
      "B2B",
      "order acknowledgement",
      "customer collaboration",
      "electronic commerce"
    ]
  },
  {
    "id": "BKZ",
    "name": "Sales Scheduling Agreements",
    "lob": "Sales",
    "process_group": "Sales Order Management",
    "description": "Long-term supply agreements with delivery schedule lines, forecast/JIT delivery calls, and automatic replenishment.",
    "migration_objects": [
      "Batch unique at material"
    ],
    "keywords": [
      "scheduling agreement",
      "delivery schedule",
      "JIT delivery",
      "forecast delivery",
      "blanket agreement",
      "release orders"
    ]
  },
  {
    "id": "BLF",
    "name": "Subscription Order Management",
    "lob": "Sales",
    "process_group": "Sales Order Management",
    "description": "Subscription-based sales including recurring billing, subscription modifications, renewals, and usage-based pricing.",
    "migration_objects": [
      "Batch unique at material"
    ],
    "keywords": [
      "subscription",
      "recurring billing",
      "subscription management",
      "usage-based pricing",
      "subscription renewal",
      "SaaS billing"
    ]
  },
  {
    "id": "OD9",
    "name": "Sell from Stock \u2013 Intercompany",
    "lob": "Sales",
    "process_group": "Sales Order Management",
    "description": "Intercompany sales process where a selling entity procures and delivers from another legal entity with automated intercompany billing.",
    "migration_objects": [
      "Characteristic"
    ],
    "keywords": [
      "intercompany sales",
      "intercompany billing",
      "cross-company",
      "third-party order",
      "intercompany process"
    ]
  },
  {
    "id": "ODH",
    "name": "Quotation Management",
    "lob": "Sales",
    "process_group": "Sales Order Management",
    "description": "Sales quotation creation, pricing simulation, approval workflow, and conversion tracking to sales orders.",
    "migration_objects": [],
    "keywords": [
      "sales quotation",
      "quote management",
      "pricing simulation",
      "quotation approval",
      "opportunity to order",
      "bid management"
    ]
  },
  {
    "id": "ODQ",
    "name": "Sales Contract Management",
    "lob": "Sales",
    "process_group": "Sales Order Management",
    "description": "Value and quantity contracts with release orders, contract compliance tracking, and renewal management.",
    "migration_objects": [
      "Characteristic"
    ],
    "keywords": [
      "sales contracts",
      "contract management",
      "value contract",
      "quantity contract",
      "framework agreements",
      "contract compliance"
    ]
  },
  {
    "id": "OFB",
    "name": "Returns and Refunds",
    "lob": "Sales",
    "process_group": "Sales Order Management",
    "description": "Consumer returns portal with QR code-based return initiation, inspection, and automated refund processing.",
    "migration_objects": [
      "Batch unique at material"
    ],
    "keywords": [
      "returns",
      "refunds",
      "consumer returns",
      "return portal",
      "QR code returns",
      "automated refunds",
      "ecommerce returns"
    ]
  },
  {
    "id": "ODG",
    "name": "Configure-to-Order",
    "lob": "Sales",
    "process_group": "Sales Order Management",
    "description": "Variant-based order configuration with integrated BOM/routing explosion for engineer-to-order and configure-to-order manufacturing.",
    "migration_objects": [
      "Characteristic"
    ],
    "keywords": [
      "configure-to-order",
      "CTO",
      "engineer-to-order",
      "ETO",
      "variant configuration",
      "custom manufacturing",
      "product configurator"
    ]
  },
  {
    "id": "OKL",
    "name": "Goods Receipt Processing",
    "lob": "Sales",
    "process_group": "Sales Logistics",
    "description": "Inbound goods receipt including scheduled receipts, quality inspection integration, and warehouse management handover.",
    "migration_objects": [
      "Characteristic"
    ],
    "keywords": [
      "goods receipt",
      "inbound logistics",
      "receiving",
      "quality inspection",
      "warehouse management",
      "GR processing"
    ]
  },
  {
    "id": "4WY",
    "name": "Sales Order Management for High-Tech",
    "lob": "Sales",
    "process_group": "Sales Order Management",
    "description": "Advanced sales order management for high-tech industries including product allocation, ATP, drop shipment, and warranty tracking.",
    "migration_objects": [],
    "keywords": [
      "high-tech sales",
      "product allocation",
      "drop shipment",
      "warranty",
      "serial number",
      "configuration management"
    ]
  },
  {
    "id": "BHG",
    "name": "Direct Store Delivery",
    "lob": "Sales",
    "process_group": "Sales Logistics",
    "description": "Route planning, van stock management, and direct delivery to retail stores with mobile invoicing and collections.",
    "migration_objects": [],
    "keywords": [
      "direct store delivery",
      "DSD",
      "route management",
      "van sales",
      "mobile sales",
      "retail delivery"
    ]
  },
  {
    "id": "1FE",
    "name": "Sales Rebate Management",
    "lob": "Sales",
    "process_group": "Sales Billing",
    "description": "Condition-based rebate management with accruals, settlement, and reporting for volume-based and value-based rebate agreements.",
    "migration_objects": [],
    "keywords": [
      "rebates",
      "sales rebate",
      "volume rebate",
      "rebate agreement",
      "rebate accrual",
      "settlement",
      "incentive management"
    ]
  },
  {
    "id": "J17",
    "name": "Billing and Revenue Innovation",
    "lob": "Sales",
    "process_group": "Sales Billing",
    "description": "Flexible billing models including milestone billing, periodic billing, dynamic pricing, and multi-party revenue sharing.",
    "migration_objects": [],
    "keywords": [
      "billing",
      "revenue innovation",
      "milestone billing",
      "periodic billing",
      "dynamic pricing",
      "revenue sharing",
      "flexible billing"
    ]
  },
  {
    "id": "1YT",
    "name": "Discrete Manufacturing",
    "lob": "Manufacturing",
    "process_group": "Production Planning and Execution",
    "description": "Make-to-stock and make-to-order discrete manufacturing with production orders, capacity planning, shop floor control, and work center management.",
    "migration_objects": [
      "AVC - Configuration profile",
      "AVC - Object dependencies",
      "AVC - Constraint"
    ],
    "keywords": [
      "discrete manufacturing",
      "production order",
      "shop floor",
      "capacity planning",
      "work center",
      "make-to-stock",
      "MTS",
      "manufacturing execution"
    ]
  },
  {
    "id": "21D",
    "name": "Repetitive Manufacturing",
    "lob": "Manufacturing",
    "process_group": "Production Planning and Execution",
    "description": "High-volume continuous production using product cost collectors, backflushing, and line-based production with rate-based planning.",
    "migration_objects": [
      "AVC - Configuration profile"
    ],
    "keywords": [
      "repetitive manufacturing",
      "backflushing",
      "rate-based planning",
      "line production",
      "product cost collector",
      "high volume",
      "continuous production"
    ]
  },
  {
    "id": "22T",
    "name": "Variant Configuration Management",
    "lob": "Manufacturing",
    "process_group": "Production Planning and Execution",
    "description": "Product variant definition with characteristics, dependency conditions, configuration profiles, and variant BOM/routing management.",
    "migration_objects": [
      "AVC - Assign global dependency",
      "AVC - Characteristics group",
      "AVC - Configuration profile",
      "AVC - Constraint",
      "AVC - Dependency net",
      "AVC - Material variant",
      "AVC - Object dependencies",
      "AVC - Variant table entry",
      "AVC - Variant table structure"
    ],
    "keywords": [
      "variant configuration",
      "characteristics",
      "dependencies",
      "configuration profile",
      "variant BOM",
      "AVC",
      "product variants",
      "configurable products"
    ]
  },
  {
    "id": "BDQ",
    "name": "Batch Management",
    "lob": "Manufacturing",
    "process_group": "Production Planning and Execution",
    "description": "Batch-level material tracking, batch classification, shelf life management, batch where-used, and batch derivation in production.",
    "migration_objects": [
      "Batch unique at material and client level"
    ],
    "keywords": [
      "batch management",
      "batch tracking",
      "batch classification",
      "shelf life",
      "expiry date",
      "batch where-used",
      "FEFO",
      "lot tracking"
    ]
  },
  {
    "id": "J56",
    "name": "Demand-Driven Replenishment",
    "lob": "Manufacturing",
    "process_group": "Production Planning and Execution",
    "description": "Demand-Driven MRP (DDMRP) with strategic buffer positioning, buffer level calculation, and demand-driven planning execution.",
    "migration_objects": [],
    "keywords": [
      "DDMRP",
      "demand-driven MRP",
      "buffer management",
      "strategic buffers",
      "demand-driven planning",
      "supply chain decoupling"
    ]
  },
  {
    "id": "4WB",
    "name": "Production Planning for Process Industries",
    "lob": "Manufacturing",
    "process_group": "Production Planning and Execution",
    "description": "Process manufacturing including recipes, process orders, resource planning, and integration with laboratory and quality management.",
    "migration_objects": [],
    "keywords": [
      "process manufacturing",
      "process orders",
      "recipes",
      "process industry",
      "chemical",
      "pharma",
      "food manufacturing",
      "resource planning"
    ]
  },
  {
    "id": "ODJ",
    "name": "Outsourced Manufacturing",
    "lob": "Manufacturing",
    "process_group": "Production Planning and Execution",
    "description": "Subcontracting process with external processing of operations including component provision, goods issue, and receipt from subcontractor.",
    "migration_objects": [],
    "keywords": [
      "subcontracting",
      "outsourced manufacturing",
      "external processing",
      "toll manufacturing",
      "contract manufacturing",
      "component provision"
    ]
  },
  {
    "id": "PLF",
    "name": "Production for External Processing",
    "lob": "Manufacturing",
    "process_group": "Production Planning and Execution",
    "description": "Control of external operations within production routing with purchase order generation for external work centers.",
    "migration_objects": [
      "Batch unique at material",
      "Characteristic",
      "Class"
    ],
    "keywords": [
      "external processing",
      "subcontract operation",
      "work center",
      "routing operation",
      "external operation",
      "manufacturing routing"
    ]
  },
  {
    "id": "BDW",
    "name": "Extended Warehouse Management in Manufacturing",
    "lob": "Manufacturing",
    "process_group": "Production Planning and Execution",
    "description": "EWM integration for production supply including warehouse tasks for production staging, material flow, and finished goods put-away.",
    "migration_objects": [
      "Batch unique at material"
    ],
    "keywords": [
      "EWM",
      "production supply",
      "warehouse management",
      "manufacturing warehouse",
      "production staging",
      "finished goods"
    ]
  },
  {
    "id": "J1L",
    "name": "Manufacturing Execution Integration",
    "lob": "Manufacturing",
    "process_group": "Production Planning and Execution",
    "description": "Integration with MES systems for production feedback, quality results, machine data collection, and real-time production monitoring.",
    "migration_objects": [],
    "keywords": [
      "MES",
      "manufacturing execution system",
      "production feedback",
      "machine data",
      "IoT",
      "OEE",
      "production monitoring",
      "Industry 4.0"
    ]
  },
  {
    "id": "BLC",
    "name": "Quality Management in Manufacturing",
    "lob": "Manufacturing",
    "process_group": "Quality Management",
    "description": "Inspection plans, quality notifications, usage decision, defect recording, and quality results management during production.",
    "migration_objects": [],
    "keywords": [
      "quality management",
      "inspection plan",
      "quality notification",
      "defect recording",
      "usage decision",
      "SPC",
      "quality control",
      "QM in production"
    ]
  },
  {
    "id": "22G",
    "name": "Material Requirements Planning \u2013 Heuristics",
    "lob": "Manufacturing",
    "process_group": "Production Planning and Execution",
    "description": "Advanced supply planning using heuristics, optimizer, and predictive analytics for multi-level material planning.",
    "migration_objects": [],
    "keywords": [
      "MRP",
      "supply planning",
      "heuristics",
      "production planning",
      "material planning",
      "supply chain planning",
      "demand fulfillment"
    ]
  },
  {
    "id": "BDH",
    "name": "Inventory Management",
    "lob": "Supply Chain",
    "process_group": "Inventory Management",
    "description": "Real-time inventory management including goods movements, stock transfers, physical inventory, and valuation with multiple valuation approaches.",
    "migration_objects": [
      "Batch unique at material",
      "Characteristic",
      "Class"
    ],
    "keywords": [
      "inventory management",
      "stock management",
      "goods movements",
      "physical inventory",
      "stock transfers",
      "inventory valuation",
      "material ledger"
    ]
  },
  {
    "id": "6NI",
    "name": "Extended Warehouse Management",
    "lob": "Supply Chain",
    "process_group": "Warehouse Management",
    "description": "Advanced warehouse management with multi-level warehouse structures, warehouse tasks, wave management, slotting, and labor management.",
    "migration_objects": [
      "Bin assignment to production supply area"
    ],
    "keywords": [
      "extended warehouse management",
      "EWM",
      "warehouse tasks",
      "slotting",
      "wave management",
      "putaway",
      "picking",
      "labor management",
      "warehouse structure"
    ]
  },
  {
    "id": "J59_1",
    "name": "Transportation Management",
    "lob": "Supply Chain",
    "process_group": "Transportation Management",
    "description": "Transportation order management, carrier selection, freight cost calculation, route optimization, and freight settlement.",
    "migration_objects": [],
    "keywords": [
      "transportation management",
      "TM",
      "freight",
      "carrier",
      "routing",
      "freight cost",
      "shipment",
      "logistics execution",
      "transport order"
    ]
  },
  {
    "id": "BDG",
    "name": "Basic Warehouse Management",
    "lob": "Supply Chain",
    "process_group": "Warehouse Management",
    "description": "Basic WM with storage locations, transfer orders, goods receipt, picking, and put-away in a structured warehouse.",
    "migration_objects": [
      "Batch unique at material",
      "Characteristic",
      "Class"
    ],
    "keywords": [
      "warehouse management",
      "WM",
      "transfer orders",
      "picking",
      "put-away",
      "storage location",
      "goods receipt in warehouse"
    ]
  },
  {
    "id": "MEL",
    "name": "Demand Planning",
    "lob": "Supply Chain",
    "process_group": "Supply Chain Planning",
    "description": "Statistical demand forecasting, collaborative demand planning, and consensus planning with machine learning-based forecasting.",
    "migration_objects": [],
    "keywords": [
      "demand planning",
      "forecasting",
      "statistical forecast",
      "consensus planning",
      "collaborative planning",
      "machine learning forecast",
      "S&OP"
    ]
  },
  {
    "id": "J52",
    "name": "Supply Chain Analytics",
    "lob": "Supply Chain",
    "process_group": "Supply Chain Planning",
    "description": "Supply chain performance analytics including inventory days, service level, fill rate, and supply chain KPI dashboards.",
    "migration_objects": [],
    "keywords": [
      "supply chain analytics",
      "inventory days",
      "service level",
      "fill rate",
      "supply chain KPI",
      "supply chain performance",
      "logistics analytics"
    ]
  },
  {
    "id": "4LQ",
    "name": "Track and Trace",
    "lob": "Supply Chain",
    "process_group": "Logistics Execution",
    "description": "End-to-end shipment tracking, event management, and proactive exception notification for transportation visibility.",
    "migration_objects": [],
    "keywords": [
      "track and trace",
      "shipment tracking",
      "event management",
      "logistics visibility",
      "exception management",
      "transportation tracking"
    ]
  },
  {
    "id": "BNY",
    "name": "Goods Receipt from Subcontractor",
    "lob": "Supply Chain",
    "process_group": "Inventory Management",
    "description": "Goods receipt processing for materials returned from subcontractors including quality inspection and component reconciliation.",
    "migration_objects": [],
    "keywords": [
      "subcontractor receipt",
      "goods receipt",
      "subcontracting",
      "component reconciliation",
      "quality inspection",
      "toll manufacturing return"
    ]
  },
  {
    "id": "5HM",
    "name": "Foreign Trade Management",
    "lob": "Supply Chain",
    "process_group": "Logistics Execution",
    "description": "Import/export compliance including license management, embargo checks, customs declarations, and Intrastat reporting.",
    "migration_objects": [],
    "keywords": [
      "foreign trade",
      "import",
      "export",
      "customs",
      "trade compliance",
      "embargo",
      "Intrastat",
      "export control",
      "trade license"
    ]
  },
  {
    "id": "4BG",
    "name": "Dangerous Goods Management",
    "lob": "Supply Chain",
    "process_group": "Logistics Execution",
    "description": "Hazmat classification, dangerous goods documents, transport restrictions, and regulatory compliance for hazardous materials.",
    "migration_objects": [],
    "keywords": [
      "dangerous goods",
      "hazmat",
      "hazardous materials",
      "IATA",
      "IMDG",
      "ADR",
      "dangerous goods documents",
      "transport compliance"
    ]
  },
  {
    "id": "MGB",
    "name": "Core HR and Payroll",
    "lob": "Human Resources",
    "process_group": "HR Core and Payroll",
    "description": "Employee master data, organizational management, and integrated payroll processing with statutory compliance.",
    "migration_objects": [],
    "keywords": [
      "core HR",
      "payroll",
      "employee master data",
      "organizational management",
      "HR admin",
      "payroll processing",
      "statutory compliance"
    ]
  },
  {
    "id": "J1P",
    "name": "Time and Attendance Management",
    "lob": "Human Resources",
    "process_group": "Workforce Management",
    "description": "Time recording, absence management, shift planning, and time evaluation with integration to payroll.",
    "migration_objects": [],
    "keywords": [
      "time management",
      "attendance",
      "time recording",
      "absence management",
      "shift planning",
      "time evaluation",
      "workforce scheduling"
    ]
  },
  {
    "id": "1Q4",
    "name": "Time Recording",
    "lob": "Human Resources",
    "process_group": "Workforce Management",
    "description": "Employee self-service time recording against projects, cost centers, and work orders with approval workflow.",
    "migration_objects": [],
    "keywords": [
      "time recording",
      "timesheet",
      "time entry",
      "project time",
      "cost center time",
      "employee self-service",
      "time approval"
    ]
  },
  {
    "id": "MHO",
    "name": "Recruitment Management",
    "lob": "Human Resources",
    "process_group": "Talent Management",
    "description": "End-to-end recruitment including job posting, candidate management, interview scheduling, and offer management.",
    "migration_objects": [],
    "keywords": [
      "recruitment",
      "talent acquisition",
      "job posting",
      "candidate management",
      "hiring",
      "applicant tracking",
      "interview",
      "offer management"
    ]
  },
  {
    "id": "MHH",
    "name": "Learning and Development",
    "lob": "Human Resources",
    "process_group": "Talent Management",
    "description": "Training course management, learning catalog, mandatory training tracking, and employee learning history.",
    "migration_objects": [],
    "keywords": [
      "learning",
      "training",
      "L&D",
      "e-learning",
      "course management",
      "learning catalog",
      "mandatory training",
      "skills development"
    ]
  },
  {
    "id": "MHK",
    "name": "Performance and Goals",
    "lob": "Human Resources",
    "process_group": "Talent Management",
    "description": "Employee goal setting, performance reviews, continuous feedback, and performance calibration for talent decisions.",
    "migration_objects": [],
    "keywords": [
      "performance management",
      "goal setting",
      "performance review",
      "feedback",
      "appraisal",
      "talent management",
      "calibration"
    ]
  },
  {
    "id": "MHL",
    "name": "Compensation Management",
    "process_group": "Total Rewards",
    "description": "Salary review, merit increase, bonus planning, and compensation benchmarking with budget management.",
    "migration_objects": [],
    "keywords": [
      "compensation",
      "salary review",
      "merit increase",
      "bonus",
      "compensation planning",
      "total rewards",
      "pay equity"
    ],
    "lob": "Human Resources"
  },
  {
    "id": "MHM",
    "name": "Succession and Career Development",
    "lob": "Human Resources",
    "process_group": "Talent Management",
    "description": "Succession planning, talent pipeline management, career path definition, and critical role identification.",
    "migration_objects": [],
    "keywords": [
      "succession planning",
      "career development",
      "talent pipeline",
      "critical roles",
      "high potential",
      "workforce planning",
      "career paths"
    ]
  },
  {
    "id": "J76",
    "name": "Benefits Administration",
    "lob": "Human Resources",
    "process_group": "HR Core and Payroll",
    "description": "Employee benefits enrollment, plan administration, life events, open enrollment, and benefits billing.",
    "migration_objects": [],
    "keywords": [
      "benefits",
      "health insurance",
      "401k",
      "benefits enrollment",
      "open enrollment",
      "life events",
      "benefits administration"
    ]
  },
  {
    "id": "MHJ",
    "name": "Employee Experience Management",
    "lob": "Human Resources",
    "process_group": "Workforce Management",
    "description": "Employee surveys, pulse checks, engagement measurement, and manager actions to improve workforce satisfaction.",
    "migration_objects": [],
    "keywords": [
      "employee experience",
      "engagement",
      "surveys",
      "pulse check",
      "employee satisfaction",
      "HR analytics",
      "workforce engagement"
    ]
  },
  {
    "id": "J28",
    "name": "Project-Based Services",
    "lob": "Professional Services",
    "process_group": "Project Management",
    "description": "End-to-end project management including project planning, resource management, time and expense recording, billing, and revenue recognition.",
    "migration_objects": [],
    "keywords": [
      "project management",
      "project billing",
      "resource management",
      "time and expense",
      "project revenue recognition",
      "professional services",
      "project lifecycle"
    ]
  },
  {
    "id": "4GR",
    "name": "Commercial Project Management",
    "lob": "Professional Services",
    "process_group": "Project Management",
    "description": "Customer project execution with WBS-based planning, cost control, milestone billing, and project profitability tracking.",
    "migration_objects": [],
    "keywords": [
      "commercial project",
      "WBS",
      "project cost control",
      "milestone billing",
      "project profitability",
      "customer project",
      "EAC",
      "earned value"
    ]
  },
  {
    "id": "J29",
    "name": "Internal Projects and Real Estate",
    "lob": "Finance",
    "process_group": "Project Management",
    "description": "Internal capital projects and IT projects with investment program management, budget control, and capitalization.",
    "migration_objects": [],
    "keywords": [
      "internal projects",
      "capital projects",
      "investment program",
      "CAPEX",
      "project budgeting",
      "project capitalization",
      "IT projects"
    ]
  },
  {
    "id": "4GT",
    "name": "Project-Based Service Delivery",
    "lob": "Professional Services",
    "process_group": "Project Management",
    "description": "Service project execution including resource staffing, utilization tracking, project margin management, and customer acceptance.",
    "migration_objects": [
      "Business solution order"
    ],
    "keywords": [
      "service delivery",
      "project staffing",
      "utilization",
      "resource management",
      "project margin",
      "consulting",
      "professional services"
    ]
  },
  {
    "id": "MLS",
    "name": "Enterprise Portfolio and Project Management",
    "lob": "Professional Services",
    "process_group": "Project Management",
    "description": "Portfolio-level project prioritization, resource capacity planning, project governance, and strategic alignment.",
    "migration_objects": [],
    "keywords": [
      "portfolio management",
      "project governance",
      "resource capacity",
      "project prioritization",
      "PPM",
      "strategic alignment"
    ]
  },
  {
    "id": "4HH",
    "name": "Reactive Maintenance",
    "lob": "Asset Management",
    "process_group": "Maintenance Management",
    "description": "Breakdown maintenance processing including malfunction reporting, maintenance notification, work order creation, execution, and technical completion.",
    "migration_objects": [],
    "keywords": [
      "reactive maintenance",
      "breakdown maintenance",
      "maintenance notification",
      "work order",
      "corrective maintenance",
      "equipment repair"
    ]
  },
  {
    "id": "4HI",
    "name": "Preventive Maintenance",
    "lob": "Asset Management",
    "process_group": "Maintenance Management",
    "description": "Time-based and counter-based preventive maintenance scheduling, maintenance plans, work order generation, and PM performance tracking.",
    "migration_objects": [],
    "keywords": [
      "preventive maintenance",
      "PM schedule",
      "maintenance plan",
      "time-based",
      "counter-based",
      "planned maintenance",
      "reliability"
    ]
  },
  {
    "id": "4HJ",
    "name": "Predictive Maintenance",
    "lob": "Asset Management",
    "process_group": "Maintenance Management",
    "description": "Condition monitoring, sensor data integration, anomaly detection, and predictive maintenance alerts using machine learning.",
    "migration_objects": [],
    "keywords": [
      "predictive maintenance",
      "condition monitoring",
      "IoT",
      "sensor data",
      "anomaly detection",
      "machine learning",
      "Industry 4.0",
      "asset health"
    ]
  },
  {
    "id": "BKN",
    "name": "Equipment and Technical Objects",
    "lob": "Asset Management",
    "process_group": "Maintenance Management",
    "description": "Technical object hierarchy management including equipment master data, functional locations, and bill of material for technical assets.",
    "migration_objects": [],
    "keywords": [
      "equipment master",
      "functional location",
      "technical objects",
      "asset hierarchy",
      "maintenance objects",
      "technical assets",
      "equipment BOM"
    ]
  },
  {
    "id": "4YX",
    "name": "Management of Change",
    "lob": "Asset Management",
    "process_group": "Maintenance Management",
    "description": "Formal change management workflow for modifications to equipment, processes, or facilities including risk assessment and approval.",
    "migration_objects": [
      "Change request and activity for SAP Management of Change"
    ],
    "keywords": [
      "management of change",
      "MOC",
      "change management",
      "risk assessment",
      "change approval",
      "process safety",
      "HAZOP"
    ]
  },
  {
    "id": "J65",
    "name": "Resource Scheduling",
    "lob": "Asset Management",
    "process_group": "Maintenance Management",
    "description": "Technician scheduling, work order assignment, mobile work execution, and maintenance crew management with Gantt visualization.",
    "migration_objects": [],
    "keywords": [
      "resource scheduling",
      "technician scheduling",
      "Gantt",
      "work order assignment",
      "mobile maintenance",
      "crew management",
      "field service"
    ]
  },
  {
    "id": "4KL",
    "name": "Linear Asset Management",
    "lob": "Asset Management",
    "process_group": "Maintenance Management",
    "description": "Management of linear infrastructure assets like pipelines, roads, and cables with route-based defect recording and inspection.",
    "migration_objects": [],
    "keywords": [
      "linear assets",
      "pipeline management",
      "infrastructure assets",
      "route-based inspection",
      "cable management",
      "utility assets"
    ]
  },
  {
    "id": "5KT",
    "name": "Environment Health and Safety Management",
    "lob": "EHS",
    "process_group": "EHS",
    "description": "EHS incident management, risk assessment, safety observations, regulatory reporting, and compliance management.",
    "migration_objects": [],
    "keywords": [
      "EHS",
      "environment health safety",
      "incident management",
      "risk assessment",
      "safety observation",
      "regulatory compliance",
      "OSHA",
      "HSE"
    ]
  },
  {
    "id": "5LX",
    "name": "Hazardous Substance Management",
    "lob": "EHS",
    "process_group": "EHS",
    "description": "Dangerous substance classification, safety data sheets (SDS), exposure limits, and regulatory compliance for chemical substances.",
    "migration_objects": [],
    "keywords": [
      "hazardous substances",
      "SDS",
      "MSDS",
      "chemical management",
      "REACH",
      "CLP",
      "GHS",
      "substance inventory",
      "chemical compliance"
    ]
  },
  {
    "id": "5MO",
    "name": "Product Safety and Stewardship",
    "lob": "EHS",
    "process_group": "EHS",
    "description": "Product safety information management, regulatory compliance for product substances, and sustainability reporting.",
    "migration_objects": [],
    "keywords": [
      "product safety",
      "product stewardship",
      "REACH",
      "substance compliance",
      "product sustainability",
      "regulatory reporting",
      "product compliance"
    ]
  },
  {
    "id": "4YX_1",
    "name": "Industrial Hygiene and Safety",
    "lob": "EHS",
    "process_group": "EHS",
    "description": "Workplace risk assessment, exposure monitoring, protective equipment management, and occupational health management.",
    "migration_objects": [],
    "keywords": [
      "industrial hygiene",
      "workplace safety",
      "exposure monitoring",
      "PPE",
      "occupational health",
      "risk assessment",
      "safety compliance"
    ]
  },
  {
    "id": "BLE",
    "name": "Quality Management in Procurement",
    "lob": "Quality",
    "process_group": "Quality Management",
    "description": "Quality inspection for incoming goods including source inspection, goods receipt inspection, and supplier quality notifications.",
    "migration_objects": [],
    "keywords": [
      "quality management",
      "incoming inspection",
      "goods receipt inspection",
      "source inspection",
      "supplier quality",
      "QM in procurement"
    ]
  },
  {
    "id": "BLF_1",
    "name": "Quality Management in Sales",
    "lob": "Quality",
    "process_group": "Quality Management",
    "description": "Quality certificate management for outgoing deliveries including customer-specific quality requirements and certificate of analysis.",
    "migration_objects": [
      "Batch unique at material",
      "Characteristic",
      "Class"
    ],
    "keywords": [
      "quality certificates",
      "certificate of analysis",
      "outgoing quality",
      "customer quality",
      "QM in sales",
      "CoA"
    ]
  },
  {
    "id": "BLD",
    "name": "Basic Quality Management",
    "lob": "Quality",
    "process_group": "Quality Management",
    "description": "Quality planning, inspection lot processing, usage decision, defect recording, and quality notifications.",
    "migration_objects": [],
    "keywords": [
      "quality planning",
      "inspection lot",
      "usage decision",
      "defect recording",
      "quality notification",
      "QM basic",
      "inspection results"
    ]
  },
  {
    "id": "BDG_PLM",
    "name": "Product Lifecycle Management \u2013 Core",
    "lob": "PLM",
    "process_group": "Product Development",
    "description": "Product master data management, bill of materials, document management, classification, and engineering change management.",
    "migration_objects": [],
    "keywords": [
      "PLM",
      "product lifecycle",
      "bill of materials",
      "BOM",
      "engineering change",
      "document management",
      "product master data",
      "ECM"
    ]
  },
  {
    "id": "5FX",
    "name": "Recipe Development",
    "lob": "PLM",
    "process_group": "Product Development",
    "description": "Recipe management for process industries including ingredient specifications, formulation, and regulatory compliance for food and pharma.",
    "migration_objects": [],
    "keywords": [
      "recipe development",
      "formulation",
      "ingredient management",
      "food recipe",
      "pharma recipe",
      "process industry PLM",
      "specification management"
    ]
  },
  {
    "id": "5HB",
    "name": "Product Compliance",
    "lob": "PLM",
    "process_group": "Product Development",
    "description": "Compliance with product substance regulations including REACH, RoHS, conflict minerals, and labeling requirements.",
    "migration_objects": [],
    "keywords": [
      "product compliance",
      "REACH",
      "RoHS",
      "conflict minerals",
      "labeling",
      "substance compliance",
      "regulatory compliance",
      "product regulations"
    ]
  },
  {
    "id": "J70",
    "name": "Engineering Change Management",
    "lob": "PLM",
    "process_group": "Product Development",
    "description": "Structured management of engineering changes with approval workflow, effectivity management, and impact analysis across BOM/routing.",
    "migration_objects": [],
    "keywords": [
      "engineering change",
      "ECM",
      "change order",
      "ECO",
      "effectivity",
      "BOM change",
      "routing change",
      "change management",
      "revision control"
    ]
  },
  {
    "id": "55F",
    "name": "Automotive Supply to Customer \u2013 Inventory Management",
    "lob": "Manufacturing",
    "process_group": "Automotive",
    "description": "Automotive industry-specific processes for JIT/JIS delivery, customer-specific sequencing, and automotive order management.",
    "migration_objects": [],
    "keywords": [
      "automotive",
      "JIT",
      "JIS",
      "just in sequence",
      "sequencing",
      "automotive delivery",
      "OEM supply",
      "automotive logistics"
    ]
  },
  {
    "id": "4LF",
    "name": "Group Reporting \u2013 Legal Consolidation",
    "lob": "Finance",
    "process_group": "Financial Close and Consolidation",
    "description": "Full legal consolidation with entity reporting, intercompany eliminations, minority interest, currency translation, and consolidated financial statements.",
    "migration_objects": [],
    "keywords": [
      "group reporting",
      "consolidation",
      "legal consolidation",
      "intercompany elimination",
      "minority interest",
      "IFRS consolidation",
      "group financial statements"
    ]
  },
  {
    "id": "J61",
    "name": "Tax Reporting and Analytics",
    "lob": "Finance",
    "process_group": "Tax Management",
    "description": "Direct tax provision calculation, uncertain tax positions, effective tax rate analysis, and country-by-country reporting.",
    "migration_objects": [],
    "keywords": [
      "tax reporting",
      "tax provision",
      "uncertain tax",
      "effective tax rate",
      "CbCR",
      "country by country",
      "BEPS",
      "deferred tax"
    ]
  },
  {
    "id": "B10",
    "name": "Governance Risk and Compliance",
    "lob": "Finance",
    "process_group": "Governance Risk and Compliance",
    "description": "Internal controls management, SOX compliance, audit management, risk assessment, and continuous control monitoring.",
    "migration_objects": [],
    "keywords": [
      "GRC",
      "governance",
      "SOX",
      "internal controls",
      "audit management",
      "risk assessment",
      "compliance monitoring",
      "COSO"
    ]
  },
  {
    "id": "BMD",
    "name": "Audit Management",
    "lob": "Finance",
    "process_group": "Governance Risk and Compliance",
    "description": "Audit planning, execution tracking, finding management, corrective actions, and audit reporting.",
    "migration_objects": [],
    "keywords": [
      "audit management",
      "internal audit",
      "audit planning",
      "audit findings",
      "corrective actions",
      "external audit",
      "audit trail"
    ]
  },
  {
    "id": "BME",
    "name": "Policy and Procedure Management",
    "lob": "Finance",
    "process_group": "Governance Risk and Compliance",
    "description": "Policy library management, employee acknowledgement tracking, policy review workflows, and compliance attestation.",
    "migration_objects": [],
    "keywords": [
      "policy management",
      "procedures",
      "compliance policies",
      "acknowledgement",
      "policy review",
      "regulatory policies",
      "SOX attestation"
    ]
  },
  {
    "id": "J86",
    "name": "Public Sector \u2013 Funds Management",
    "lob": "Finance",
    "process_group": "Public Sector",
    "description": "Government budget management with funds, fund centers, commitment items, and budgetary ledger for public sector compliance.",
    "migration_objects": [],
    "keywords": [
      "funds management",
      "public sector",
      "government budget",
      "fund center",
      "commitment item",
      "budgetary ledger",
      "appropriation"
    ]
  },
  {
    "id": "4ZG",
    "name": "Grants Management",
    "lob": "Finance",
    "process_group": "Public Sector",
    "description": "Grant lifecycle management from application through award, expense tracking, billing, and compliance reporting for government grants.",
    "migration_objects": [],
    "keywords": [
      "grants management",
      "government grants",
      "grant application",
      "grant award",
      "grant compliance",
      "sponsored programs",
      "research grants"
    ]
  },
  {
    "id": "J87",
    "name": "Utilities \u2013 Contract Accounts Receivable",
    "lob": "Finance",
    "process_group": "Utilities",
    "description": "Mass billing and collection for utility customers including meter reading, consumption billing, and payment management.",
    "migration_objects": [],
    "keywords": [
      "utilities",
      "FI-CA",
      "contract accounts",
      "meter reading",
      "consumption billing",
      "utility billing",
      "mass billing"
    ]
  },
  {
    "id": "J46",
    "name": "Payment Processing",
    "lob": "Finance",
    "process_group": "Accounts Payable",
    "description": "Automated payment runs including ACH, wire, check, and electronic fund transfers with payment advice and remittance information.",
    "migration_objects": [],
    "keywords": [
      "payment processing",
      "payment run",
      "ACH",
      "wire transfer",
      "check",
      "remittance",
      "payment advice",
      "bank transfer",
      "EFT"
    ]
  },
  {
    "id": "J47",
    "name": "Intercompany Reconciliation",
    "lob": "Finance",
    "process_group": "Accounting and Financial Close",
    "description": "Automated intercompany balance matching, reconciliation workflow, and difference resolution for month-end close.",
    "migration_objects": [],
    "keywords": [
      "intercompany reconciliation",
      "ICR",
      "intercompany balance",
      "intercompany matching",
      "intercompany close",
      "reconciliation workflow"
    ]
  },
  {
    "id": "J48",
    "name": "Cost Allocation",
    "lob": "Finance",
    "process_group": "Management Accounting",
    "description": "Allocation of shared service center costs, IT costs, and corporate overhead using flexible allocation methods.",
    "migration_objects": [],
    "keywords": [
      "cost allocation",
      "shared services",
      "overhead allocation",
      "IT cost allocation",
      "corporate overhead",
      "cost recharging",
      "chargeback"
    ]
  },
  {
    "id": "J49",
    "name": "Working Capital Management",
    "lob": "Finance",
    "process_group": "Treasury and Cash Management",
    "description": "Dynamic discounting, supply chain finance, and early payment optimization to improve working capital metrics.",
    "migration_objects": [],
    "keywords": [
      "working capital",
      "dynamic discounting",
      "supply chain finance",
      "early payment",
      "DPO",
      "DSO",
      "cash conversion cycle"
    ]
  },
  {
    "id": "J50",
    "name": "Statutory Reporting",
    "lob": "Finance",
    "process_group": "Accounting and Financial Close",
    "description": "Country-specific statutory financial statements, electronic filing of tax and regulatory reports, and report mapping to local GAAP.",
    "migration_objects": [],
    "keywords": [
      "statutory reporting",
      "local GAAP",
      "IFRS",
      "financial statements",
      "electronic filing",
      "regulatory reporting",
      "annual report"
    ]
  },
  {
    "id": "4NA",
    "name": "Margin Analysis",
    "lob": "Finance",
    "process_group": "Management Accounting",
    "description": "Real-time margin analysis by market segment, customer group, or product line using account-based COPA with actual cost flows.",
    "migration_objects": [],
    "keywords": [
      "margin analysis",
      "COPA",
      "profitability",
      "market segment",
      "product margin",
      "customer margin",
      "contribution margin",
      "real-time COPA"
    ]
  },
  {
    "id": "J71",
    "name": "Real Estate Contract Management",
    "lob": "Finance",
    "process_group": "Real Estate",
    "description": "Real estate lease and rental contract management including condition management, service charges, and contract correspondence.",
    "migration_objects": [],
    "keywords": [
      "real estate contracts",
      "lease management",
      "rental contracts",
      "service charges",
      "rent review",
      "lease agreements",
      "property leasing"
    ]
  },
  {
    "id": "4HQ",
    "name": "Customer Financial Services",
    "lob": "Finance",
    "process_group": "Customer Service",
    "description": "Financial services processes including loan management, leasing, installment payment plans, and customer credit facilities.",
    "migration_objects": [],
    "keywords": [
      "customer financing",
      "loan management",
      "leasing",
      "installment",
      "customer credit",
      "financial services",
      "consumer finance"
    ]
  },
  {
    "id": "BMJ",
    "name": "Service Order Management",
    "lob": "Service",
    "process_group": "Service Operations",
    "description": "Field service order management including service notification, resource scheduling, parts management, and service billing.",
    "migration_objects": [],
    "keywords": [
      "service order",
      "field service",
      "service notification",
      "resource scheduling",
      "service parts",
      "service billing",
      "after-sales service"
    ]
  },
  {
    "id": "4GT_SVC",
    "name": "Service Contract Management",
    "lob": "Service",
    "process_group": "Service Operations",
    "description": "Service contract creation, SLA management, contract billing, warranty tracking, and contract renewal.",
    "migration_objects": [],
    "keywords": [
      "service contract",
      "SLA",
      "service level agreement",
      "warranty",
      "contract billing",
      "service renewal",
      "customer support"
    ]
  },
  {
    "id": "BMK",
    "name": "In-House Repair",
    "lob": "Service",
    "process_group": "Service Operations",
    "description": "Customer product repair management in internal workshops including receipt, diagnosis, repair execution, and return to customer.",
    "migration_objects": [],
    "keywords": [
      "in-house repair",
      "repair order",
      "workshop",
      "customer repair",
      "depot repair",
      "service workshop",
      "returns repair"
    ]
  },
  {
    "id": "BML",
    "name": "Field Service Management",
    "lob": "Service",
    "process_group": "Service Operations",
    "description": "On-site field service with mobile work execution, technician dispatch, GPS tracking, and customer signature capture.",
    "migration_objects": [],
    "keywords": [
      "field service",
      "mobile service",
      "technician dispatch",
      "GPS",
      "on-site service",
      "mobile work order",
      "field technician"
    ]
  },
  {
    "id": "J66",
    "name": "Customer Service and Support",
    "lob": "Service",
    "process_group": "Customer Service",
    "description": "Customer case management, knowledge base, service request processing, and customer self-service portal integration.",
    "migration_objects": [],
    "keywords": [
      "customer service",
      "customer support",
      "case management",
      "knowledge base",
      "service request",
      "helpdesk",
      "customer portal"
    ]
  },
  {
    "id": "4W9",
    "name": "Sustainability Management",
    "lob": "Sustainability",
    "process_group": "ESG Reporting",
    "description": "Carbon footprint tracking, ESG data collection, sustainability reporting (GRI, CSRD), and green accounting.",
    "migration_objects": [],
    "keywords": [
      "sustainability",
      "ESG",
      "carbon footprint",
      "GHG emissions",
      "CSRD",
      "GRI",
      "green accounting",
      "scope 1 2 3",
      "sustainability reporting"
    ]
  },
  {
    "id": "4WA",
    "name": "Environmental Management",
    "lob": "Sustainability",
    "process_group": "ESG Reporting",
    "description": "Environmental compliance reporting, waste management, energy consumption tracking, and environmental incident management.",
    "migration_objects": [],
    "keywords": [
      "environmental management",
      "waste management",
      "energy consumption",
      "environmental compliance",
      "ISO 14001",
      "emissions reporting",
      "environmental incidents"
    ]
  },
  {
    "id": "4WC",
    "name": "Product Carbon Footprint",
    "lob": "Sustainability",
    "process_group": "ESG Reporting",
    "description": "Product-level carbon footprint calculation based on materials, manufacturing processes, and supply chain emissions.",
    "migration_objects": [],
    "keywords": [
      "product carbon footprint",
      "PCF",
      "scope 3",
      "product emissions",
      "carbon accounting",
      "supply chain emissions",
      "carbon per product"
    ]
  },
  {
    "id": "5HP",
    "name": "Advanced Intercompany Stock Transfer",
    "lob": "Supply Chain",
    "process_group": "Logistics Execution",
    "description": "Multi-leg intercompany stock transfers with automatic billing, in-transit inventory, and cross-company visibility.",
    "migration_objects": [],
    "keywords": [
      "intercompany transfer",
      "stock transfer",
      "in-transit",
      "cross-company stock",
      "multi-leg transfer",
      "intercompany logistics"
    ]
  },
  {
    "id": "58A",
    "name": "Retail \u2013 Point of Sale Integration",
    "lob": "Sales",
    "process_group": "Retail",
    "description": "Integration with POS systems for real-time sales data, inventory updates, and promotion execution in retail environments.",
    "migration_objects": [],
    "keywords": [
      "POS",
      "point of sale",
      "retail",
      "store integration",
      "sales data",
      "retail inventory",
      "promotion execution",
      "store operations"
    ]
  },
  {
    "id": "4ZR",
    "name": "Retail \u2013 Merchandise Planning",
    "lob": "Sales",
    "process_group": "Retail",
    "description": "Assortment planning, merchandise buying, OTB (open-to-buy) management, and markdown optimization for retail.",
    "migration_objects": [],
    "keywords": [
      "merchandise planning",
      "assortment planning",
      "open-to-buy",
      "OTB",
      "markdown optimization",
      "retail planning",
      "buying"
    ]
  },
  {
    "id": "2GT",
    "name": "Mining \u2013 Long-Term Planning",
    "lob": "Manufacturing",
    "process_group": "Mining",
    "description": "Long-term mine planning, ore body management, production scheduling, and mining equipment maintenance.",
    "migration_objects": [],
    "keywords": [
      "mining",
      "mine planning",
      "ore body",
      "production scheduling",
      "mining equipment",
      "mineral planning"
    ]
  },
  {
    "id": "BPJ",
    "name": "Public Sector \u2013 Budget Control",
    "lob": "Finance",
    "process_group": "Public Sector",
    "description": "Public sector budget execution with availability control, commitment management, and expenditure tracking against appropriations.",
    "migration_objects": [],
    "keywords": [
      "public sector budget",
      "budget execution",
      "availability control",
      "appropriation",
      "government expenditure",
      "budget control",
      "PSM"
    ]
  },
  {
    "id": "4MQ",
    "name": "Embedded Analytics",
    "lob": "Cross-Functional",
    "process_group": "Analytics",
    "description": "Real-time operational analytics embedded in SAP Fiori apps using CDS views, analytical list pages, and live calculations.",
    "migration_objects": [],
    "keywords": [
      "embedded analytics",
      "Fiori analytics",
      "real-time analytics",
      "CDS views",
      "analytical list page",
      "KPI tiles",
      "operational reporting"
    ]
  },
  {
    "id": "4MR",
    "name": "Financial Planning and Analysis",
    "lob": "Finance",
    "process_group": "Analytics",
    "description": "Integrated financial planning with P&L, balance sheet, and cash flow planning connected to operational planning.",
    "migration_objects": [],
    "keywords": [
      "FP&A",
      "financial planning",
      "budgeting",
      "forecasting",
      "P&L planning",
      "balance sheet planning",
      "integrated planning",
      "financial analysis"
    ]
  },
  {
    "id": "1GF",
    "name": "Management Reporting",
    "lob": "Finance",
    "process_group": "Analytics",
    "description": "Management information system with customizable reports, segment reporting, and executive dashboards for decision support.",
    "migration_objects": [],
    "keywords": [
      "management reporting",
      "MIS",
      "executive dashboard",
      "segment reporting",
      "management accounts",
      "decision support",
      "financial reporting"
    ]
  },
  {
    "id": "4QL",
    "name": "SAP Integration Suite Connectivity",
    "lob": "Cross-Functional",
    "process_group": "Integration",
    "description": "Pre-built integration content for connecting S/4HANA to SuccessFactors, Ariba, Concur, and third-party systems.",
    "migration_objects": [],
    "keywords": [
      "integration",
      "SAP Integration Suite",
      "BTP",
      "iFlow",
      "pre-built integration",
      "API integration",
      "middleware",
      "connectivity"
    ]
  },
  {
    "id": "J85",
    "name": "Concur Travel and Expense Integration",
    "lob": "Finance",
    "process_group": "Accounts Payable",
    "description": "Integration with SAP Concur for automated expense report processing, corporate credit card reconciliation, and travel booking.",
    "migration_objects": [],
    "keywords": [
      "Concur",
      "travel expense",
      "expense report",
      "corporate card",
      "T&E",
      "expense management",
      "travel management",
      "employee expenses"
    ]
  },
  {
    "id": "4KP",
    "name": "Ariba Integration \u2013 Procurement",
    "lob": "Procurement",
    "process_group": "Operational Procurement",
    "description": "Integration with SAP Ariba for purchase requisitions, purchase orders, and invoice processing via Ariba Network.",
    "migration_objects": [],
    "keywords": [
      "Ariba",
      "Ariba Network",
      "supplier network",
      "purchase order",
      "invoice",
      "procure-to-pay",
      "supplier collaboration",
      "Ariba integration"
    ]
  },
  {
    "id": "4KQ",
    "name": "SuccessFactors Integration \u2013 HR",
    "lob": "Human Resources",
    "process_group": "HR Core and Payroll",
    "description": "Integration with SAP SuccessFactors for employee master data, organizational data, and HR processes.",
    "migration_objects": [],
    "keywords": [
      "SuccessFactors",
      "HR integration",
      "employee data",
      "organizational data",
      "HCM",
      "talent management",
      "payroll integration"
    ]
  },
  {
    "id": "5FJ_1",
    "name": "Advanced Compliance and Reporting",
    "lob": "Finance",
    "process_group": "Tax Management",
    "description": "Country-specific advanced compliance reporting including e-invoicing, digital reporting obligations, and real-time tax authority submissions.",
    "migration_objects": [
      "Characteristic"
    ],
    "keywords": [
      "e-invoicing",
      "digital reporting",
      "real-time reporting",
      "tax authority",
      "compliance reporting",
      "mandatory reporting"
    ]
  },
  {
    "id": "J13_LEASE",
    "name": "Lease Accounting \u2013 IFRS 16",
    "lob": "Finance",
    "process_group": "Asset Accounting",
    "description": "IFRS 16 lease accounting with right-of-use asset tracking, lease liability amortization, lease reassessments, and disclosure reporting.",
    "migration_objects": [],
    "keywords": [
      "IFRS 16",
      "lease accounting",
      "right-of-use",
      "ROU asset",
      "lease liability",
      "lease reassessment",
      "ASC 842"
    ]
  },
  {
    "id": "BHJ",
    "name": "Inventory Valuation",
    "lob": "Finance",
    "process_group": "Inventory Management",
    "description": "Material ledger actual costing, actual cost distribution, price differences, and multi-currency material ledger.",
    "migration_objects": [],
    "keywords": [
      "inventory valuation",
      "material ledger",
      "actual costing",
      "price differences",
      "multi-currency",
      "standard price",
      "moving average price"
    ]
  },
  {
    "id": "4WT",
    "name": "Shelf Life Management",
    "lob": "Supply Chain",
    "process_group": "Inventory Management",
    "description": "Expiry date tracking, FEFO picking, minimum remaining shelf life management, and shelf life warnings in procurement and sales.",
    "migration_objects": [],
    "keywords": [
      "shelf life",
      "expiry date",
      "FEFO",
      "minimum shelf life",
      "perishables",
      "batch expiry",
      "food safety",
      "pharma expiry"
    ]
  },
  {
    "id": "J80",
    "name": "Trade Finance",
    "lob": "Finance",
    "process_group": "Treasury and Cash Management",
    "description": "Letter of credit management, documentary collections, bank guarantees, and trade finance instruments.",
    "migration_objects": [],
    "keywords": [
      "trade finance",
      "letter of credit",
      "LC",
      "documentary collection",
      "bank guarantee",
      "trade instruments",
      "import export finance"
    ]
  },
  {
    "id": "BMR",
    "name": "Spend Control and Budget Management",
    "lob": "Finance",
    "process_group": "Management Accounting",
    "description": "Real-time budget availability control, commitment tracking, and budget consumption reporting across cost centers and internal orders.",
    "migration_objects": [],
    "keywords": [
      "budget control",
      "availability control",
      "commitment",
      "budget consumption",
      "spending control",
      "budget monitoring",
      "cost control"
    ]
  },
  {
    "id": "4KM",
    "name": "Customer Rebate Management",
    "lob": "Sales",
    "process_group": "Sales Billing",
    "description": "Condition-based customer rebate processing with real-time accruals, periodic settlement, and rebate agreement management.",
    "migration_objects": [],
    "keywords": [
      "customer rebate",
      "rebate accrual",
      "settlement",
      "volume rebate",
      "rebate agreement",
      "trade promotion",
      "customer incentive"
    ]
  },
  {
    "id": "BHK",
    "name": "Make-to-Stock Production",
    "lob": "Manufacturing",
    "process_group": "Production Planning and Execution",
    "description": "Standard make-to-stock manufacturing with MRP-driven production orders, capacity leveling, and finished goods inventory management.",
    "migration_objects": [],
    "keywords": [
      "make-to-stock",
      "MTS",
      "production planning",
      "MRP",
      "capacity leveling",
      "finished goods",
      "mass production",
      "standard manufacturing"
    ]
  },
  {
    "id": "BHL",
    "name": "Engineer-to-Order",
    "lob": "Manufacturing",
    "process_group": "Production Planning and Execution",
    "description": "Project-based manufacturing for highly custom products with individual engineering, project management integration, and milestone billing.",
    "migration_objects": [],
    "keywords": [
      "engineer-to-order",
      "ETO",
      "custom engineering",
      "project manufacturing",
      "complex manufacturing",
      "one-of-a-kind",
      "engineered products"
    ]
  },
  {
    "id": "J53",
    "name": "Master Data Management",
    "lob": "Cross-Functional",
    "process_group": "Master Data",
    "description": "Central master data governance for customers, suppliers, materials, and business partners with data quality and workflow.",
    "migration_objects": [],
    "keywords": [
      "master data management",
      "MDM",
      "data governance",
      "customer master",
      "vendor master",
      "material master",
      "business partner",
      "data quality"
    ]
  },
  {
    "id": "BNA",
    "name": "Procurement of Indirect Materials and Services",
    "lob": "Procurement",
    "process_group": "Operational Procurement",
    "description": "Procurement of MRO, office supplies, and indirect services through catalogs, shopping carts, and non-stock purchase orders.",
    "migration_objects": [],
    "keywords": [
      "indirect procurement",
      "MRO",
      "office supplies",
      "non-stock",
      "catalog ordering",
      "spot buy",
      "tail spend"
    ]
  },
  {
    "id": "BNB",
    "name": "Supplier Invoice Processing with OCR",
    "lob": "Procurement",
    "process_group": "Accounts Payable",
    "description": "AI-powered invoice capture from email and scan with automatic PO matching, exception routing, and touchless processing.",
    "migration_objects": [],
    "keywords": [
      "invoice OCR",
      "touchless invoice",
      "AI invoice",
      "automatic matching",
      "invoice capture",
      "invoice automation"
    ]
  },
  {
    "id": "BNC",
    "name": "Vendor Evaluation and Performance",
    "lob": "Procurement",
    "process_group": "Sourcing and Contract Management",
    "description": "Systematic supplier performance scoring across quality, delivery, service, and price dimensions with scorecards.",
    "migration_objects": [],
    "keywords": [
      "vendor evaluation",
      "supplier scorecard",
      "supplier performance",
      "supplier rating",
      "vendor scorecard",
      "delivery performance",
      "quality performance"
    ]
  },
  {
    "id": "BND",
    "name": "Consignment Processing",
    "lob": "Procurement",
    "process_group": "Operational Procurement",
    "description": "Consignment stock management where supplier goods are stored at customer site and liability transfers only on consumption.",
    "migration_objects": [],
    "keywords": [
      "consignment",
      "vendor consignment",
      "consignment stock",
      "pay on consumption",
      "supplier-owned stock"
    ]
  },
  {
    "id": "BNE",
    "name": "Outline Agreements \u2013 Scheduling",
    "lob": "Procurement",
    "process_group": "Operational Procurement",
    "description": "Long-term scheduling agreements with automatic delivery schedule generation based on MRP requirements.",
    "migration_objects": [],
    "keywords": [
      "scheduling agreement",
      "outline agreement",
      "long-term supply",
      "delivery schedule",
      "MRP integration",
      "blanket agreement"
    ]
  },
  {
    "id": "4KR",
    "name": "Supplier Risk Management",
    "lob": "Procurement",
    "process_group": "Sourcing and Contract Management",
    "description": "Continuous monitoring of supplier financial health, geographic risks, ESG compliance, and supply chain disruption signals.",
    "migration_objects": [],
    "keywords": [
      "supplier risk",
      "supply chain risk",
      "vendor risk",
      "supplier resilience",
      "ESG compliance",
      "supply chain disruption",
      "third party risk"
    ]
  },
  {
    "id": "J64",
    "name": "Financial Statement Closing",
    "lob": "Finance",
    "process_group": "Accounting and Financial Close",
    "description": "Guided financial close cockpit with task management, status tracking, automated checks, and audit-ready documentation.",
    "migration_objects": [],
    "keywords": [
      "financial close",
      "close cockpit",
      "task management",
      "period end close",
      "close checklist",
      "fast close",
      "financial statements"
    ]
  },
  {
    "id": "J66_FIN",
    "name": "Predictive Accounting",
    "lob": "Finance",
    "process_group": "Accounting and Financial Close",
    "description": "AI-powered accounting predictions for likely payables, receivables, and cash positions based on historical patterns.",
    "migration_objects": [],
    "keywords": [
      "predictive accounting",
      "AI accounting",
      "predictive payables",
      "cash prediction",
      "forward-looking accounting",
      "machine learning finance"
    ]
  },
  {
    "id": "BJA",
    "name": "Multi-Currency Accounting",
    "lob": "Finance",
    "process_group": "Accounting and Financial Close",
    "description": "Parallel currency management with transaction currency, company code currency, and group currency postings simultaneously.",
    "migration_objects": [],
    "keywords": [
      "multi-currency",
      "foreign currency",
      "currency translation",
      "exchange rate",
      "parallel currency",
      "FX accounting",
      "currency revaluation"
    ]
  },
  {
    "id": "BJB",
    "name": "Currency Risk Management",
    "lob": "Finance",
    "process_group": "Treasury and Cash Management",
    "description": "FX exposure identification, hedging strategy, forward contracts, and FX hedge effectiveness testing.",
    "migration_objects": [],
    "keywords": [
      "FX risk",
      "currency risk",
      "hedging",
      "forward contracts",
      "FX exposure",
      "hedge accounting",
      "currency management"
    ]
  },
  {
    "id": "BJC",
    "name": "Commodity Risk Management",
    "lob": "Finance",
    "process_group": "Treasury and Cash Management",
    "description": "Commodity price risk management with physical and financial positions, hedging, and mark-to-market valuation.",
    "migration_objects": [],
    "keywords": [
      "commodity risk",
      "commodity hedging",
      "physical commodity",
      "mark-to-market",
      "commodity trading",
      "price risk"
    ]
  },
  {
    "id": "BJD",
    "name": "Liquidity Planning",
    "lob": "Finance",
    "process_group": "Treasury and Cash Management",
    "description": "Short and medium-term cash flow forecasting from AR, AP, and treasury positions with scenario analysis.",
    "migration_objects": [],
    "keywords": [
      "liquidity planning",
      "cash forecast",
      "cash flow planning",
      "liquidity forecast",
      "short-term funding",
      "cash position"
    ]
  },
  {
    "id": "BJF",
    "name": "Bank Fee Analysis",
    "lob": "Finance",
    "process_group": "Treasury and Cash Management",
    "description": "Analysis and optimization of bank service charges, account analysis statements, and banking cost benchmarking.",
    "migration_objects": [],
    "keywords": [
      "bank fees",
      "bank charges",
      "bank cost optimization",
      "account analysis",
      "banking costs",
      "bank relationship management"
    ]
  },
  {
    "id": "4LA",
    "name": "Central Finance",
    "lob": "Finance",
    "process_group": "Accounting and Financial Close",
    "description": "Central financial data aggregation from multiple SAP and non-SAP source systems for unified group reporting and analysis.",
    "migration_objects": [],
    "keywords": [
      "central finance",
      "CFIN",
      "financial aggregation",
      "group finance",
      "financial harmonization",
      "SAP landscape consolidation"
    ]
  },
  {
    "id": "4LB",
    "name": "Intercompany Financial Reporting",
    "lob": "Finance",
    "process_group": "Accounting and Financial Close",
    "description": "Automated intercompany matching, netting, and settlement to streamline month-end close across multiple entities.",
    "migration_objects": [],
    "keywords": [
      "intercompany reporting",
      "IC matching",
      "IC netting",
      "IC settlement",
      "intercompany close",
      "related party transactions"
    ]
  },
  {
    "id": "4LC",
    "name": "Segment Reporting",
    "lob": "Finance",
    "process_group": "Management Accounting",
    "description": "IFRS 8 compliant segment reporting with operating segment definition, allocation, and disclosure notes.",
    "migration_objects": [],
    "keywords": [
      "segment reporting",
      "IFRS 8",
      "operating segments",
      "management segments",
      "divisional reporting",
      "segment disclosure"
    ]
  },
  {
    "id": "4LD",
    "name": "Joint Venture Accounting",
    "lob": "Finance",
    "process_group": "Accounting and Financial Close",
    "description": "JV accounting for oil, gas, and mining including cutback calculations, billing to JV partners, and AFE management.",
    "migration_objects": [],
    "keywords": [
      "joint venture accounting",
      "JV",
      "cutback",
      "AFE",
      "oil gas",
      "JV partner billing",
      "joint operation"
    ]
  },
  {
    "id": "4LE",
    "name": "Production Cost Reporting",
    "lob": "Finance",
    "process_group": "Management Accounting",
    "description": "Detailed production cost analysis with material, labor, and overhead breakdowns by production order and work center.",
    "migration_objects": [],
    "keywords": [
      "production cost",
      "cost reporting",
      "manufacturing cost analysis",
      "cost breakdown",
      "labor cost",
      "overhead cost"
    ]
  },
  {
    "id": "4WD",
    "name": "Production Scheduling with Finite Capacity",
    "lob": "Manufacturing",
    "process_group": "Production Planning and Execution",
    "description": "Finite capacity scheduling using heuristics and optimization to create feasible production plans within capacity constraints.",
    "migration_objects": [],
    "keywords": [
      "finite capacity",
      "production scheduling",
      "capacity planning",
      "capacity optimization",
      "scheduling",
      "production feasibility",
      "capacity constraints"
    ]
  },
  {
    "id": "4WE",
    "name": "Kanban \u2013 Pull-Based Production",
    "lob": "Manufacturing",
    "process_group": "Production Planning and Execution",
    "description": "Kanban-based pull production control with signal cards, container management, and automatic replenishment.",
    "migration_objects": [],
    "keywords": [
      "kanban",
      "pull production",
      "kanban signal",
      "lean manufacturing",
      "pull system",
      "replenishment kanban",
      "JIT production"
    ]
  },
  {
    "id": "4WF",
    "name": "Process Order Management",
    "lob": "Manufacturing",
    "process_group": "Production Planning and Execution",
    "description": "Process industry manufacturing with recipes, resources, process orders, phases, and GMP-compliant documentation.",
    "migration_objects": [],
    "keywords": [
      "process orders",
      "process manufacturing",
      "recipe management",
      "phases",
      "GMP",
      "pharmaceutical manufacturing",
      "food production",
      "chemical processing"
    ]
  },
  {
    "id": "4WG",
    "name": "MES Integration",
    "lob": "Manufacturing",
    "process_group": "Production Planning and Execution",
    "description": "Bidirectional integration with manufacturing execution systems for work orders, confirmations, and quality results.",
    "migration_objects": [],
    "keywords": [
      "MES",
      "manufacturing execution",
      "work order integration",
      "production confirmation",
      "OEE",
      "production data",
      "machine integration"
    ]
  },
  {
    "id": "4WH",
    "name": "Production Quality Control",
    "lob": "Manufacturing",
    "process_group": "Quality Management",
    "description": "In-process quality checks, statistical process control (SPC), control charts, and immediate corrective actions during production.",
    "migration_objects": [],
    "keywords": [
      "in-process quality",
      "SPC",
      "statistical process control",
      "control chart",
      "quality check",
      "production quality",
      "defect prevention"
    ]
  },
  {
    "id": "4WI",
    "name": "Tool and Resource Management",
    "lob": "Manufacturing",
    "process_group": "Production Planning and Execution",
    "description": "Production tool tracking, tool certification management, tool assignment to work centers, and tool lifecycle.",
    "migration_objects": [],
    "keywords": [
      "tool management",
      "production tools",
      "tooling",
      "work center resources",
      "tool assignment",
      "tool lifecycle",
      "jig and fixture"
    ]
  },
  {
    "id": "4WJ",
    "name": "Production Waste Management",
    "lob": "Manufacturing",
    "process_group": "Production Planning and Execution",
    "description": "Scrap recording, rework management, yield tracking, and waste cost allocation in manufacturing operations.",
    "migration_objects": [],
    "keywords": [
      "scrap",
      "rework",
      "waste management",
      "yield",
      "production waste",
      "manufacturing losses",
      "scrap recording"
    ]
  },
  {
    "id": "4WK",
    "name": "Assembly Management",
    "lob": "Manufacturing",
    "process_group": "Production Planning and Execution",
    "description": "Assembly order management for complex assemblies with multi-level BOM explosion, serial number assignment, and assembly completion.",
    "migration_objects": [],
    "keywords": [
      "assembly",
      "assembly order",
      "BOM explosion",
      "serial number",
      "product assembly",
      "multi-level BOM",
      "assembly line"
    ]
  },
  {
    "id": "4WL",
    "name": "Supply Chain Event Management",
    "lob": "Supply Chain",
    "process_group": "Supply Chain Planning",
    "description": "Real-time supply chain event monitoring with exception alerts, escalation management, and root cause analysis.",
    "migration_objects": [],
    "keywords": [
      "supply chain events",
      "exception management",
      "supply chain alerts",
      "disruption management",
      "event management",
      "supply chain visibility"
    ]
  },
  {
    "id": "4WM",
    "name": "Multi-Site Inventory Optimization",
    "lob": "Supply Chain",
    "process_group": "Supply Chain Planning",
    "description": "Network-wide inventory optimization balancing service levels against total inventory investment across multiple distribution centers.",
    "migration_objects": [],
    "keywords": [
      "inventory optimization",
      "multi-site",
      "safety stock optimization",
      "service level",
      "distribution network",
      "inventory investment",
      "multi-echelon"
    ]
  },
  {
    "id": "4WN",
    "name": "Inbound Logistics",
    "lob": "Supply Chain",
    "process_group": "Logistics Execution",
    "description": "Inbound delivery scheduling, dock appointment management, goods receipt processing, and unloading management.",
    "migration_objects": [],
    "keywords": [
      "inbound logistics",
      "dock scheduling",
      "goods receipt",
      "unloading",
      "delivery appointment",
      "receiving dock",
      "yard management"
    ]
  },
  {
    "id": "4WO",
    "name": "Outbound Logistics",
    "lob": "Supply Chain",
    "process_group": "Logistics Execution",
    "description": "Outbound delivery processing including picking, packing, route assignment, and goods issue confirmation.",
    "migration_objects": [],
    "keywords": [
      "outbound logistics",
      "picking",
      "packing",
      "goods issue",
      "delivery processing",
      "outbound delivery",
      "route assignment"
    ]
  },
  {
    "id": "4WP",
    "name": "Returns Management \u2013 Reverse Logistics",
    "lob": "Supply Chain",
    "process_group": "Logistics Execution",
    "description": "Reverse logistics processing for customer and vendor returns including inspection, refurbishment, scrapping, and credit note.",
    "migration_objects": [],
    "keywords": [
      "reverse logistics",
      "returns processing",
      "refurbishment",
      "scrapping",
      "vendor returns",
      "customer returns",
      "return logistics"
    ]
  },
  {
    "id": "4WQ",
    "name": "Cross-Docking",
    "lob": "Supply Chain",
    "process_group": "Warehouse Management",
    "description": "Cross-docking operations with direct transfer from inbound to outbound without storage, reducing handling and lead time.",
    "migration_objects": [],
    "keywords": [
      "cross-docking",
      "direct transfer",
      "warehouse efficiency",
      "flow-through",
      "transit distribution",
      "cross dock"
    ]
  },
  {
    "id": "4WR",
    "name": "Warehouse Yard Management",
    "lob": "Supply Chain",
    "process_group": "Warehouse Management",
    "description": "Yard management with vehicle check-in/out, trailer parking, dock appointment coordination, and driver self-check-in.",
    "migration_objects": [],
    "keywords": [
      "yard management",
      "vehicle management",
      "trailer parking",
      "dock appointment",
      "driver check-in",
      "gate management"
    ]
  },
  {
    "id": "4WS",
    "name": "Slotting and Warehouse Layout",
    "lob": "Supply Chain",
    "process_group": "Warehouse Management",
    "description": "Warehouse slotting optimization based on velocity, weight, and picking ergonomics to maximize picking efficiency.",
    "migration_objects": [],
    "keywords": [
      "slotting",
      "warehouse layout",
      "picking optimization",
      "velocity analysis",
      "warehouse design",
      "bin assignment",
      "ergonomic picking"
    ]
  },
  {
    "id": "4WT_SCM",
    "name": "Cold Chain Management",
    "lob": "Supply Chain",
    "process_group": "Logistics Execution",
    "description": "Temperature-controlled logistics for pharma, food, and chemicals with temperature monitoring and deviation alerts.",
    "migration_objects": [],
    "keywords": [
      "cold chain",
      "temperature control",
      "temperature monitoring",
      "cold storage",
      "pharma logistics",
      "food safety",
      "deviation alert"
    ]
  },
  {
    "id": "4WU",
    "name": "Last Mile Delivery",
    "lob": "Supply Chain",
    "process_group": "Logistics Execution",
    "description": "Last mile delivery optimization with route planning, driver mobile apps, proof of delivery, and customer notifications.",
    "migration_objects": [],
    "keywords": [
      "last mile delivery",
      "route planning",
      "proof of delivery",
      "POD",
      "driver app",
      "customer notification",
      "delivery optimization"
    ]
  },
  {
    "id": "MHN",
    "name": "Payroll Accounting Integration",
    "lob": "Human Resources",
    "process_group": "HR Core and Payroll",
    "description": "Integration of HR payroll results with Finance including G/L posting, cost center allocation, and pay slip generation.",
    "migration_objects": [],
    "keywords": [
      "payroll integration",
      "payroll G/L",
      "payroll posting",
      "cost center payroll",
      "HR finance integration",
      "pay slip",
      "salary posting"
    ]
  },
  {
    "id": "MHP",
    "name": "Workforce Analytics",
    "lob": "Human Resources",
    "process_group": "HR Analytics",
    "description": "HR analytics including headcount reporting, attrition analysis, diversity metrics, and workforce planning dashboards.",
    "migration_objects": [],
    "keywords": [
      "workforce analytics",
      "HR analytics",
      "headcount",
      "attrition",
      "diversity",
      "workforce planning",
      "people analytics",
      "HR dashboard"
    ]
  },
  {
    "id": "MHQ",
    "name": "Absence and Leave Management",
    "lob": "Human Resources",
    "process_group": "Workforce Management",
    "description": "Employee leave request, approval workflow, leave balance tracking, and integration with payroll and time management.",
    "migration_objects": [],
    "keywords": [
      "leave management",
      "absence management",
      "leave request",
      "leave balance",
      "vacation",
      "sick leave",
      "leave approval",
      "HR leave"
    ]
  },
  {
    "id": "MHR",
    "name": "Employee Self-Service",
    "lob": "Human Resources",
    "process_group": "HR Core and Payroll",
    "description": "Employee portal for viewing pay slips, updating personal data, submitting leave requests, and accessing HR documents.",
    "migration_objects": [],
    "keywords": [
      "employee self-service",
      "ESS",
      "HR portal",
      "pay slip",
      "personal data",
      "employee portal",
      "HR self-service"
    ]
  },
  {
    "id": "MHS",
    "name": "Manager Self-Service",
    "lob": "Human Resources",
    "process_group": "HR Core and Payroll",
    "description": "Manager portal for team management including headcount approval, performance reviews, and HR approvals.",
    "migration_objects": [],
    "keywords": [
      "manager self-service",
      "MSS",
      "manager portal",
      "team management",
      "HR approvals",
      "headcount management"
    ]
  },
  {
    "id": "BKM",
    "name": "Order Promising and Allocation",
    "lob": "Sales",
    "process_group": "Sales Order Management",
    "description": "Product allocation management for constrained supply scenarios with priority rules and fair-share distribution.",
    "migration_objects": [],
    "keywords": [
      "order promising",
      "product allocation",
      "constrained supply",
      "fair share",
      "allocation rules",
      "demand prioritization",
      "supply allocation"
    ]
  },
  {
    "id": "BKN_SALES",
    "name": "Price and Condition Management",
    "lob": "Sales",
    "process_group": "Sales Order Management",
    "description": "Complex pricing condition management including customer-specific pricing, price lists, discounts, and surcharges.",
    "migration_objects": [],
    "keywords": [
      "pricing",
      "conditions",
      "price list",
      "discount",
      "surcharge",
      "customer price",
      "pricing procedure",
      "condition technique"
    ]
  },
  {
    "id": "BKO",
    "name": "Free Goods Processing",
    "lob": "Sales",
    "process_group": "Sales Order Management",
    "description": "Automatic determination and processing of free goods (bonus items) based on purchase quantity thresholds.",
    "migration_objects": [],
    "keywords": [
      "free goods",
      "bonus items",
      "promotional goods",
      "quantity thresholds",
      "automatic free goods",
      "sales promotion"
    ]
  },
  {
    "id": "BKP",
    "name": "Third-Party Order Processing",
    "lob": "Sales",
    "process_group": "Sales Order Management",
    "description": "Drop-ship order fulfillment where goods are delivered directly from supplier to customer with automatic PO generation.",
    "migration_objects": [],
    "keywords": [
      "third party order",
      "drop ship",
      "vendor direct",
      "purchase order automatic",
      "supplier direct delivery",
      "drop shipment"
    ]
  },
  {
    "id": "BKQ",
    "name": "Billing Document Management",
    "lob": "Sales",
    "process_group": "Sales Billing",
    "description": "Invoice creation, credit and debit memo processing, pro forma invoices, and billing document management.",
    "migration_objects": [],
    "keywords": [
      "billing",
      "invoice",
      "credit memo",
      "debit memo",
      "pro forma",
      "billing document",
      "customer invoice",
      "billing run"
    ]
  },
  {
    "id": "4ZF",
    "name": "Subscription Management \u2013 Recurring",
    "lob": "Sales",
    "process_group": "Sales Billing",
    "description": "Subscription lifecycle management with automatic renewal, upgrade/downgrade, usage-based charging, and contract management.",
    "migration_objects": [],
    "keywords": [
      "subscription management",
      "recurring revenue",
      "subscription billing",
      "auto-renewal",
      "usage-based",
      "SaaS",
      "subscription lifecycle"
    ]
  },
  {
    "id": "4ZG_SALES",
    "name": "E-Commerce Integration",
    "lob": "Sales",
    "process_group": "Sales Order Management",
    "description": "Integration with e-commerce platforms for online order capture, real-time inventory availability, and customer account management.",
    "migration_objects": [],
    "keywords": [
      "ecommerce",
      "online order",
      "webshop",
      "digital commerce",
      "B2C",
      "B2B portal",
      "online sales",
      "ecommerce integration"
    ]
  },
  {
    "id": "4HL",
    "name": "Reliability-Centered Maintenance",
    "lob": "Asset Management",
    "process_group": "Maintenance Management",
    "description": "RCM analysis for critical assets with failure mode identification, maintenance task optimization, and risk-based scheduling.",
    "migration_objects": [],
    "keywords": [
      "reliability centered maintenance",
      "RCM",
      "failure mode",
      "FMEA",
      "critical assets",
      "risk-based maintenance",
      "maintenance optimization"
    ]
  },
  {
    "id": "4HM",
    "name": "Spare Parts Management",
    "lob": "Asset Management",
    "process_group": "Maintenance Management",
    "description": "Maintenance spare parts planning, critical spare identification, MRO inventory optimization, and component exchange.",
    "migration_objects": [],
    "keywords": [
      "spare parts",
      "MRO",
      "critical spares",
      "spare parts planning",
      "maintenance inventory",
      "component exchange",
      "parts management"
    ]
  },
  {
    "id": "4HN",
    "name": "Asset Performance Management",
    "lob": "Asset Management",
    "process_group": "Maintenance Management",
    "description": "Asset health monitoring with OEE calculation, downtime analysis, MTBF/MTTR tracking, and asset performance dashboards.",
    "migration_objects": [],
    "keywords": [
      "asset performance",
      "OEE",
      "overall equipment effectiveness",
      "MTBF",
      "MTTR",
      "downtime analysis",
      "asset health",
      "reliability"
    ]
  },
  {
    "id": "4HO",
    "name": "Calibration Management",
    "lob": "Asset Management",
    "process_group": "Maintenance Management",
    "description": "Measurement equipment calibration management with calibration certificates, recall management, and integration to quality.",
    "migration_objects": [],
    "keywords": [
      "calibration",
      "measurement equipment",
      "calibration certificate",
      "equipment calibration",
      "metrology",
      "ISO 9001",
      "calibration recall"
    ]
  },
  {
    "id": "4HP_AM",
    "name": "Fleet Management",
    "lob": "Asset Management",
    "process_group": "Maintenance Management",
    "description": "Vehicle fleet management including maintenance scheduling, fuel consumption, driver assignment, and fleet cost reporting.",
    "migration_objects": [],
    "keywords": [
      "fleet management",
      "vehicle management",
      "fleet maintenance",
      "fuel management",
      "driver assignment",
      "fleet cost",
      "motor pool"
    ]
  },
  {
    "id": "5HC",
    "name": "Bill of Materials Management",
    "lob": "PLM",
    "process_group": "Product Development",
    "description": "Multi-level BOM management with engineering BOM, manufacturing BOM, and sales BOM with change management.",
    "migration_objects": [],
    "keywords": [
      "BOM",
      "bill of materials",
      "engineering BOM",
      "manufacturing BOM",
      "EBOM",
      "MBOM",
      "BOM management",
      "multi-level BOM"
    ]
  },
  {
    "id": "5HD",
    "name": "Routing and Work Center Management",
    "lob": "PLM",
    "process_group": "Product Development",
    "description": "Manufacturing routing definition with operations, sequences, standard times, and work center assignment.",
    "migration_objects": [],
    "keywords": [
      "routing",
      "work center",
      "operation sequence",
      "standard times",
      "manufacturing routing",
      "process routing",
      "work instructions"
    ]
  },
  {
    "id": "5HE",
    "name": "Document Management System",
    "lob": "PLM",
    "process_group": "Product Development",
    "description": "Central document management with version control, classification, status management, and CAD integration.",
    "migration_objects": [],
    "keywords": [
      "document management",
      "DMS",
      "version control",
      "CAD integration",
      "technical documents",
      "drawing management",
      "document classification"
    ]
  },
  {
    "id": "5HF",
    "name": "Project System",
    "lob": "PLM",
    "process_group": "Product Development",
    "description": "Project network planning, milestone tracking, resource assignment, and project cost control for product development.",
    "migration_objects": [],
    "keywords": [
      "project system",
      "PS",
      "WBS",
      "network planning",
      "milestone",
      "project cost",
      "product development project",
      "R&D project"
    ]
  },
  {
    "id": "5HG",
    "name": "Configuration Management",
    "lob": "PLM",
    "process_group": "Product Development",
    "description": "Product configuration baseline management, as-built versus as-designed comparison, and configuration item tracking.",
    "migration_objects": [],
    "keywords": [
      "configuration management",
      "as-built",
      "as-designed",
      "product baseline",
      "configuration items",
      "revision control",
      "product history"
    ]
  },
  {
    "id": "4QM",
    "name": "Joule AI Assistant",
    "lob": "Cross-Functional",
    "process_group": "Artificial Intelligence",
    "description": "Generative AI assistant embedded in S/4HANA for natural language queries, process guidance, and intelligent recommendations.",
    "migration_objects": [],
    "keywords": [
      "Joule",
      "AI assistant",
      "generative AI",
      "natural language",
      "conversational AI",
      "AI recommendations",
      "intelligent assistant"
    ]
  },
  {
    "id": "4QN",
    "name": "Intelligent Automation with RPA",
    "lob": "Cross-Functional",
    "process_group": "Intelligent Technologies",
    "description": "Robotic process automation integration for repetitive high-volume tasks with bot management and audit trail.",
    "migration_objects": [],
    "keywords": [
      "RPA",
      "robotic process automation",
      "automation",
      "bots",
      "intelligent automation",
      "repetitive tasks",
      "process automation"
    ]
  },
  {
    "id": "4QO",
    "name": "Machine Learning in Finance",
    "lob": "Finance",
    "process_group": "Artificial Intelligence",
    "description": "ML-powered cash application, payment prediction, dunning optimization, and anomaly detection in financial processes.",
    "migration_objects": [],
    "keywords": [
      "machine learning",
      "AI finance",
      "cash application",
      "payment prediction",
      "anomaly detection",
      "intelligent finance",
      "AI-powered accounting"
    ]
  },
  {
    "id": "4QP",
    "name": "Predictive Analytics in Supply Chain",
    "lob": "Supply Chain",
    "process_group": "Artificial Intelligence",
    "description": "AI-driven demand sensing, supply risk prediction, and inventory optimization recommendations.",
    "migration_objects": [],
    "keywords": [
      "predictive analytics",
      "demand sensing",
      "supply risk prediction",
      "AI supply chain",
      "intelligent planning",
      "demand AI",
      "supply chain AI"
    ]
  },
  {
    "id": "4QQ",
    "name": "Business Process Intelligence",
    "lob": "Cross-Functional",
    "process_group": "Analytics",
    "description": "Process mining integrated with S/4HANA to identify bottlenecks, compliance deviations, and optimization opportunities.",
    "migration_objects": [],
    "keywords": [
      "process mining",
      "process intelligence",
      "Signavio",
      "bottleneck analysis",
      "process optimization",
      "process conformance",
      "process analytics"
    ]
  },
  {
    "id": "J88",
    "name": "SAP Business Network Integration",
    "lob": "Cross-Functional",
    "process_group": "Integration",
    "description": "Integration with SAP Business Network for supplier collaboration, invoice exchange, and logistics visibility.",
    "migration_objects": [],
    "keywords": [
      "business network",
      "supplier network",
      "Ariba Network",
      "EDI",
      "supplier collaboration",
      "e-invoicing",
      "network integration"
    ]
  },
  {
    "id": "J89",
    "name": "SAP Analytics Cloud Integration",
    "lob": "Finance",
    "process_group": "Analytics",
    "description": "Live connection from S/4HANA to SAP Analytics Cloud for advanced planning, predictive analytics, and storytelling.",
    "migration_objects": [],
    "keywords": [
      "SAC",
      "SAP Analytics Cloud",
      "advanced analytics",
      "planning integration",
      "predictive analytics",
      "storytelling",
      "live data connection"
    ]
  },
  {
    "id": "JL1",
    "name": "Germany \u2013 Reporting and Localization",
    "lob": "Finance",
    "process_group": "Localization",
    "description": "German-specific reporting requirements including Elster electronic tax filing, ZM reporting, and German GAAP compliance.",
    "migration_objects": [],
    "keywords": [
      "Germany",
      "Elster",
      "ZM",
      "German GAAP",
      "HGB",
      "German tax",
      "German localization",
      "DACH"
    ]
  },
  {
    "id": "JL2",
    "name": "United States \u2013 Reporting and Localization",
    "lob": "Finance",
    "process_group": "Localization",
    "description": "US-specific requirements including US GAAP, 1099 reporting, state and local tax, and ACH payment formats.",
    "migration_objects": [],
    "keywords": [
      "United States",
      "US GAAP",
      "1099",
      "state tax",
      "ACH",
      "US localization",
      "FASB",
      "ASC",
      "US tax"
    ]
  },
  {
    "id": "JL3",
    "name": "United Kingdom \u2013 Reporting and Localization",
    "lob": "Finance",
    "process_group": "Localization",
    "description": "UK-specific compliance including Making Tax Digital (MTD), PAYE, and UK GAAP reporting.",
    "migration_objects": [],
    "keywords": [
      "United Kingdom",
      "MTD",
      "Making Tax Digital",
      "PAYE",
      "UK GAAP",
      "UK VAT",
      "UK localization"
    ]
  },
  {
    "id": "JL4",
    "name": "France \u2013 Reporting and Localization",
    "lob": "Finance",
    "process_group": "Localization",
    "description": "French-specific reporting including FEC, DAS2, Chorus Pro e-invoicing, and French GAAP compliance.",
    "migration_objects": [],
    "keywords": [
      "France",
      "FEC",
      "DAS2",
      "Chorus Pro",
      "French GAAP",
      "PCG",
      "French localization",
      "French VAT"
    ]
  },
  {
    "id": "JL5",
    "name": "India \u2013 GST and Localization",
    "lob": "Finance",
    "process_group": "Localization",
    "description": "Indian GST compliance including GSTIN management, GSTR filings, e-invoicing, e-way bill, and TDS/TCS handling.",
    "migration_objects": [],
    "keywords": [
      "India",
      "GST",
      "GSTIN",
      "GSTR",
      "e-invoicing",
      "e-way bill",
      "TDS",
      "TCS",
      "Indian localization"
    ]
  },
  {
    "id": "JL6",
    "name": "Mexico \u2013 CFDI and Localization",
    "lob": "Finance",
    "process_group": "Localization",
    "description": "Mexican electronic invoicing with CFDI generation, SAT certification, and Mexican tax compliance.",
    "migration_objects": [],
    "keywords": [
      "Mexico",
      "CFDI",
      "SAT",
      "electronic invoicing",
      "Mexican tax",
      "RFC",
      "complement",
      "Mexican localization"
    ]
  },
  {
    "id": "JL7",
    "name": "China \u2013 Golden Tax Integration",
    "lob": "Finance",
    "process_group": "Localization",
    "description": "Chinese VAT fapiao management, Golden Tax System integration, and Chinese GAAP accounting.",
    "migration_objects": [],
    "keywords": [
      "China",
      "Golden Tax",
      "fapiao",
      "VAT invoice",
      "Chinese GAAP",
      "CAS",
      "Chinese localization",
      "VAT compliance"
    ]
  }
]

# Quick lookup dict
SCOPE_ITEM_BY_ID = {item["id"]: item for item in SCOPE_ITEMS}

def get_catalogue_text():
    """Returns all scope items as a single formatted string for LLM context."""
    lines = []
    for item in SCOPE_ITEMS:
        lines.append(f"[{item['id']}] {item['name']} ({item['lob']} > {item['process_group']})")
        lines.append(f"  {item['description']}")
        if item.get('migration_objects'):
            lines.append(f"  Migration Objects: {', '.join(item['migration_objects'])}")
    return "\n".join(lines)
