import tkinter as tk
from tkinter import ttk

import pandas as pd
import os

import tax


class GUI(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("offer选择计算器")
        self.geometry("900x800+600-1750")

        self.label = tk.Label(self, text="offer选择计算器")
        self.label.pack()

        self.create_menu()

        self.main_frame = tk.Frame(self)
        self.main_frame.pack(fill=tk.BOTH, padx=10, pady=10)

        self.create_basic_frame()

        user_name = os.getenv('USERNAME')
        self.base_folder = f"C:/Users/{user_name}/Documents/offer_calculator"
    
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
        edit_menu.add_command(label="新建工作", command=self.add_offer)
        edit_menu.add_command(label="删除工作", command=None)

    def create_basic_frame(self):
        self.basic_frame = tk.Frame(self.main_frame)
        self.basic_frame.pack(fill=tk.Y, side=tk.LEFT, padx=10, pady=10)

        tk.Label(self.basic_frame, text="基本信息", anchor='center').pack()
    
    def add_offer(self):
        def add_salary_frame(base_frame):
            salary_frame = tk.Frame(base_frame)
            salary_frame.pack(fill=tk.Y, side=tk.LEFT, padx=10, pady=10)

            basic_frame = tk.Frame(salary_frame)
            basic_frame.pack(fill=tk.X, side=tk.TOP, padx=10, pady=10)
            tk.Label(basic_frame, text="基本信息", anchor='center').grid(row=0, column=0, columnspan=2)
            keys = ["公司", "城市"]
            values = [tk.StringVar() for _ in range(len(keys))]
            for i in range(len(keys)):
                tk.Label(basic_frame, text=keys[i]).grid(row=i+1, column=0)
                tk.Entry(basic_frame, textvariable=values[i], width=10).grid(row=i+1, column=1, padx=10, pady=5)
            offer_info["basic"] = {keys[i]: values[i] for i in range(len(keys))}

            temp_frame = tk.Frame(salary_frame)
            temp_frame.pack(fill=tk.X, side=tk.TOP, padx=10, pady=10)
            tk.Label(temp_frame, text="薪资结构", anchor='center').grid(row=0, column=0, columnspan=3)
            keys = ["月薪", "月奖金", "季度奖金", "年终奖"]
            values = [tk.DoubleVar() for _ in range(4)]
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
            values = [tk.DoubleVar(value=value) for value in insurance_default]
            unit_list = ["千元", "%", "%", "%", "%", "%", "千元", "%"]
            for i in range(len(keys)):
                tk.Label(insurance_frame, text=keys[i]).grid(row=i+1, column=0)
                tk.Entry(insurance_frame, textvariable=values[i], width=5).grid(row=i+1, column=1, padx=10, pady=5)
                tk.Label(insurance_frame, text=unit_list[i]).grid(row=i+1, column=2)
            offer_info["insurance"] = {keys[i]: values[i] for i in range(len(keys))}

        def print_dict():
            for key, value in offer_info.items():
                print(key, value)

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
            
            df = tax.cal_annual_tax(salarys, bonuses, insurance_list, provient_list)
            print(df)
            # 随时刷新
            total_raw_income = round(df['salary'].sum() / 10000 + df['bonus'].sum() / 10000, 2)
            total_income = round(df['actual_income'].sum() / 10000, 2)
            total_tax = round(df['tax'].sum() / 10000, 2)

            tk.Label(result_frame, text="年到手总包（税前占比）:").pack()
            tk.Label(result_frame, text=f"{total_income}万元（{total_income/total_raw_income: .2%}）").pack(pady=10)
            tk.Label(result_frame, text="年缴纳个税（税前占比）:").pack()
            tk.Label(result_frame, text=f"{total_tax}万元（{total_tax/total_raw_income: .2%}）").pack(pady=10)

            return df

        def add_spend_frame(base_frame):
            def add_spend():
                # 添加一行用户输入的
                i = len(spend_df)
                item = tk.StringVar(); amount = tk.DoubleVar(); freq = tk.StringVar(value="周")
                tk.Entry(sheet_frame, textvariable=item, width=10).grid(row=i, column=0, padx=10, pady=5)
                tk.Entry(sheet_frame, textvariable=amount, width=10).grid(row=i, column=1, padx=10, pady=5)
                ttk.OptionMenu(sheet_frame, freq, "日", "周", "季", "月", "年").grid(row=i, column=2, padx=10, pady=5)
                spend_df.loc[i] = [item, amount, freq]

            spend_frame = tk.Frame(base_frame)
            spend_frame.pack(fill=tk.Y, side=tk.LEFT, padx=10, pady=10)
            spend_df = pd.DataFrame(columns=['item', 'amount', 'freq'])

            tk.Label(spend_frame, text="支出", anchor='center').grid(row=0, column=0, columnspan=3)
            tk.Label(spend_frame, text="项目").grid(row=1, column=0, padx=10, pady=5)
            tk.Label(spend_frame, text="金额（元）").grid(row=1, column=1, padx=10, pady=5)
            tk.Label(spend_frame, text="频率").grid(row=1, column=2, padx=10, pady=5)

            sheet_frame = tk.Frame(spend_frame)
            sheet_frame.grid(row=2, column=0, columnspan=3, pady=10)
            tk.Button(spend_frame, text="添加", command=add_spend).grid(row=3, column=0, columnspan=1, pady=10)
        

        # 弹出offer信息输入框
        offer_frame = tk.Toplevel(self)
        offer_frame.title("offer信息")
        offer_frame.geometry("900x600+600-1750")
        offer_info = {}

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
        tk.Button(button_frame, text="Print", command=print_dict).grid(row=0, column=0, pady=10)
        tk.Button(button_frame, text="计算", command=cal_income).grid(row=0, column=1, pady=10)
        # 结果框架
        result_frame = tk.Frame(income_frame)
        result_frame.pack(fill=tk.X, padx=10, pady=10)


        # 支出大框架 OUTCOME_FRAME
        outcome_frame = tk.Frame(offer_frame, bd=2, relief='groove')
        outcome_frame.pack(fill=tk.Y, side=tk.LEFT, padx=10, pady=10)
        # 输入框架
        input_frame = tk.Frame(outcome_frame)
        input_frame.pack(fill=tk.X, side=tk.TOP, padx=10, pady=10)
        add_spend_frame(input_frame)

        tk.Button(offer_frame, text="Print", command=print_dict).pack(pady=10)


    def create_salary_frame(self):
        input_width = 5
        self.salary_frame = tk.Frame(self.main_frame)
        self.salary_frame.pack(fill=tk.Y, side=tk.LEFT, padx=10, pady=10)
        
        # 计算按钮
        ttk.Separator(self.salary_frame, orient='horizontal', style='Dashed.TSeparator').pack(fill='x', padx=20, pady=5)
        tk.Button(self.salary_frame, text="计算", command=self.calculate_actual_salary).pack(pady=10)
        self.result_frame = tk.Frame(self.salary_frame)
        self.result_frame.pack(fill=tk.X, padx=10, pady=10)

    
    def print_spend(self):
        print(self.spend_df)
        spend_df = self.spend_df.applymap(lambda x: x.get())
        print(spend_df)



if __name__ == "__main__":
    app = GUI()
    app.mainloop()