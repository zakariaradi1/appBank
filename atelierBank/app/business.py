from dall import *
import matplotlib.pyplot as plt

def plot_accounts_by_type(count_accounts_by_type, save_dir="."):
    try:
        if not count_accounts_by_type:
            print("No data to plot for accounts by type")
            return

        account_types = [row[0] for row in count_accounts_by_type]
        account_counts = [row[1] for row in count_accounts_by_type]

        plt.figure(figsize=(12, 8))
        plt.bar(account_types, account_counts, color='blue')
        plt.xlabel('Account Type')
        plt.ylabel('Number of Accounts')
        plt.title('Number of Accounts by Type')
        plt.tight_layout()

        save_path = f"{save_dir}/Accounts_by_type.png"
        plt.savefig(save_path)
        plt.close()

        return save_path

    except Exception as e:
        print(f"Error plotting accounts by type: {e}")
        return None


def plot_balances_by_type(count_accounts_by_balance, save_dir="."):
    try:
        if not count_accounts_by_balance:
            print("No data to plot for balances by range")
            return

        balance_ranges = [row[0] for row in count_accounts_by_balance]
        account_counts = [row[1] for row in count_accounts_by_balance]

        plt.figure(figsize=(12, 8))
        plt.bar(balance_ranges, account_counts, color='green')
        plt.xlabel('Balance Range')
        plt.ylabel('Number of Accounts')
        plt.title('Number of Accounts by Balance Range')
        plt.tight_layout()

        save_path = f"{save_dir}/Balances_by_type.png"
        plt.savefig(save_path)
        plt.close()

        return save_path

    except Exception as e:
        print(f"Error plotting balances by type: {e}")
        return None


""" if __name__ == "__main__":
    dao = AdminDao()

    # Plot accounts by type
    accounts_by_type = dao.count_Accounts_by_type()
    plot_accounts_by_type(accounts_by_type)

    # Plot balances by type
    balances_by_type = dao.count_Accounts_by_balance()
    plot_balances_by_type(balances_by_type) """
