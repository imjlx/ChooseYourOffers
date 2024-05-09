
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def plot_raw_income_ratio(income_df):
    # 画饼图
    sns.set(style="whitegrid", font='SimSun')
    annual_income = income_df.sum()
    annual_income['insurance'] = annual_income['pension'] + annual_income['medical'] + annual_income['unemployment'] + annual_income['birth'] + annual_income['injury']
    labels = {
        "actual_income": "实际到手工资",
        "tax": "个税",
        "insurance": "社保",
        "provient": "公积金"
    }
    plt.pie(annual_income[labels.keys()].values, labels=labels.values(), explode=(0.1, 0, 0, 0),
            autopct='%1.1f%%')
    plt.title('税前收入分布', fontsize=15)
    plt.plot()


df = pd.read_csv(r"C:\Users\JHR\Documents\offer_calculator\拼多多\monthly_income.csv")
plot_raw_income_ratio(df)