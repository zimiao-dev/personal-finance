from services import (
    add_transaction,
    get_all_transactions,
    update_transaction,
    get_transaction_by_id,
    delete_transaction,
    query_transactions
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


def add_bill() -> int:

    amount = float(
        input("请输入账单金额：")
    )

    transaction_type = input(
        "请输入账单类型(income/expense)："
    )

    category = input(
        "请输入账单分类："
    )

    transaction_date = input(
        "请输入账单日期(yyyy-mm-dd)："
    )

    description = input(
        "请输入账单描述："
    )


    transaction = Transaction(
        id = None,
        amount=amount,
        type=transaction_type,
        category=category,
        transaction_date=transaction_date,
        description=description
    )


    transaction_id = add_transaction(transaction)

    return transaction_id


def list_bill():

    transactions = get_all_transactions()

    if not transactions:
        print("暂无账单记录")
        return


    print("全部历史账单如下：")

    for t in transactions:
        print(t)


def update_bill():

    tr_id = int(
        input("请输入需要修改的账单ID: ")
    )


    old_transaction = get_transaction_by_id(tr_id)


    if not old_transaction:
        print("账单记录不存在！")
        return


    print("当前账单:")
    print(old_transaction)


    confirm = input(
        "是否确认修改(y/n): "
    )


    if confirm.lower() != "y":
        print("取消修改")
        return


    amount = float(
        input("请输入账单金额：")
    )

    transaction_type = input(
        "请输入账单类型(income/expense)："
    )

    category = input(
        "请输入账单分类："
    )

    transaction_date = input(
        "请输入账单日期(yyyy-mm-dd)："
    )

    description = input(
        "请输入账单描述："
    )


    transaction = Transaction(
        id=tr_id,
        amount=amount,
        type=transaction_type,
        category=category,
        transaction_date=transaction_date,
        description=description
    )


    result = update_transaction(transaction)


    if result:
        print("修改成功")
    else:
        print("修改失败")


def delete_bill():

    tr_id = int(
        input("请输入要删除的账单ID：")
    )


    transaction = get_transaction_by_id(tr_id)


    if not transaction:
        print("账单不存在！")
        return


    print("当前账单:")
    print(transaction)


    confirm = input(
        "是否确认删除(y/n): "
    )


    if confirm.lower() != "y":
        print("取消删除")
        return


    result = delete_transaction(tr_id)


    if result:
        print("删除成功！")
    else:
        print("删除失败！")


def query_bill():

    category = None
    start_date = None
    end_date = None

    print("""
    a. 按分类查询
    b. 按日期范围查询
    c. 分类+日期查询
    """)

    choice = input("请选择查询方式：")


    if choice == "a":

        category = input("请输入类别：")


    elif choice == "b":

        start_date = input("请输入开始日期：")
        end_date = input("请输入结束日期：")


    elif choice == "c":

        category = input("请输入类别：")
        start_date = input("请输入开始日期：")
        end_date = input("请输入结束日期：")


    else:
        print("输入错误")
        return


    transactions = query_transactions(
        category=category,
        start_date=start_date,
        end_date=end_date
    )


    if not transactions:
        print("没有符合条件的账单记录！")
        return


    print("查询结果如下：")

    for t in transactions:
        print(t)

    

def main():

    while True:

        show_menu()

        choice = input("请选择功能：")

        if choice == "1":
            result = add_bill()
            print(f"添加成功，账单ID：{result}")

        elif choice == "2":
            list_bill()

        elif choice == "3":
            update_bill()

        elif choice == "4":
            delete_bill()

        elif choice == "5":
            query_bill()

        elif choice == "6":
            print("收支统计")

        elif choice == "0":
            print("退出系统")
            break

        else:
            print("无效输入，请重新选择")


if __name__ == "__main__":
    main()