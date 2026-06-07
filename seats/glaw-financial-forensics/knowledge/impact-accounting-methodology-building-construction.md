
# Impact Accounting Methodology for Building Construction


Report / February 2025

### Authors and Acknowledgments

###### Authors

Chris Magwood Victor Olgyay Katie Ross, Microsoft

Authors listed alphabetically. All authors from RMI unless otherwise noted.

###### Contacts

Chris Magwood, cmagwood@rmi.org

###### Copyrights and Citation

Victor Olgyay, Chris Magwood, and Katie Ross, Impact Accounting Methodology for Building Construction, RMI, 2025, https://rmi.org/insight/impact-accounting-methodology-for-building-construction.

RMI values collaboration and aims to accelerate the energy transition through sharing knowledge and insights. We therefore allow interested parties to reference, share, and cite our work through the Creative Commons CC BY-SA 4.0 license. https://creativecommons.org/licenses/by-sa/4.0/.

All images used are from iStock.com unless otherwise noted.

###### Acknowledgments

The authors would like to thank Dinesh Chandra Das, Morgan German, Baha Sadreddin, and Ben Stanley of Microsoft; Cristal Ortiz of LinkedIn; Stacy Smedley of Building Transparency; and Kate Simonen and Azeezah Priyota of the University of Washington for their contributions to the research and development of this paper.

###### About RMI

RMI is an independent nonprofit, founded in 1982 as Rocky Mountain Institute, that transforms global energy systems through market-driven solutions to align with a 1.5°C future and secure a clean, prosperous, zero-carbon future for all. We work in the world’s most critical geographies and engage businesses, policymakers, communities, and NGOs to identify and scale energy system interventions that will cut climate pollution at least 50 percent by 2030. RMI has offices in Basalt and Boulder, Colorado; New York City; Oakland, California; Washington, D.C.; Abuja, Nigeria; and Beijing.

## Contents

###### Rationale . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 5 General Guidance from the GHG Protocol for the Impact Accounting Method . . . . . . . . . . . . . . . . . . . . . . . 12 Calculation Method for Impact Accounting . . . . . . . . . . . . . . . . . . 15

Division of Project Costs and Materials. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 16

- Emissions Calculations for Part A Materials . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 17 Calculation Details . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 19 Reporting of Part A Emissions . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 19
- Emissions Calculations for Part B . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 19 Recommendations for Implementation of Part A . . . . . . . . . . . . . . 20 Reporting Total Emissions from Impact Accounting . . . . . . . . . . . . 21 Conclusion . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 22 Next Steps. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 23 Endnotes . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 24


### Rationale

Corporate emissions quantification and reporting divides greenhouse gas (GHG) emissions into three distinct scopes (see Exhibit 1). Scope 1 includes direct emissions from company facilities, vehicles, and other directly controlled sources. Scope 2 includes indirect emissions from electricity, steam, heating, and cooling purchased from other entities for company use. Finally, Scope 3 emissions can include upstream activities like purchased goods and services, capital goods, distribution, and employee commuting, as well as downstream activities such as the use of sold products and end-of-life treatment of products.

###### Exhibit 1 Overview of Scope 1, 2, and 3 emissions

Carbon dioxide Nitrous oxide Perfluorocarbons Hydrofluorocarbons Methane Sulfur hexafluoride





Scope 2 indirect

Scope 3 indirect

Scope 1 direct

Scope 3 indirect

Business travel

Purchased electricity, steam, heating, and cooling for own use

Fuel- and energyrelated activities

Company facilities



Leased assets




Employee commuting

Leased assets




Use of sold products





Investments




Purchased goods and services
























Waste generated in operations

Company vehicles

End-of-life treatment of sold products

Processing Franchises of sold products

Transportation and distribution

Capital goods




Transportation and distribution

Upstream activities Reporting company Downstream activities

RMI Graphic. Source: GTG Protocol, https://ghgprotocol.org/scope-3-calculation-guidance-2

Early corporate adopters of Scope 3 reporting such as Microsoft have discovered that these emissions can be significantly larger than their combined Scope 1 and 2 emissions. This is in part because the embodied carbon emissions from building materials and construction activities are substantial.

The GHG Protocol provides four methods to calculate Scope 3 emissions from capital goods (see Exhibit 2):

- 1. Supplier-specific or process-based method
- 2. Hybrid method
- 3. Average-data method
- 4. Spend-based method


###### Exhibit 2 GHG Protocol decision flowchart for selecting a calculation method for Scope 3 capital goods

Based on the screening, does the purchased good or service contribute significantly to Scope 3 emissions or is supplier engagement otherwise relevant to the business goals?

YES NO

Is data available on the physical quantity of the purchased good or service?

Is data available on the physical quantity of the purchased good or service?

|NO|YES NO|
|---|---|
|NO| |


YES

NO

Can the Tier 1 supplier provide product-level cradle-to-gate GHG data (of sufficient quality to meet the business goals) for the purchased good or service?

Can the supplier provide allocated Scope 1 and 2 data (of sufficient quality to meet the business goals) relating to the purchased good or service?

YES

NO

YES

Can the supplier provide allocated Scope 1 and 2 data (of sufficient quality to meet the business goals) relating to the purchased good or service?

YES

Use the

supplier-specific method

Use the

hybrid method

Use the

average-data method

Use the

spend-based method

More precise Less precise

RMI Graphic. Source: GHG Protocol, https://ghgprotocol.org/scope-3-calculation-guidance-2

###### Spend-based accounting perversely results in companies reporting higher emissions rather than lower when they willingly make investments to reduce embodied carbon from their building projects.

Companies that have historically used the spend-based method (see Exhibit 3) are finding significant limitations when using it to assess emissions associated with building projects because even the most granular dollar-to-emissions factors available do not differentiate between competing building products with higher or lower embodied carbon emissions. Reliance on spend-based accounting therefore results in a critical barrier to decarbonization: the only way for a company to reduce its emissions is to spend less on construction even though efforts to reduce embodied carbon through design and procurement choices may come with higher costs. Spend-based accounting perversely results in companies reporting higher emissions rather than lower when they willingly make investments to reduce embodied carbon from their building projects.

###### Exhibit 3 Overview of spend-based accounting

Total spend with capital goods suppliers

Emissions per dollar factor (from economic input-output database)

Total project emissions

RMI Graphic

Microsoft has been engaged in significant efforts to understand and reduce its construction-related Scope 3 emissions. It undertook an effort with RMI, Building Transparency, and the University of Washington to explore how to move beyond spend-based accounting and find an acceptable and impactful accounting methodology to reflect its strategic investments in embodied carbon reductions in construction projects that can be practically implemented today.

The team began its efforts by examining the three more precise, non-spend-based options provided by the GHG Protocol for measuring Scope 3 emissions.

The average-data method was not pursued because, as with spend-based accounting, this method is less precise and does not provide the product-specific insights valued by Microsoft for construction project decision-making to support embodied carbon reductions.

Thesupplier-specific or process-based method (see Exhibit 4, next page) identified as “more precise” in the GHG Protocol is becoming a standard approach in the construction industry.i Process-based life-cycle assessment (LCA) data is specific to individual products or product types. It involves detailed information on

- i Process-based methods are included in codes such as CALGreen, federal and state Buy Clean procurement programs, and green building programs such as Leadership in Energy and Environmental Design (LEED).


material and energy flows, emissions, and waste for each stage of a product’s life cycle, typically guided by industry standards. An example of process-based LCA data is environmental product declarations (EPDs) for specific building products, which provide detailed environmental impact information for that product, including global warming potential (GWP). The process-based method was seen by the research team as being the most desirable to measure embodied carbon for construction projects because many of the high-emissions products commonly used in construction projects are well represented by process-based data such as EPDs.

###### Exhibit 4 Overview of process-based method

Material quantities for all project materials

A1–A3 EPD emissions factor for each material

A4 & A5 emissions for each material

###### Total project emissions

(optional)

Note: A1–A3 are product stage emissions; A4 is emissions from the transportation of products to the construction site; and A5 is construction-related emissions.

RMI Graphic

However, a lack of product-level data for many important construction divisions such as mechanical, electrical, and plumbing products makes it impossible today to use process-based accounting for all the products used in a construction project. Companies completing numerous and complex building projects also face issues of practicality when attempting to track every single building product via process-based data sources. There are diminishing returns when reporting on numerous individual products that contribute minimally to the overall embodied carbon of projects and for which products with significantly improved embodied carbon may not exist.

These significant issues with process-based methods point to the use of some form of hybrid accounting method to enable a combination of spend-based and process-based data to assess construction projects. The GHG Protocol recognizes hybrid methods as acceptable for Scope 3 accounting. There are four main hybrid life-cycle inventory methods found in the literature.1 A brief overview of each was prepared by the University of Washington for this project:

- 1. Tiered Hybrid Method: The tiered hybrid method combines process-based and input-output (I-O) data within a process analysis framework. It uses process data for specific, well-defined foreground processes and I-O data for background processes or where process data is unavailable. This method aims to reduce truncation errors associated with pure process analysis while maintaining specificity for key processes. The main challenges include defining clear boundaries between process and I-O data to avoid double counting and the potential for some level of truncation to remain due to system boundary definition.
- 2. Path Exchange (PXC) Method: The PXC method involves mathematically disaggregating an I-O matrix into mutually exclusive pathways representing the entire economy. Specific pathways can then be modified using process data to tailor the analysis to a unique product or service. This method maintains system completeness while allowing for increased specificity in key areas of the supply chain. The main advantage is the ability to modify specific parts of the supply chain without affecting


- the overall I-O structure. However, it can be complex and time-consuming to implement due to the large amount of data involved.
- 3. Matrix Augmentation Method: The matrix augmentation method involves directly modifying the I-O matrix to create additional sectors. This can be done either by disaggregating an existing sector into subsectors or by creating a new theoretical sector. The method aims to address aggregation errors in conventional I-O analysis by allowing for a more specific representation of products or processes. It is particularly useful for assessing new or emerging technologies. The main limitation is that modifications to the matrix can potentially reverberate across every tier of the supply chain.
- 4. Integrated Hybrid Method: The integrated hybrid method combines process and I-O data within a single matrix framework. It uses upstream and downstream cutoff matrices to link process data (represented as a technology matrix) with the I-O table. This method aims to solve the entire system via matrix computations, potentially providing a more comprehensive and consistent approach. The main challenges include the complexity of implementation and the potential for double counting due to the introduction of process data that no longer sums with the rest of the I-O table to a complete description of the economy.2



Of these hybrids, the University of Washington team indicated that the PXC method provides the desired increase in specificity found in process-based data such as EPDs while maintaining the completeness of I-O analysis.ii The Environmental Performance in Construction (EPiC) Database is an open-access repository for the Australian market providing these embodied environmental flow coefficients for construction materials.3 It utilizes the PXC hybrid life-cycle inventory method to create these coefficients.

Although this option was explored by the research team, it was determined that the creation, ownership, and maintenance of robust PXC databases for every country in which a company such as Microsoft operates would be too time- and budget-intensive. Also, it does not seem an appropriate task for a single corporate

- ii The process of creating a PXC database involves several steps: First, relevant I-O sectors and process data are identified for each material. A structural path analysis is then performed on both the I-O sector and process data to break down their supply chains into mutually exclusive nodes. Equivalent nodes between the I-O and process data are identified to avoid double counting. Total environmental flows for the relevant I-O sector are obtained from government sources and allocated using a concordance matrix. The hybrid coefficient is then calculated by summing the environmental flows from selected process nodes (the process component), subtracting the equivalent I-O flows from the total sector flows, and converting the remainder to the appropriate functional unit (the I-O component). These components combined form the hybrid coefficient.


entity to undertake and maintain in order to assess the positive impacts it can achieve through design and procurement decisions on high-emitting products for building projects.

None of the existing hybrids satisfy the key objective of the impact accounting method: enabling companies like Microsoft to measure and report embodied carbon from high-emitting products in their construction projects regardless of financial costs using data sources identified in the GHG Protocol as “more precise” in a way that can be implemented immediately. Rather than creating a hybrid that attempts to accurately combine aspects of all four methods identified in the GHG Protocol, impact accounting identifies two data pathways in the protocol’s decision tree that can currently cover all construction activities and consistently splits all construction-related procurement across them (see Exhibit 5).

###### Exhibit 5 Impact accounting splits analysis between two existing pathways in the protocol

Based on the screening, does the purchased good or service contribute significantly to Scope 3 emissions or is supplier engagement otherwise relevant to the business goals?

###### YES

NO

Is data available on the physical quantity of the purchased good or service?

Is data available on the physical quantity of the purchased good or service?

|NO|YES NO|
|---|---|
|NO| |


YES

NO

Can the Tier 1 supplier provide product-level cradle-to-gate GHG data (of sufficient quality to meet the business goals) for the purchased good or service?

Can the supplier provide allocated Scope 1 and 2 data (of sufficient quality to meet the business goals) relating to the purchased good or service?

YES

NO YES

Can the supplier provide allocated Scope 1 and 2 data (of sufficient quality to meet the business goals) relating to the purchased good or service?

YES

Use the

supplier-specific method

Use the

hybrid method

Use the

average-data method

Use the

spend-based method

More precise Less precise

RMI Graphic. Source: GTG Protocol, https://ghgprotocol.org/scope-3-calculation-guidance-2

The benefit of this approach is that it enables the use of existing datasets — available EPDs for high-impact and high-volume product categories and existing spend-based factors for all other categories — to capture the embodied carbon reductions from investing in low-carbon products while still representing emissions from the full range of construction products and activities via spend-based data. This two-path analysis can be enacted immediately rather than waiting for new hybrid datasets to be funded and created.

Impact accounting combines process-based and EIO datasets in the evaluation of construction projects. Both are acceptable in the GHG Protocol but each represents different scope boundaries. EIO attempts to broadly capture all emissions that arise in an economy from a particular activity, whereas process-based accounting focuses more narrowly on the direct emissions arising from the creation of a product. This unique feature of impact accounting requires users to be aware of some key considerations:

- 1. Scope 3 emissions for projects calculated using the impact method would not be directly comparable with any existing baselines or benchmarks established using only spend-based (or other hybrid) accounting. New benchmarks would need to be established using the impact method and no impact method results could be compared with previous reports.
- 2. Scope 3 emissions for specific products are likewise not comparable unless the same pathway (process- or spend-based) has been used to generate results. Construction products assessed using EPD data based on the reported GWP factor for the product cannot be compared to emissions for equivalent products assessed using spend-based data.


The GHG Protocol supports the use of a supplier-specific or process-based method for calculating Scope 3 emissions despite the narrower boundaries inherent in this type of cradle-to-gate analysis when compared with EIO approaches. Because this narrower boundary would be acceptable if applied to all construction products, applying this approach to predefined product categories and using more broadly focused EIO data for the remainder aligns with the GHG Protocol for calculating Scope 3 emissions.

Substantial embodied carbon reductions are possible when EPD data is used to make decisions from building design development through product procurement, especially for high-impact, high-volume products (concrete, steel, glass, insulation, wallboard, flooring). The strength of the impact method is the ability to implement it immediately because it makes use of available process-based data, and to therefore illuminate and quantify substantial embodied carbon reductions available today.

In the coming decade, it is likely that process-based datasets and supporting standards will grow to the point that they can be used to fully calculate construction-related emissions for large and complex building portfolios. It is also possible that robust hybrid datasets will become available that can provide productlevel specificity in blended data that provides consistent quantification across a whole construction project and across successive years. The impact method is intended to provide a consistent framework for using today’s best available process-based data to ensure that emissions reductions are identified and can be prioritized for measurable action, while ensuring emissions are captured for product categories where spend-based data is currently the best available option.

### General Guidance from the GHG Protocol for the Impact Accounting Method

The impact accounting method aligns with the GHG Protocol and represents a combination of two of its accounting standards in a streamlined manner. The GHG Protocol directs companies to select calculation methods for each Scope 3 activity within a category based on the following criteria:

- • The relative size of the emissions from the Scope 3 activity
- • The company’s business goals
- • Data availability
- • Data quality
- • The cost and effort required to apply each method
- • Other criteria identified by the company


The decision to focus this methodology on the material categories with the highest contributions to overall construction-related emissions and the best available data is in alignment with this approach.

This method provides specific guidance for four of the nine overall steps outlined in the GHG Protocol (see Exhibit 6); how the impact method aligns with each of these four steps is outlined in detail below.

Exhibit 6 The steps in Scope 3 accounting and reporting from the GHG Protocol that

are covered by the impact method

###### Define

###### Review

###### Identify

###### Set

###### Collect

###### Allocate

###### Target

###### Assure

###### Report

business goals

accounting + reporting principles

Scope 3 activities

Scope 3 boundary

data

emissions

(optional) + track emissions over time

emissions (optional)

emissions

Impact method begins

Impact method covers these steps

RMI Graphic. Source: GHG Protocol, https://ghgprotocol.org/scope-3-calculation-guidance-2

Identify Scope 3 activities: The impact accounting method specifically addresses the upstream emissions arising from construction materials for new buildings and tenant improvement projects. This is defined in the GHG Protocol as upstream Scope 3 emissions in Category 2, capital goods (see Exhibit 7, next page).

Impact Accounting Methodology for Building Construction rmi.org / 12

###### Exhibit 7 Category description and minimum boundary for upstream

###### Scope 3 emissions for capital goods

The extraction, production, and transportation of capital goods purchased or acquired by the reporting company in the reporting year

###### Upstream Scope 3: Capital Goods

Description

All upstream (cradle-to-gate) emissions of purchased capital goods

Minimum boundary

RMI Graphic. Source: GHG Protocol, https://ghgprotocol.org/scope-3-calculation-guidance-2

Set the Scope 3 boundary: For process-based calculations, this method applies the minimum boundary specified in the GHG Protocol, defined as “all upstream (cradle-to-gate, A1–A3) emissions of purchased capital goods,”4 and can be voluntarily expanded to include A4 (transportation to site) and A5 (construction/ installation) emissions. The intent is to capture material-specific emissions from the material categories with the highest contributions to overall construction-related emissions and the best available data. Exhibit 11 (see page 18) provides a specific list of construction material categories to be included in reporting.


Collect data: The calculations outlined in Calculation Method for Impact Accounting require a spend budget

for the project that will be divided into two parts: Part A is the hard cost and quantity of materials to be included in the process-based calculations and Part B is all other project costs. Division of Project Costs and Materials outlines a detailed breakdown of these two parts. Exhibit 11 provides a list of materials

appropriate for inclusion in the process-based calculations. For all materials in Part A, appropriate EPD data will need to be collected or a software tool that includes EPD data can be used. See Emissions Calculations for Part A Materials for tool requirements.

Allocate emissions: Following completion of the calculations outlined in Calculation Method for Impact Accounting, the total quantity of emissions for a particular new construction or tenant improvement project can be included in a company’s overall Scope 3 emissions report. We suggest reporting both the total emissions and the distinct totals for both Part A and Part B.

###### Boundary Definitions

Category boundaries: This method is intended to be used to calculate Scope 3 emissions from construction materials for new buildings, renovations, or tenant improvements. This is defined in the GHG Protocol as upstream Scope 3 emissions in Category 2 (capital goods). This methodology adheres to the minimum boundary of cradle-to-gate emissions.

Organizational/operational boundaries: The operational boundary includes embodied carbon construction from both owned and leased assets, including:

- • Owned assets:Scope 3, Category 2 (capital goods) emissions including:

› Construction materials, activities, materials transportation, and construction/deconstruction waste › Mechanical, electrical, and plumbing equipment › Critical infrastructure equipment (e.g., air handling units, generators)

- • Leased assets:Construction or renovation elements and activities purchased by the company

The boundary of the proposed methodology excludes the following aspects:

- • Owned assets:All hardware and information technology equipment managed by a separate business

group or entity

- • Leased assets:


› Any construction or renovation elements and activities purchased by the lessor › Pre-existing and/or externally controlled building material components

Geographic boundaries: This methodology is intended to be applied to construction projects anywhere in the world. Data availability will vary regionally due to EPD data availability. Any regional variations in data quality and/or material inclusions should be included in project reports.

Temporal boundaries: Reporting of Scope 3 emissions is annual, whereas building construction may take place over many years. The impact accounting methodology will be reported on an annual basis for both the spend- and process-based approaches. For the spend-based portion of the methodology, emissions will tie to the amount spent in that year. For the process-based portion of the methodology, emissions will be attributed to the appropriate fiscal year consistent with the procurement of material and the associated invoice.

### Calculation Method for Impact Accounting

The impact method divides construction project products and costs into two parts (see Exhibit 8).

###### Exhibit 8 Overview of impact accounting method

- Part A: High-impact materials with EPDs
- Part B: Costs for all aspects of project not covered in Part A


A1–A3 EPD emissions factor for each material

Material quantities for Part A materials

Total process-based emissions

#### +

(Optional) A4 & A5 emissions for each material

Total spend-based emissions

Total Part B cost

Emissions per dollar factor

Total project emissions

Note: A1–A3 are product stage emissions; A4 is emissions from the transportation of products to the construction site; and A5 is construction-related emissions.

RMI Graphic

- Part A: Products for which EPD data will be used to calculate emissions. Part A includes two pathways:


- 1. Preferred Pathway: For products with GWP factors derived from product-specific Type III EPDs. EPDs used for Part A, Preferred Pathway must meet these criteria:


- • Cover a single product from a manufacturer
- • Sate a referenced product category rule (PCR)
- • Have had a PCR review by a third-party entity
- • Conform to ISO 14025, EN 15804, or ISO 21930
- • Be verified by a third party (usually the program operator)
- • Industry-wide Type III EPDs cannot be used for this pathway


Impact Accounting Methodology for Building Construction rmi.org / 15

- 2. Acceptable Pathway: For products without product-specific Type III EPDs but for which benchmark GWP factors can be used that represent the 80th percentile of GWP factors from EPDs of comparable product types from an approved database. Industry-wide Type III EPDs can be used for this pathway if the product's manufacturer is a participant in the industry-wide EPD.


The Preferred Pathway must be used whenever appropriate EPDs exist for the specified product.

- Part B: Products without product-specific or benchmark EPD factors, for which spend-based data will be used to calculate emissions using emissions-per-dollar-spent factors, which are conversions from a dollar value to a GHG emissions equivalent value that are calculated per a company’s inventory management plan.



###### Division of Project Costs and Materials

To apply the impact method, project costs must be divided appropriately between Parts A and B (see

- Exhibit 9, next page):


- • Part A(process-based) requires the material and associated labor costs for all materials included in

Exhibit 11, which will be subject to a process-based calculation. Do not include insurance or other costs that are additional to materials and installation labor.

- • Part B(spend-based) includes all project costs that do not fall into Part A. Once the total cost of Part A


has been determined, this can be subtracted from the total project cost. Part B costs are to be summed using a company’s current method for calculating costs for spend-based accounting.

###### Exhibit 9 Division of project costs and materials

Total cost to track with spend-based method

Total project cost

Cost of materials for all Part A materials

RMI Graphic

Emissions Calculations for Part A Materials

###### Exhibit 11 (see next page) provides a list of the high-impact material categories for which sufficient EPD data exists to perform Part A calculations, determined by a review of current EPD databases. All materials in Exhibit 11 that are used on a construction project must be included in Part A calculations. Multiple entries under each material type may be required to account for different suppliers and/or material specifications. For example, different types of concrete are likely to be used in a project and each specific mix will require unique calculations.

The specific quantity of each material in Exhibit 11 is multiplied by the A1–A3 (and optional A4 and A5) emissions factor from an appropriate EPD to calculate the total emissions per material type. The results for each unique material type are summed to provide the total emissions for all Part A materials (see Exhibit 10).

###### Exhibit 10 Calculation example for Part A materials

A1–A3 emissions factor from EPD

Total emissions for

- Product 1 quantity
- Product 2 quantity


+

- Product 1

Total emissions for

- Product 2


(Optional) A4 & A5 emissions

A1–A3 emissions factor from EPD

+

(Optional) A4 & A5 emissions

(Repeat for all Part A products)

Total emissions for each product in Exhibit 11

Total emissions for Part A

RMI Graphic

###### Exhibit 11 Sample of information required for Part A material emissions calculations

|Material type|Qty|Unit|A1–A5 emissions factor kg CO2e/ unit|EPD number or URL|EPD type|Data specificity|Total emissions kg CO2e (Qty x emissions factor)|Notes|
|---|---|---|---|---|---|---|---|---|
|STRUCTURE| | | | | | | | |
|Concrete (includes ready-mix, precast)| |m3| | |☐ Industry average|N/A<br><br>| | |
| | | | | |☐ Product specific|☐ Industry average ☐ Industry average| | |
|Steel reinforcing for concrete (rebar)| |kg| | |☐ Industry average|N/A<br><br>| | |
| | | | | |☐ Product specific|☐ Industry average ☐ Industry average| | |
|Structural steel| |kg| | |☐ Industry average<br><br>|N/A| | |
| | | | | |☐ Product specific|☐ Industry average ☐ Industry average| | |
|Mass timber| |m3| | |☐ Industry average<br><br>|N/A| | |
| | | | | |☐ Product specific|☐ Industry average ☐ Industry average| | |
|Concrete masonry units| |m3| | |☐ Industry average<br><br>|N/A| | |
| | | | | |☐ Product specific|☐ Industry average ☐ Industry average| | |
|ENCLOSURE| | | | | | | | |
|Glazing| |m2| | |☐ Industry average<br><br>|N/A| | |
| | | | | |☐ Product specific|☐ Industry average ☐ Industry average| | |
|Structural aluminum framing| |kg| | |☐ Industry average<br><br>|N/A| | |
| | | | | |☐ Product specific|☐ Industry average ☐ Industry average| | |
|Cold-formed metal framing| |kg| | |☐ Industry average|N/A<br><br>| | |
| | | | | |☐ Product specific|☐ Industry average ☐ Industry average| | |
|Thermal insulation| |m2x RSI| | |☐ Industry average<br><br>|N/A| | |
| | | | | |☐ Product specific|☐ Industry average ☐ Industry average| | |
|INTERIOR| | | | | | | | |
|Sheathing/ cladding| |m2| | |☐ Industry average|N/A<br><br>| | |
| | | | | |☐ Product specific|☐ Industry average ☐ Industry average| | |
|Gypsum wallboard| |m2| | |☐ Industry average<br><br>|N/A| | |
| | | | | |☐ Product specific|☐ Industry average ☐ Industry average| | |
|Paint| |m2| | |☐ Industry average|N/A<br><br>| | |
| | | | | |☐ Product specific|☐ Industry average ☐ Industry average| | |
|Carpet| |m2| | |☐ Industry average|N/A<br><br>| | |
| | | | | |☐ Product specific|☐ Industry average ☐ Industry average| | |
|Resilient flooring| |m2| | |☐ Industry average<br><br>|N/A| | |
| | | | | |☐ Product specific|☐ Industry average ☐ Industry average| | |
|Acoustic ceiling tiles| |m2| | |☐ Industry average<br><br>|N/A| | |
| | | | | |☐ Product specific|☐ Industry average ☐ Industry average| | |
|TOTAL PART A EMISSIONS| | | | | | | | |
|TOTAL PART A EMISSIONS INTENSITY| | | | | | | | |


RMI Graphic

###### Calculation Details

Calculations must be performed using embodied carbon data of at least the following minimum standards:

- • Data must be from Type III, third-party-verified product-specific EPDs and industry average EPDs.
- • Material quantities shown in Exhibit 11 must be expressed in the declared unit of the relevant EPD.
- • Uncertainty values must be applied to reported EPD GWP carbon intensities, following a published


methodology, to account for lack of data specificity, granularity, and/or transparency.

Software tools that assist in the generation of Part A results must use data that meets the above minimum standards and additionally:

- • Enable aggregation of EPDs by material categories included in Part A to enable an 80th percentile calculation to be completed in lieu of a product-specific EPD when one is not available for the product procured or in the region where the product is procured.
- • Include a project-level accounting function to enable material quantities to be multiplied by kilograms of


CO2 equivalent (kg CO2e) intensity values from approved data sources for the products included in Part A.

Software tools that meet these requirements may be used to perform Part A calculations and present results in place of Exhibit 11 if all the information required in the exhibit is provided in the report.

###### Reporting of Part A Emissions

All sections of Exhibit 11 should be included in a Part A report. Results from Part A calculations should be reported as both total net embodied carbon for the project and as embodied carbon intensity, expressed in either kg CO2e per square foot (ft2) or kg CO2e per square meter (m2) of building floor area. This will enable consistent reporting across building types and sizes and allow companies to track trends in project- and portfolio-level embodied carbon over time.

###### Emissions Calculations for Part B

All materials and project costs not associated with Part A are totaled and used to perform a spend-based calculation according to a company’s current method for spend-based accounting.

The total cost for Part B of a construction project is multiplied by an emissions-per-dollar-spent factor from an EIO LCA database (such as the US Environmentally-Extended Input-Output model or UK Department for Environment, Food and Rural Affairs [DEFRA] model) to create an estimate of total emissions for Part B.

### Recommendations for Implementation of Part A

Material categories included in Part A should be shared early with the designer(s) and contractor(s) to ensure they are aware of the need to accurately track quantities and material costs.

Perform Part A calculations early to track reductions: Calculating Part A emissions according to this method will provide companies with valuable results for Scope 3 emissions. However, to understand and maximize emissions reductions, the calculations should be performed throughout project design and execution and the impact of decisions to use less emissions-intensive products can be reported by comparing Part A emissions from the following project stages:

- • Schematic design:Decisions about building massing and major material selections can provide

insights into strategies to reduce Part A emissions.

- • Design development:Decisions about assemblies and material selections will affect Part A emissions.
- • Construction documents:Procurement decisions will affect Part A emissions.

Inform contractors of data requirements: Successful implementation of this method requires integrating new expectations into contracts and billing practices to ensure appropriate collection of data from the contractor. The contractor will be required to track the following pieces of data:

- • Material quantities for materials listed in Exhibit 11
- • Material cost (without labor and insurance costs) for those quantities, as separate from the remainder

of the project cost

- • Products used for each material type, and documentation of data type used for carbon values (industry


average EPD, product-specific EPD, etc.)

This data is typically tracked or collected by contractors, but they may not be supplying this information to the owner depending on their billing structure. Alerting the contractor to this at the beginning of the project (and integrating it into owner project requirements) will avoid additional work by the contractor to meet expectations on reporting templates.

Guidance on documentation requirements for Part A material quantities can be found in the ownersCAN Embodied Carbon Action Plan.5

### Reporting Total Emissions from Impact Accounting

Emissions reporting using the impact method should include the following (see Exhibit 12):

- • Total project emissions:The total emissions for Parts A and B, expressed as both a total kg CO2e and

as an emissions intensity expressed as kg CO2e/ft2 or kg CO2e/m2 of building floor area

- • Emissions for Part A:

- ○ Total emissions for Part A, expressed as both a total kg CO2e and as an emissions intensity expressed as kg CO2e/ft2 or kg CO2e/m2 of building floor area
- ○ Emissions per material category from Exhibit 11
- ○ Emissions reductions per material category from Exhibit 11 may be shown to demonstrate reductions achieved over the design and construction of the project by material selection and procurement


- • Emissions for Part B:


○ Total emissions for Part B, expressed as both a total kg CO2e and as an emissions intensity expressed as kg CO2e/ft2 or kg CO2e/m2 of building floor area

###### Exhibit 12 Reporting requirements for impact method accounting

- Total Part A

process-based emissions kg CO2e and kg CO2e/area

- Total Part B


Report for Part A process-based emissions kg CO2e and kg CO2e/area

- Sum of total Part A process-based emissions per material/category kg CO2e
- Sum of total Part B spend-based emissions


Report for Part B spend-based emissions kg CO2e and kg CO2e/area

spend-based emissions kg CO2e and kg CO2e/area

per material/category kg CO2e

Report for total project emissions kg CO2e and kg CO2e/area

RMI Graphic

### Conclusion

The intent of calculating and reporting Scope 3 emissions is “to accelerate efforts to reduce anthropogenic GHG emissions.”6 The use of spend-based factors can deter companies from investing in low-carbon building solutions by artificially raising reported emissions when additional money is spent to achieve lower embodied carbon in buildings. Although impact accounting for embodied carbon is an admittedly imperfect model for reporting Scope 3 emissions from construction projects, it enables a set of highimpact materials to be calculated more precisely using a process-based approach. In addition, it can reveal important insights for emissions reductions that can shape project designs and material procurement while leaving all other materials to continue to be calculated by the more widely used spend-based approach.

The construction sector has begun to embrace process-based estimations for material-related emissions due to the clarity they can bring to design and procurement decisions that can significantly reduce emissions. In case studies from Microsoft and the University of Washington that were examined during the research phase for the impact method, it was found that the use of process-based data could reduce emissions from a project by 17% to 23%.

The process-based method used for Part A of the impact accounting method is a more actionable means of calculating embodied carbon, but process-based data is not available for all the materials included in a typical construction project. Impact accounting is premised on the understanding that the available dataset for process-based calculations is now robust enough to capture a significant portion of the emissions of a construction project and that significant emissions reductions are available in these material categories when this data is used to guide design and procurement decisions.

The division between what materials are included in Part A (product-specific emissions accounting) versus Part B (spend-based emissions accounting) will continue to shift toward ever-greater portions of construction projects being able to be captured by Part A calculations as data collection efforts expand in light of increasing momentum and interest in reducing supply chain emissions across industries. It is anticipated that Exhibit 11 will be updated and expanded over time.

In the spirit of the GHG Protocol, the proposed impact accounting method is intended to bring additional clarity to the industry and motivate major emissions reductions in the high-impact construction sector. It will not accurately reveal the precise carbon footprint of a construction project, but it will make obvious the areas in which real and significant emissions reductions can be achieved today and enable users to achieve significant and important embodied carbon reductions in their construction projects.

### Next Steps


This report proposes an impact accounting method for calculating and reporting Scope 3 emissions from construction projects. With consistent categorization of purchases into Part A and Part B and adherence to the calculation and reporting requirements, this method can be put to use immediately.

The authors have identified the following areas for further research, review, and discussion:

- • Review and discussion with other companies reporting and reducing their Scope 3 construction emissions
- • Additional analysis on opportunities to address the lack of comparability between Part A and Part B

emissions until more products can be included in Part A emissions

- • Existing case research that informed Exhibit 11 (i.e., provide more background research and case studies on

why this is the list of the highest-impact materials with the highest EPD availability)

- • Research and interviews to understand some of the context on the spend-based accounting that is not


covered in this report, such as:

› Significant discrepancies in the order of magnitude between spend-based and process-based emissions. › Spend does not track material quantities separately (such as gypsum wall board and metal framing). › Interviews with other companies to establish which emissions factors are used for those doing spend-based accounting will provide important context to understanding the magnitude of reduction that could be attributed to impact accounting versus the reductions seen just through changing emissions factors.

### Endnotes

- 1 R. Crawford et al., “Hybrid Life Cycle Inventory Methods — A Review,” Journal of Cleaner Production 172 (January 2018): 1273–1288, https://doi.org/10.1016/J.JCLEPRO.2017.10.176.
- 2 Crawford, “Hybrid Life Cycle Inventory Methods — A Review,” 2018.
- 3 EPiC Database and Resource Hub, Melbourne School of Design, https://epicdatabase.com.au/.
- 4 Technical Guidance for Calculating Scope 3 Emissions, GHG Protocol, 2013, https://ghgprotocol.org/ scope-3-calculation-guidance-2.
- 5 Embodied Carbon Action Plan, ownersCAN, Building Transparency, 2021, https://www. buildingtransparency.org/programs/carbon-action-network/.
- 6 Greenhouse Gas Protocol: Corporate Value Chain (Scope 3) Accounting and Reporting Standard, World Resources Institute and World Business Council for Sustainable Development, 2011, https://ghgprotocol.org/sites/default/files/ghgp/standards/Corporate-Value-Chain-AccountingReporing-Standard_041613_2.pdf.


Victor Olgyay, Chris Magwood, and Katie Ross, Impact Accounting Methodology for Building Construction, RMI, 2025, https://rmi.org/insight/impact-accounting-methodology-for-building-construction.

RMI values collaboration and aims to accelerate the energy transition through sharing knowledge and insights. We therefore allow interested parties to reference, share, and cite our work through the Creative Commons CC BY-SA 4.0 license. https://creativecommons.org/licenses/by-sa/4.0/.

All images used are from iStock.com unless otherwise noted.

###### RMI Innovation Center

22830 Two Rivers Road Basalt, CO 81621

###### www.rmi.org

© February 2025 RMI. All rights reserved. Rocky Mountain Institute® and RMI® are registered trademarks.

