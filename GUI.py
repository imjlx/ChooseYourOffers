import tkinter as tk
from tkinter import ttk, messagebox

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import pickle
import os
import shutil

import income


class GUI(tk.Tk):
    def __init__(self):
        super().__init__()

        user_name = os.getenv('USERNAME')
        self.base_folder = f"C:/Users/{user_name}/Documents/offer_calculator"

        self.title("offer选择计算器")
        self.geometry("900x800+600-1750")

        self.label = tk.Label(self, text="offer选择计算器", font=("楷体", 20))
        self.label.pack()

        self.create_menu()

        self.main_frame = tk.Frame(self)
        self.main_frame.pack(fill=tk.BOTH, padx=10, pady=10)

        self.create_basic_frame()
        self.create_offer_frame()
    
    # 创建一个菜单
    def create_menu(self):
        menu = tk.Menu(self)
        self.config(menu=menu)

        # 文件菜单
        file_menu = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label="文件", menu=file_menu)
        file_menu.add_command(label="打开", command=None)
        file_menu.add_command(label="保存", command=None)
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=None)

        # 编辑菜单
        edit_menu = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label="编辑", menu=edit_menu)
        edit_menu.add_command(label="新建offer", command=self.pop_offer_frame)

        open_work_menu = tk.Menu(edit_menu, tearoff=0)
        edit_menu.add_cascade(label="打开offer", menu=open_work_menu)
        for offer in os.listdir(self.base_folder):
            open_work_menu.add_command(label=offer, command=lambda name=offer: self.pop_offer_frame(offer_name=name))
        edit_menu.entryconfig("打开offer", state="normal")
        edit_menu.bind("<Enter>", lambda event: open_work_menu.post(event.x_root, event.y_root))

        def delete_offer(offer_name):
            # 删除文件夹
            offer_folder = os.path.join(self.base_folder, offer_name)
            # 弹窗询问是否删除
            if messagebox.askokcancel("删除offer", f"是否删除offer：{offer_name}"):
                shutil.rmtree(offer_folder)
                self.create_menu()            
        delete_work_menu = tk.Menu(edit_menu, tearoff=0)
        edit_menu.add_cascade(label="删除offer", menu=delete_work_menu)
        for offer in os.listdir(self.base_folder):
            delete_work_menu.add_command(label=offer, command=lambda name=offer: delete_offer(offer_name=name))
        edit_menu.entryconfig("删除offer", state="normal")
        edit_menu.bind("<Enter>", lambda event: delete_work_menu.post(event.x_root, event.y_root))
        
    def create_basic_frame(self):
        self.basic_frame = tk.Frame(self.main_frame)
        self.basic_frame.pack(fill=tk.Y, side=tk.LEFT, padx=10, pady=10)
        bias_value = {
            "insurance": {"养老保险": 0, "医疗保险": 7, "失业保险": 0, "生育保险": 0, "工伤保险": 0, "公积金": 8}, 
            }
        bias = {}

        tk.Label(self.basic_frame, text="基本信息", anchor='center', font=("楷体", 15)).pack()
        insurance_frame = tk.Frame(self.basic_frame)
        insurance_frame.pack(fill=tk.X, side=tk.TOP, padx=10, pady=10)
        for i, (key, value) in enumerate(bias_value["insurance"].items()):
            bias[key] = tk.IntVar(value=value)
            tk.Label(insurance_frame, text=key, font=("宋体", 12)).grid(row=i, column=0)
            tk.Scale(insurance_frame, from_=0, to=10, variable=bias[key], orient=tk.HORIZONTAL, length=100).grid(row=i, column=1)
    
    def pop_offer_frame(self, offer_name=None):
        def offer_info_to_value(offer_info: dict):
            return {key: {k: v.get() for k, v in value.items()} for key, value in offer_info.items()}
        
        # 弹出offer信息输入框
        offer_frame = tk.Toplevel(self)
        offer_frame.title("offer信息")
        offer_frame.geometry("900x600+600-1750")
        # 读取可能存在的offer相关信息
        spend_df = pd.DataFrame(columns=['item', 'amount', 'freq'])
        if offer_name is None:
            print("新建offer")
            offer_info = {}
            spend_value = None
        else:
            print("打开offer：", offer_name)
            try:
                with open(os.path.join(self.base_folder, offer_name, "offer_info.pickle"), 'rb') as f:
                    offer_info = pickle.load(f)
            except FileNotFoundError:
                print(os.path.join(self.base_folder, offer_name, "offer_info.pickle"), "not found")
                offer_info = {}
            try:
                spend_value = pd.read_csv(os.path.join(self.base_folder, offer_name, "spend.csv"))
            except FileNotFoundError:
                spend_value = None

        def add_salary_frame(base_frame):
            salary_frame = tk.Frame(base_frame)
            salary_frame.pack(fill=tk.Y, side=tk.LEFT, padx=10, pady=10)

            basic_frame = tk.Frame(salary_frame)
            basic_frame.pack(fill=tk.X, side=tk.TOP, padx=10, pady=10)
            tk.Label(basic_frame, text="基本信息", anchor='center').grid(row=0, column=0, columnspan=2)
            keys = ["公司", "城市"]
            values = [tk.StringVar(value=offer_info.get("basic", {}).get(key, "")) for key in keys]
            for i in range(len(keys)):
                tk.Label(basic_frame, text=keys[i]).grid(row=i+1, column=0)
                tk.Entry(basic_frame, textvariable=values[i], width=10).grid(row=i+1, column=1, padx=10, pady=5)
            offer_info["basic"] = {keys[i]: values[i] for i in range(len(keys))}

            temp_frame = tk.Frame(salary_frame)
            temp_frame.pack(fill=tk.X, side=tk.TOP, padx=10, pady=10)
            tk.Label(temp_frame, text="薪资结构", anchor='center').grid(row=0, column=0, columnspan=3)
            keys = ["月薪", "月奖金", "季度奖金", "年终奖"]
            values = [tk.DoubleVar(value=offer_info.get("salary", {}).get(key, 0)) for key in keys]
            for i in range(len(keys)):
                tk.Label(temp_frame, text=keys[i]).grid(row=i+1, column=0)
                tk.Entry(temp_frame, textvariable=values[i], width=5).grid(row=i+1, column=1, padx=10, pady=5)
                tk.Label(temp_frame, text="千元").grid(row=i+1, column=2)
            offer_info["salary"] = {keys[i]: values[i] for i in range(len(keys))}

        def add_insurance_frame(base_frame):
            insurance_frame = tk.Frame(base_frame)
            insurance_frame.pack(fill=tk.Y, side=tk.LEFT, padx=10, pady=10)
            tk.Label(insurance_frame, text="五险一金", anchor='center').grid(row=0, column=0, columnspan=3)

            keys = ["社保缴纳基数", "养老保险", "医疗保险", "失业保险", "生育保险", "工伤保险", "公积金缴纳基数", "公积金"]
            insurance_default = [4, 8, 2, 0.5, 0, 0, 4, 12]
            values = [tk.DoubleVar(value=offer_info.get("insurance", {}).get(key, v_d)) for key, v_d in zip(keys, insurance_default)]
            unit_list = ["千元", "%", "%", "%", "%", "%", "千元", "%"]
            for i in range(len(keys)):
                tk.Label(insurance_frame, text=keys[i]).grid(row=i+1, column=0)
                tk.Entry(insurance_frame, textvariable=values[i], width=5).grid(row=i+1, column=1, padx=10, pady=5)
                tk.Label(insurance_frame, text=unit_list[i]).grid(row=i+1, column=2)
            offer_info["insurance"] = {keys[i]: values[i] for i in range(len(keys))}

        def cal_income():
            # 清空result_frame
            for widget in result_frame.winfo_children():
                widget.destroy()

            incomes = [var.get() for var in offer_info["salary"].values()]
            salarys = [incomes[0] * 1000, ] * 12
            monthly_bonuses = [incomes[1] * 1000, ] * 12
            quarterly_bonuses = [0, 0, incomes[2] * 1000, ] * 4
            annual_bonuses = [0, ] * 11 + [incomes[3] * 1000]
            bonuses = [monthly_bonuses[i] + quarterly_bonuses[i] + annual_bonuses[i] for i in range(12)]
            
            ins_pro = [var.get() for var in offer_info["insurance"].values()]
            insurance_list = [var / 100 for var in ins_pro[:-2]]
            insurance_list[0] = insurance_list[0] * 1000 * 100
            provient_list = [ins_pro[-2] * 1000, ins_pro[-1] / 100]
            
            df = income.cal_monthly_income(salarys, bonuses, insurance_list, provient_list)
            print(df)
            # 显示结果
            total_raw_income = round(df['salary'].sum() / 10000 + df['bonus'].sum() / 10000, 2)
            total_income = round(df['actual_income'].sum() / 10000, 2)
            total_tax = round(df['tax'].sum() / 10000, 2)

            tk.Label(result_frame, text="年到手总包（税前占比）:").pack()
            tk.Label(result_frame, text=f"{total_income}万元（{total_income/total_raw_income: .2%}）").pack(pady=10)
            tk.Label(result_frame, text="年缴纳个税（税前占比）:").pack()
            tk.Label(result_frame, text=f"{total_tax}万元（{total_tax/total_raw_income: .2%}）").pack(pady=10)

            # 保存文件
            offer_name = offer_info["basic"]["公司"].get()
            offer_name = offer_name if offer_name != '' else "default_offer"
            offer_folder = os.path.join(self.base_folder, offer_name)
            os.makedirs(offer_folder, exist_ok=True)
            # 保存年度收入
            df.to_csv(os.path.join(offer_folder, "monthly_income.csv"), index=False)
            # 保存offer_info
            with open(os.path.join(offer_folder, "offer_info.pickle"), 'wb') as f:
                pickle.dump(offer_info_to_value(offer_info), f)

        # 收入、五险一金大框架 INCOME_FRAME
        income_frame = tk.Frame(offer_frame, bd=2, relief='groove')
        income_frame.pack(fill=tk.Y, side=tk.LEFT, padx=10, pady=10)
        # 输入框架
        input_frame = tk.Frame(income_frame)
        input_frame.pack(fill=tk.X, side=tk.TOP, padx=10, pady=10)
        add_salary_frame(input_frame)
        add_insurance_frame(input_frame)
        # 按钮框架
        ttk.Separator(income_frame, orient='horizontal', style='Dashed.TSeparator').pack(fill='x', padx=20, pady=5)
        button_frame = tk.Frame(income_frame)
        button_frame.pack(fill=tk.X, side=tk.TOP, padx=10, pady=10)
        tk.Button(button_frame, text="保存并计算", command=cal_income).grid(row=0, column=1, pady=10)
        # 结果框架
        result_frame = tk.Frame(income_frame)
        result_frame.pack(fill=tk.X, padx=10, pady=10)
        
        def add_spend_frame(base_frame):
            def add_spend(item=None, amount=None, freq="月"):
                # 添加一行用户输入的
                i = len(spend_df)
                item = tk.StringVar(value=item); amount = tk.DoubleVar(value=amount); freq = tk.StringVar(value=freq)
                tk.Entry(sheet_frame, textvariable=item, width=10).grid(row=i, column=0, padx=10, pady=5)
                tk.Entry(sheet_frame, textvariable=amount, width=10).grid(row=i, column=1, padx=10, pady=5)
                ttk.OptionMenu(sheet_frame, freq, freq.get(), "日", "周", "月", "季", "年").grid(row=i, column=2, padx=10, pady=5)
                spend_df.loc[i] = [item, amount, freq]

            spend_frame = tk.Frame(base_frame)
            spend_frame.pack(fill=tk.Y, side=tk.LEFT, padx=10, pady=10)

            tk.Label(spend_frame, text="支出", anchor='center').grid(row=0, column=0, columnspan=3)
            tk.Label(spend_frame, text="项目").grid(row=1, column=0, padx=10, pady=5)
            tk.Label(spend_frame, text="金额（元）").grid(row=1, column=1, padx=10, pady=5)
            tk.Label(spend_frame, text="频率").grid(row=1, column=2, padx=10, pady=5)

            sheet_frame = tk.Frame(spend_frame)
            sheet_frame.grid(row=2, column=0, columnspan=3, pady=10)

            # 添加已有的支出
            if spend_value is not None:
                for i in range(len(spend_value)):
                    add_spend(spend_value.loc[i, 'item'], spend_value.loc[i, 'amount'], spend_value.loc[i, 'freq'])

            tk.Button(spend_frame, text="添加", command=add_spend).grid(row=3, column=0, columnspan=1, pady=10)
        
        def cal_outcome():
            spend_value, monthly_outcome = income.cal_monthly_spend(spend_df)
            print(spend_value)
            print(monthly_outcome)

            # 保存文件
            offer_name = offer_info["basic"]["公司"].get()
            offer_name = offer_name if offer_name != '' else "default_offer"
            offer_folder = os.path.join(self.base_folder, offer_name)
            os.makedirs(offer_folder, exist_ok=True)
            # 保存支出项目输入
            spend_value.to_csv(os.path.join(offer_folder, "spend.csv"), index=False)
            # 保存月度支出
            monthly_outcome.to_csv(os.path.join(offer_folder, "monthly_outcome.csv"), index=False)

        # 支出大框架 OUTCOME_FRAME
        outcome_frame = tk.Frame(offer_frame, bd=2, relief='groove')
        outcome_frame.pack(fill=tk.Y, side=tk.LEFT, padx=10, pady=10)
        # 输入框架
        input_frame = tk.Frame(outcome_frame)
        input_frame.pack(fill=tk.X, side=tk.TOP, padx=10, pady=10)
        add_spend_frame(input_frame)
        # 按钮框架
        ttk.Separator(outcome_frame, orient='horizontal', style='Dashed.TSeparator').pack(fill='x', padx=20, pady=5)
        button_frame = tk.Frame(outcome_frame)
        button_frame.pack(fill=tk.X, side=tk.TOP, padx=10, pady=10)
        tk.Button(button_frame, text="保存并计算", command=cal_outcome).grid(row=0, column=0, pady=10)

        # 保存按钮
        def save_offer():
            self.create_menu()
            offer_frame.destroy()

        tk.Button(offer_frame, text="保存offer", command=save_offer).pack(pady=10)

    def create_offer_frame(self):
        def compare():
            for widget in compare_frame.winfo_children():
                widget.destroy()

            col_names = ['     ', "税前", "到手", '养老', '医疗', '公积金']
            for i, col in enumerate(col_names):
                tk.Label(compare_frame, text=col, anchor='center', font=("楷体", 15)
                         ).grid(row=0, column=i, padx=5, pady=10)

            for i, offer in enumerate([offer for offer, var in show_offers.items() if var.get()]):
                income = pd.read_csv(os.path.join(self.base_folder, offer, "monthly_income.csv"))
                vals = [
                    offer, 
                    round(income['salary'].sum() / 10000 + income['bonus'].sum() / 10000, 2),
                    round(income['actual_income'].sum() / 10000, 2),
                    round(income['pension'].sum() / 10000, 2),
                    round(income['medical'].sum() / 10000, 2),
                    round(income['provient'].sum() / 10000, 2)
                    ]
                    
                for j, val in enumerate(vals):
                    tk.Label(compare_frame, text=val, anchor='center', font=("楷体", 15)
                            ).grid(row=i+1, column=j, padx=2, pady=10)

        self.offer_frame = tk.Frame(self.main_frame)
        self.offer_frame.pack(fill=tk.Y, side=tk.LEFT, padx=10, pady=10)
        
        tk.Label(self.offer_frame, text="Offer比较", anchor='center', font=("楷体", 15)).pack()
        choice_frame = tk.Frame(self.offer_frame)
        choice_frame.pack(fill=tk.X, side=tk.TOP, padx=10, pady=10)
        tk.Label(choice_frame, text="选择要比较的offer: ", anchor='center', font=("楷体", 15)).pack(side=tk.LEFT)
        # 读取可能存在的offer相关信息，用复选框显示
        show_offers = {}
        for offer in os.listdir(self.base_folder):
            if os.path.isdir(os.path.join(self.base_folder, offer)):
                show_offers[offer] = tk.IntVar()

        for offer, var in show_offers.items():
            tk.Checkbutton(choice_frame, text=offer, variable=var, command=compare).pack(side=tk.LEFT)
        
        compare_frame = tk.Frame(self.offer_frame, bd=2, relief='groove')
        compare_frame.pack(fill=tk.BOTH, padx=10, pady=10, expand=True)
        compare()

    @staticmethod
    def plot_raw_income_ratio(income_df):
        # 画饼图
        annual_income = income_df['actual_income'].sum()
        plt.pie(annual_income, labels=income_df.index, autopct='%1.1f%%')



if __name__ == "__main__":
    app = GUI()
    app.mainloop()