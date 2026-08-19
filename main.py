from services import (
    add_transaction,
    get_all_transactions,
    update_transaction,
    get_transaction_by_id,
    delete_transaction
)

from models import Transaction


def show_menu():
    """
    显示菜单
    """

    print("""
============================
 Personal Finance System
============================

1. 添加账单
2. 查看账单
3. 修改账单
4. 删除账单
5. 查询账单
6. 收支统计
0. 退出

============================
""")


def main():

    while True:

        show_menu()

        choice = input("请选择功能：")

        if choice == "1":
            print("添加账单")

        elif choice == "2":
            print("查看账单")

        elif choice == "3":
            print("修改账单")

        elif choice == "4":
            print("删除账单")

        elif choice == "5":
            print("查询账单")

        elif choice == "6":
            print("收支统计")

        elif choice == "0":
            print("退出系统")
            break

        else:
            print("无效输入，请重新选择")


if __name__ == "__main__":
    main()