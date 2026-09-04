export interface ChartSpecification {
  chart_id: string;
  title: string;
  subtitle: string;
  economic_question: string;
  chart_type: 'line' | 'bar' | 'area' | 'scatter' | 'heatmap' | 'waterfall' | 'sankey' | 'network' | 'fan' | 'radar' | 'timeline' | 'map' | 'tornado' | 'diagram';
  x_variable: string | null;
  y_variable: string | null;
  secondary_y_variable: string | null;
  unit: string;
  frequency: string;
  start_date: string | null;
  end_date: string | null;
  source: string[];
  transformation: string[];
  annotations: string[];
  confidence: 'UNAVAILABLE' | 'LOW' | 'MODERATE' | 'HIGH';
  interpretation: string;
  policy_implication: string;
}

export const CHART_TITLES = [
  'Real GDP','Nominal GDP','GDP per capita','Annual GDP growth','GDP indexed to 1998=100','Oil vs non-oil GDP','Sector composition','Investment/GDP','Consumption/GDP','Government expenditure/GDP',
  'CPI level','CPI YoY','CPI MoM','Cumulative inflation','Food inflation','Housing inflation','Transport inflation','Venezuela vs U.S. inflation','Inflation vs money growth','Inflation vs FX depreciation',
  'Monetary base','Currency circulation','Bank reserves','M1','M2','M2/GDP','Money velocity','Money growth vs inflation','Monetary financing','Monetary aggregates in USD-equivalent terms',
  'Official VES/USD','Parallel VES/USD','Official-parallel spread','Monthly depreciation','REER','NEER','FX volatility','FX turnover','Implied conversion rate by monetary aggregate','Proposed dollarization conversion-rate range',
  'Gross international reserves','Liquid reserves','Gold reserves','Reserves excluding gold','Reserves/months imports','Reserves/M0','Reserves/M1','Reserves/M2','Reserve adequacy','Dollarization funding gap',
  'Banking assets','Total deposits','VES deposits','USD deposits','Loans','Credit/GDP','Loan/deposit ratio','Bank capitalization','NPL ratio','Liquidity ratio','Bank profitability','Deposit concentration','Government exposure','FX mismatch','Banking recapitalization requirement',
  'Credit under base scenario','10% credit contraction','20% credit contraction','30% credit contraction','50% credit contraction','Credit vs GDP','Credit vs employment','Deposit withdrawal stress','Emergency liquidity requirement','Lender-of-last-resort gap',
  'Government revenue','Oil revenue','Non-oil revenue','Total spending','Wage bill','Pensions','Subsidies','Interest expenditure','Fiscal balance','Primary balance','Deficit/GDP','Monetary financing','Seigniorage','Tax revenue/GDP','Fiscal adjustment requirement',
  'Oil production 1970-present','Oil exports','Domestic consumption','Oil price','Production x price matrix','Gross oil revenue','Estimated net oil FX','Oil revenue/GDP','Oil revenue/fiscal revenue','PDVSA investment','Rig count','Refinery capacity utilization','Export destinations','Production scenarios','Oil break-even dollarization heat map',
  'Exports','Imports','Trade balance','Current account','Remittances','FDI','Capital flows','Capital flight','External financing need','Net USD inflows','USD inflow waterfall','Imports vs FX receipts','Current-account stress',
  'Sovereign debt','PDVSA debt','Total public external claims','Debt/GDP','Debt/revenue','Debt service','Maturity wall','Creditor composition','Restructuring haircut scenarios','Debt sustainability paths',
  'Minimum wage','Median wage','Public salary','Pension','Food basket','Household purchasing power','Poverty','Extreme poverty','Employment','Unemployment','Informality','Remittances by household','USD-income share','Income-decile impact','Dollarization winners/losers',
  'SME credit','Commercial lending','Borrowing rates','Working-capital requirements','Business formation','Business closures','Construction activity','Industrial production','Retail sales','Imports dependence','Corporate FX exposure',
  'Ecuador inflation before/after','Ecuador GDP','Ecuador bank credit','Ecuador unemployment','Ecuador fiscal balance','Panama GDP','Panama banking credit','El Salvador growth','El Salvador debt','Cross-country inflation','Cross-country GDP','Cross-country credit/GDP','Cross-country debt/GDP','Dollarization outcomes matrix',
  'DSGE GDP impulse','DSGE inflation impulse','DSGE credit impulse','Oil shock','Fiscal shock','Bank-run shock','Capital-flight shock','Monte Carlo GDP distribution','Reserve distribution','Fiscal-deficit distribution','Banking-crisis risk distribution','Regime success distribution','Sensitivity tornado chart','Parameter sensitivity','Scenario fan chart','Dollarization Readiness Index','Monetary readiness','Banking readiness','Fiscal readiness','Reserve readiness','External readiness','Debt readiness','Institutional readiness','Social readiness','Regime scorecard','Policy trade-off frontier','Implementation timeline','Funding waterfall','Dependency diagram','Critical-path chart','GO / NO-GO dashboard','Sankey USD flows'
] as const;

export const CHART_SPECIFICATIONS: ChartSpecification[] = CHART_TITLES.map((title, index) => ({
  chart_id: `CHART-${String(index + 1).padStart(3, '0')}`,
  title,
  subtitle: `Venezuela economic review — ${title}`,
  economic_question: `What does ${title.toLowerCase()} show, and what evidence is required before interpreting it for dollarization?`,
  chart_type: title.toLowerCase().includes('heat map') ? 'heatmap' : title.toLowerCase().includes('waterfall') ? 'waterfall' : title.toLowerCase().includes('distribution') || title.toLowerCase().includes('fan') ? 'fan' : title.toLowerCase().includes('scorecard') || title.toLowerCase().includes('readiness') ? 'radar' : 'line',
  x_variable: null,
  y_variable: null,
  secondary_y_variable: null,
  unit: 'UNAVAILABLE UNTIL SOURCE-BOUND',
  frequency: 'UNAVAILABLE',
  start_date: null,
  end_date: null,
  source: [],
  transformation: [],
  annotations: ['redenominations', 'regime changes', 'hyperinflation', 'sanctions', 'COVID', 'oil shocks'],
  confidence: 'UNAVAILABLE',
  interpretation: 'No chart interpretation is issued until the underlying series, units, dates, transformations, and uncertainty are verified.',
  policy_implication: 'No policy implication is issued from an unpopulated chart specification.'
}));

export function validateChartSpecifications(specifications: ChartSpecification[]): string[] {
  const errors: string[] = [];
  if (specifications.length !== 200) errors.push(`expected 200 chart specifications, found ${specifications.length}`);
  const ids = new Set<string>();
  for (const chart of specifications) {
    if (ids.has(chart.chart_id)) errors.push(`duplicate chart_id: ${chart.chart_id}`);
    ids.add(chart.chart_id);
    for (const field of ['title', 'subtitle', 'economic_question', 'unit', 'frequency', 'interpretation', 'policy_implication'] as const) if (!chart[field].trim()) errors.push(`${chart.chart_id} missing ${field}`);
    if (!Array.isArray(chart.source) || !Array.isArray(chart.transformation) || !Array.isArray(chart.annotations)) errors.push(`${chart.chart_id} metadata arrays are invalid`);
  }
  return [...new Set(errors)];
}
