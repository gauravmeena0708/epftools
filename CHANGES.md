# epftools Changelog

## v0.2.1 - Multi-Source Report Aggregation (Latest)

### New Features

#### **MultiSourceReportAggregator** 📊
Aggregate reports from multiple EPF data sources into unified dashboards.

**Data sources supported:**
- Claims (Claim.xls)
- EPFiGMS (grievances)
- E-Sign pending
- DSC (Digital Signature) pending
- Transfer-In claims
- Form-249 (Basic/Primary/Others)

```python
from epftools import MultiSourceReportAggregator

config = {
    'claims': 'Claim.xls',
    'epfigms': 'EPFiGMS.xlsx',
    'esign': 'esign.xlsx',
    'dsc': 'dsc.xlsx',
    'transfer': 'transfer.csv',
    'basic': '249_pending_list_online.xlsx',
    'primary': '249_pending_list_primary.xlsx',
    'others': '249_pending_list_others.xlsx'
}

aggregator = MultiSourceReportAggregator(config)
dashboard = aggregator.generate_consolidated_report()
aggregator.export_to_html('dashboard.html')
```

**Use cases:**
- Unified dashboard creation
- Cross-system reporting
- Comprehensive pendency tracking
- Management information systems (MIS)

---

## v0.2.0 - Major Release

## 🎉 What's New

### Critical Fixes
- ✅ **Dependencies**: Added `install_requires` to setup.py with all required packages
- ✅ **Resource Leak**: Fixed file handle leak in `PDFTools.split_pdf()`
- ✅ **Temp File Cleanup**: `PDFGenerator2` now properly cleans up temporary HTML files
- ✅ **Error Handling**: Comprehensive error handling and logging added to all modules

### New Modules

#### 1. **PendencyProcessor** 📊
Extract and analyze EPFO pendency reports from PDFs.
```python
from epftools import PendencyProcessor

processor = PendencyProcessor()
df = processor.process_pendency_files("Pendency DA.PDF", "Pendency SS.PDF")
summary = processor.create_pivot_summary(df, 'days_cat', 'group')
```

Features:
- Parse pendency PDF reports
- Officer-wise grouping (GM, NK, VK, SR)
- Day categorization
- Pivot table generation

#### 2. **ValidationUtils** ✔️
EPF-specific data validation utilities.
```python
from epftools import ValidationUtils

# Validate Member ID
is_valid, msg = ValidationUtils.validate_member_id("PYKRP00534130000030651")

# Parse components
components = ValidationUtils.parse_member_id("PYKRP00534130000030651")
print(components['establishment_code'])  # '0053413'

# Batch validation
results = ValidationUtils.validate_batch(member_ids, ValidationUtils.validate_member_id)
```

Validators for:
- Member IDs, Claim IDs, Establishment codes
- Task IDs, Group IDs, Form types
- Dates, Pending days
- DataFrame columns

#### 3. **RejectionCategorizer** 🤖 (Optional)
ML-based categorization of rejection reasons.
```python
from epftools import RejectionCategorizer

categorizer = RejectionCategorizer()
categorizer.train('reason_category.csv')

# Predict categories
df = categorizer.predict_dataframe(claims_df, reason_column='REJECT_REASON')

# Review low confidence predictions
low_conf = categorizer.get_low_confidence_predictions(df, threshold=0.6)
```

Requires: `pip install epftools[ml]`

### Enhanced Modules

#### **DataFrameStyler** 🎨
Added new styling methods:
- `color_change_from_previous()` - Highlight time-series changes
- `color_by_threshold_with_highlight()` - Threshold-based highlighting
- `get_styled_with_quantiles()` - Combined top-3 + quantile styling

#### **ExcelMerger** 📑
- Better error handling
- Progress reporting
- Handles corrupted files gracefully

#### **PDFGenerator & PDFGenerator2** 📄
- Input validation
- Comprehensive error messages
- Logging support

#### **PDFOCR** 🔍
- Progress reporting
- Batch processing with error recovery
- Summary statistics

### Code Quality Improvements

1. **Logging**: All modules now use Python's logging framework
2. **Docstrings**: Comprehensive documentation for all public methods
3. **Error Messages**: Clear, actionable error messages
4. **Type Safety**: Better input validation throughout

### Package Structure
```
src/epftools/
├── __init__.py (v0.2.0)
├── claim_processor.py
├── periodicity_processor.py
├── pendency_processor.py          # NEW
├── pdf_generator.py
├── pdf_generator2.py
├── pdf_tools.py
├── pdf_ocr.py
├── df_styler.py
├── excel_merger.py
├── validation_utils.py             # NEW
└── rejection_categorizer.py        # NEW
```

## 📦 Installation

### Basic Installation
```bash
pip install -e git+https://github.com/gauravmeena0708/epftools#egg=epftools
```

### With Optional Features
```bash
# With OCR support
pip install epftools[ocr]

# With ML categorization
pip install epftools[ml]

# With all features
pip install epftools[ocr,ml]
```

## 🔧 Dependencies

### Core (Always Installed)
- pandas >= 1.3.0
- numpy >= 1.20.0
- reportlab >= 3.6.0
- pdfkit >= 1.0.0
- PyPDF2 >= 2.0.0
- beautifulsoup4 >= 4.9.0
- plotly >= 5.0.0

### Optional Features
- **OCR**: pytesseract, pdf2image, Pillow
- **ML**: scikit-learn >= 1.0.0

## ⚠️ Breaking Changes
- Removed unused `module1.py`
- Changed from `from epftools import *` to explicit imports
- Version bump from 0.1.5 → 0.2.0

## 🐛 Bug Fixes
- Fixed resource leak in `PDFTools` (file handles)
- Fixed temp file cleanup in `PDFGenerator2`
- Fixed silent failures in `ExcelMerger`
- Improved error handling across all modules

## 📝 Migration Guide

### From v0.1.5 to v0.2.0

**Old (still works):**
```python
from epftools import *
```

**New (recommended):**
```python
from epftools import ClaimProcessor, PDFGenerator, DataFrameStyler
```

**New features:**
```python
# Pendency processing
from epftools import PendencyProcessor
processor = PendencyProcessor()

# Validation
from epftools import ValidationUtils
is_valid, msg = ValidationUtils.validate_member_id(member_id)

# ML categorization (requires scikit-learn)
from epftools import RejectionCategorizer
categorizer = RejectionCategorizer()
```

## 🎯 What's Next (Future Releases)

- Unit tests for all modules
- Package restructuring (processors/, generators/, utils/)
- Performance optimizations
- More ML models for claim analysis
- API documentation site

## 🙏 Contributors
- All improvements based on analysis of existing notebooks
- Extracted common patterns from `nbs/` folder

---

**Full Changelog**: v0.1.5...v0.2.0
