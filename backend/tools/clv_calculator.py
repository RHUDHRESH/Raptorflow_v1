from langchain.tools import BaseTool
import json

class CLVCalculatorTool(BaseTool):
    name = "clv_calculator"
    description = """
    Calculate Customer Lifetime Value by ICP segment.
    
    CLV = (Average Purchase Value  Purchase Frequency  Customer Lifespan)
    
    Also calculates:
    - CAC (Customer Acquisition Cost)
    - LTV:CAC ratio
    - Payback period
    
    Examples:
    clv_calculator(icp_data={...}, purchase_data={...})
    """
    
    def __init__(self):
        super().__init__()
    
    def _run(
        self,
        action: str = 'calculate',
        icp_id: Optional[str] = None,
        purchase_data: Optional[Dict] = None,
        acquisition_cost: Optional[float] = None,
        cohort_data: Optional[List[Dict]] = None
    ) -> str:
        
        if action == 'calculate':
            if not purchase_data:
                raise ValueError("calculate requires: purchase_data")
            
            # Extract values
            avg_purchase_value = purchase_data.get('average_purchase_value', 0)
            purchase_frequency = purchase_data.get('purchases_per_year', 0)
            customer_lifespan = purchase_data.get('average_lifespan_years', 0)
            gross_margin = purchase_data.get('gross_margin_percentage', 70) / 100
            discount_rate = purchase_data.get('discount_rate', 10) / 100
            
            # Basic CLV
            basic_clv = avg_purchase_value * purchase_frequency * customer_lifespan
            
            # Adjusted for gross margin
            profit_clv = basic_clv * gross_margin
            
            # Net Present Value (discounted for time value of money)
            npv_clv = 0
            for year in range(int(customer_lifespan)):
                yearly_value = avg_purchase_value * purchase_frequency * gross_margin
                discounted_value = yearly_value / ((1 + discount_rate) ** (year + 1))
                npv_clv += discounted_value
            
            # CAC and ratios
            cac = acquisition_cost or 0
            ltv_cac_ratio = npv_clv / cac if cac > 0 else 0
            
            # Payback period (months to recover CAC)
            monthly_profit = (avg_purchase_value * purchase_frequency * gross_margin) / 12
            payback_months = cac / monthly_profit if monthly_profit > 0 else 0
            
            # Categorize health
            if ltv_cac_ratio >= 3:
                health = "HEALTHY"
                health_note = "Strong economics, scale aggressively"
            elif ltv_cac_ratio >= 1:
                health = "VIABLE"
                health_note = "Positive but room to improve"
            else:
                health = "UNHEALTHY"
                health_note = "Losing money on each customer"
            
            return json.dumps({
                'icp_id': icp_id,
                'clv_metrics': {
                    'basic_clv': round(basic_clv, 2),
                    'profit_clv': round(profit_clv, 2),
                    'npv_clv': round(npv_clv, 2),
                    'cac': round(cac, 2),
                    'ltv_cac_ratio': round(ltv_cac_ratio, 2),
                    'payback_period_months': round(payback_months, 1)
                },
                'inputs': {
                    'avg_purchase_value': avg_purchase_value,
                    'purchase_frequency': purchase_frequency,
                    'customer_lifespan': customer_lifespan,
                    'gross_margin': gross_margin * 100,
                    'discount_rate': discount_rate * 100
                },
                'health': health,
                'health_note': health_note,
                'recommendations': self._get_recommendations(ltv_cac_ratio, payback_months)
            })
        
        elif action == 'compare_icps':
            if not cohort_data:
                raise ValueError("compare_icps requires: cohort_data")
            
            results = []
            for cohort in cohort_data:
                clv_result = json.loads(self._run(
                    action='calculate',
                    icp_id=cohort.get('icp_id'),
                    purchase_data=cohort.get('purchase_data'),
                    acquisition_cost=cohort.get('cac')
                ))
                results.append(clv_result)
            
            # Sort by NPV CLV
            results.sort(key=lambda x: x['clv_metrics']['npv_clv'], reverse=True)
            
            return json.dumps({
                'cohorts_analyzed': len(results),
                'results': results,
                'best_icp': results[0]['icp_id'],
                'worst_icp': results[-1]['icp_id'],
                'recommendations': "Focus acquisition on top-performing ICPs"
            })
        
        else:
            raise ValueError(f"Unknown action: {action}")
    
    def _get_recommendations(self, ltv_cac_ratio, payback_months):
        recs = []
        
        if ltv_cac_ratio < 1:
            recs.append("URGENT: You're losing money. Either increase LTV or decrease CAC.")
        elif ltv_cac_ratio < 3:
            recs.append("Improve LTV:CAC ratio to 3:1 for healthy growth")
        else:
            recs.append("Strong unit economics. Scale acquisition.")
        
        if payback_months > 12:
            recs.append("Payback period too long. Optimize for faster profitability.")
        elif payback_months < 6:
            recs.append("Fast payback. Consider investing more in CAC.")
        
        return recs
    
    async def _arun(self, *args, **kwargs):
        return self._run(*args, **kwargs)
