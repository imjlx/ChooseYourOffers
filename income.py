import numpy as np
import pandas as pd

StartThreshold = 5000

TaxLaw = {
    36000: (0.03, 0),
    144000: (0.1, 2520),
    300000: (0.2, 16920),
    420000: (0.25, 31920),
    660000: (0.3, 52920),
    960000: (0.35, 85920),
    999999999: (0.45, 181920)
}

RatePension = (0.08, 0.16)
RateMedical = (0.02, 0.06)
RateUnemployment = (0.005, 0.02)
RateBirth = (0, 0.008)
RateInjury = (0, 0.01)
RateProvient = (0.12, 0.12)


def cal_monthly_tax(month, cum_income, cum_insurance, early_cum_tax, cum_deductions=0):

    # 应纳税所得额 = 累计税前工资收入 - 累计减除费用(特指5000元的起征线) - 累计五险一金（个人缴纳部分） - 累计专项附加扣除。
    taxable_income = cum_income - month * StartThreshold - cum_insurance - cum_deductions
    
    cum_tax = None
    for level, (rate, deduction) in TaxLaw.items():
        if taxable_income <= level:
            cum_tax = taxable_income * rate - deduction
            break
    if cum_tax is None:
        raise ValueError('您赚的太多了')
    
    tax = cum_tax - early_cum_tax

    return tax

def cal_monthly_income(salarys: list, bonuses: list, insurance_list: list, provient_list: list):
    """计算年度的实际到手工资（按年度计算是因为个税按照年度计算）

    Args:
        salarys (list): 12个月的工资（单位全部为元）
        bonuses (list): 12个月的奖金
        insurance_list (list): [社保缴纳基数，养老保险（缴纳比例），医疗保险，失业保险，生育保险，工伤保险]
        provient_list (list): [公积金缴纳基数，缴纳比例]

    Returns:
        _type_: _description_
    """
    
    bonuses = bonuses if bonuses is not None else [0, ] * 12
    assert len(salarys) == len(bonuses) == 12, '工资或奖金数量不为12个月'
    insurance_base = [insurance_list[0], ] * 12 if insurance_list[0] is not None else salarys
    provient_base = [provient_list[0], ] * 12 if provient_list[0] is not None else salarys
    
    df = pd.DataFrame(index=range(1, 13), columns=['salary', 'bonus', 'pension', 'medical', 'unemployment', 'birth', 'injury', 
                                                   'provient', 'insurance', 'tax', 'actual_income'])

    df['salary'] = salarys
    df['bonus'] = bonuses

    df['pension'] = np.array(insurance_base) * insurance_list[1]
    df['medical'] = np.array(insurance_base) * insurance_list[2]
    df['unemployment'] = np.array(insurance_base) * insurance_list[3]
    df['birth'] = np.array(insurance_base) * insurance_list[4]
    df['injury'] = np.array(insurance_base) * insurance_list[5]
    df['provient'] = np.array(provient_base) * provient_list[1]

    df['insurance'] = df.loc[:, 'pension': 'provient'].sum(axis=1)

    for i in range(1, 13):
        tax = cal_monthly_tax(
            month=i, 
            cum_income=df.loc[:i, ['salary', 'bonus']].sum().sum(), 
            cum_insurance=df.loc[:i, 'insurance'].sum(), 
            early_cum_tax=df.loc[:i, 'tax'].sum(), 
            cum_deductions=0)
        
        df.loc[i, 'tax'] = tax
    
    df['actual_income'] = df['salary'] + df['bonus'] - df['insurance'] - df['tax']

    return df
     

def cal_monthly_spend(spend_df):
    spend_value = spend_df.applymap(lambda x: x.get())
    spend_value = spend_value[(spend_value['amount'] != 0) & (spend_value['item'] != '')]

    spend_value['freq_nb'] = spend_value['freq'].map({'日': 365, '周': 52, '月': 12, '季': 4, '年': 1})
    spend_value['annual_outcome'] = spend_value['amount'] * spend_value['freq_nb']
    monthly_outcome = pd.DataFrame(index=range(1, 13))
    for idx in spend_value.index:
        monthly_outcome.loc[:, spend_value.loc[idx, 'item']] = np.ones(12) * spend_value.loc[idx, 'annual_outcome'] / 12
        
    return spend_value, monthly_outcome
      


if __name__ == '__main__':
    cal_monthly_income(salarys=[18000]*12, insurance_list=[18000, 0.08, 0.02, 0.005, 0, 0], provient_list=[18000, 0.07])

    pass


