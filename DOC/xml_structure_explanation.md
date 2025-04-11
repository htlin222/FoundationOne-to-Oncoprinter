# XML Structure: Foundation Medicine Cancer Report

This document explains the structure of the XML file `ORD-0808717-01.xml` in a tree-style format. This XML contains a comprehensive cancer genomic report from Foundation Medicine.

## Overall Structure

```
rr:ResultsReport
├── rr:CustomerInformation
│   ├── rr:ReferenceID
│   ├── rr:CSN
│   ├── rr:TRF
│   ├── rr:MRN
│   ├── rr:PhysicianId
│   └── rr:NPI
└── rr:ResultsPayload
    ├── FinalReport
    │   ├── Application
    │   │   └── ApplicationSettings
    │   │       └── ApplicationSetting
    │   │           ├── n
    │   │           └── Value
    │   ├── DemographicCorrectionDate
    │   ├── ReportId
    │   ├── SampleName
    │   ├── Version
    │   ├── Sample
    │   │   ├── FM_Id
    │   │   ├── SampleId
    │   │   ├── BlockId
    │   │   ├── TRFNumber
    │   │   ├── TestType
    │   │   ├── SpecFormat
    │   │   ├── ReceivedDate
    │   │   └── processSites
    │   │       └── processSite (multiple entries)
    │   ├── PMI (Patient Medical Information)
    │   │   ├── ReportId
    │   │   ├── MRN
    │   │   ├── FullName
    │   │   ├── FirstName
    │   │   ├── LastName
    │   │   ├── SubmittedDiagnosis
    │   │   ├── Gender
    │   │   ├── DOB
    │   │   ├── OrderingMD
    │   │   ├── OrderingMDId
    │   │   ├── Pathologist
    │   │   ├── CopiedPhysician1
    │   │   ├── MedFacilName
    │   │   ├── MedFacilID
    │   │   ├── SpecSite
    │   │   ├── CollDate
    │   │   ├── ReceivedDate
    │   │   └── CountryOfOrigin
    │   ├── PertinentNegatives
    │   │   └── PertinentNegative (multiple entries)
    │   │       └── Gene
    │   ├── Summaries (with attributes: alterationCount, clinicalTrialCount, etc.)
    │   ├── VariantProperties
    │   │   └── VariantProperty (multiple entries with attributes: geneName, isVUS, variantName)
    │   ├── priorTests
    │   ├── Genes
    │   │   └── Gene (multiple entries)
    │   │       ├── n (gene name)
    │   │       ├── Include
    │   │       ├── Alterations
    │   │       │   └── Alteration (multiple entries)
    │   │       │       ├── n (alteration name)
    │   │       │       ├── AlterationProperties
    │   │       │       │   └── AlterationProperty (attributes: isEquivocal, name)
    │   │       │       ├── Interpretation (detailed clinical interpretation)
    │   │       │       ├── Include
    │   │       │       ├── ClinicalTrialNote
    │   │       │       ├── Therapies
    │   │       │       │   └── Therapy (optional)
    │   │       │       │       ├── Name
    │   │       │       │       ├── GenericName
    │   │       │       │       ├── FDAApproved
    │   │       │       │       └── Rationale
    │   │       │       ├── ReferenceLinks
    │   │       │       └── ClinicalTrialLinks
    │   │       └── ReferenceLinks
    │   ├── Trials
    │   │   └── Trial (multiple entries)
    │   │       ├── Gene
    │   │       ├── Alteration
    │   │       ├── Title
    │   │       ├── StudyPhase
    │   │       └── ... (other trial information)
    │   ├── References
    │   │   └── Reference (multiple entries)
    │   │       ├── ReferenceId
    │   │       ├── FullCitation
    │   │       └── Include
    │   └── Signatures
    │       └── Signature
    │           ├── ServerTime
    │           └── OpName
    └── variant-report (with multiple attributes)
        └── samples
            └── sample (with attributes: bait-set, mean-exon-depth, name, nucleic-acid-type)
```

## Key Components Explained

### 1. Customer Information
Contains basic identifiers for the patient and physician, including reference IDs and physician information.

### 2. Results Payload
The main content of the report, divided into two major sections:

#### 2.1 Final Report
Contains comprehensive clinical information including:

- **Sample Information**: Details about the specimen, processing sites, and test type
- **Patient Medical Information (PMI)**: Patient demographics, diagnosis, and medical facility details
- **Genomic Findings**:
  - **PertinentNegatives**: Genes specifically noted as not having mutations
  - **VariantProperties**: List of genetic variants with properties like VUS (Variant of Unknown Significance) status
  - **Genes**: Detailed information about each gene with alterations
    - Each gene contains one or more alterations
    - Each alteration includes detailed clinical interpretation, therapy implications, and trial information
  - **Trials**: Clinical trials relevant to the detected genetic alterations
  - **References**: Scientific literature citations supporting the interpretations

#### 2.2 Variant Report
Technical information about the sequencing and analysis, including sample quality metrics.

## Notable Findings in This Report

This particular report shows:
- Patient diagnosed with Colon adenocarcinoma (CRC)
- Key genetic alterations including:
  - KRAS G12D mutation
  - TP53 Y236D mutation
  - Several variants of unknown significance (VUS)
- Pertinent negative findings for BRAF and NRAS
- Microsatellite status and Tumor Mutation Burden could not be determined
- Multiple clinical trials relevant to the KRAS mutation

## Clinical Significance

The report provides comprehensive genomic profiling to guide treatment decisions:
- Identifies actionable mutations that may respond to targeted therapies
- Highlights resistance markers that suggest certain treatments may be ineffective
- Connects findings to relevant clinical trials
- Provides scientific evidence through extensive references

This structured format allows clinicians to quickly access critical genomic information for clinical decision-making in precision oncology.
